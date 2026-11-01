from datetime import timedelta

try:
    from dateutil.relativedelta import relativedelta
except (ImportError, ModuleNotFoundError):
    relativedelta = None

try:
    from odoo import api, fields, models
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class api:
        @staticmethod
        def model(func):
            return func

    class fields:
        class Date:
            @staticmethod
            def context_today(_record):
                from datetime import date
                return date.today()

    class models:
        Model = _StandaloneModel


class AccountMove(models.Model):
    _inherit = 'account.move'

    @staticmethod
    def compute_membership_end_date(start_date, duration_months):
        months = max(1, int(duration_months or 12))
        if relativedelta:
            return start_date + relativedelta(months=months)
        return start_date + timedelta(days=months * 30)

    def write(self, vals):
        result = super().write(vals)
        if set(vals).intersection({'payment_state', 'state'}):
            self._apply_paid_membership_propagation()
        return result

    def _apply_paid_membership_propagation(self):
        for move in self:
            if move.move_type != 'out_invoice':
                continue
            if move.state != 'posted' or move.payment_state != 'paid':
                continue
            move._activate_memberships_for_paid_lines()

    def _activate_memberships_for_paid_lines(self):
        self.ensure_one()
        for line in self.invoice_line_ids:
            template = line.product_id.product_tmpl_id
            if not template.x_is_membership_product:
                continue

            beneficiaries = self._resolve_membership_beneficiaries(line, template.x_membership_scope)
            if not beneficiaries:
                continue

            date_start = self.invoice_date or fields.Date.context_today(self)
            date_end = self.compute_membership_end_date(date_start, template.x_membership_duration_months)
            beneficiaries.write(
                {
                    'x_membership_status': 'active',
                    'x_membership_end_date': date_end,
                }
            )

    def _resolve_membership_beneficiaries(self, invoice_line, scope):
        self.ensure_one()
        partner = self.partner_id
        manager = partner.parent_id or partner

        if scope == 'household':
            return (manager | manager.child_ids).filtered(lambda p: p.active)

        sale_lines = invoice_line.sale_line_ids.filtered(lambda sl: sl.member_id)
        if sale_lines:
            return sale_lines.mapped('member_id')
        return partner
