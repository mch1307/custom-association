try:
    from odoo import api, fields, models
    from odoo.exceptions import UserError
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class api:
        @staticmethod
        def depends(*args, **kwargs):
            def _wrap(func):
                return func
            return _wrap

    class fields:
        @staticmethod
        def Selection(*args, **kwargs):
            return None

        @staticmethod
        def Date(*args, **kwargs):
            return None

        @staticmethod
        def Many2one(*args, **kwargs):
            return None

        @staticmethod
        def Integer(*args, **kwargs):
            return None

        @staticmethod
        def Char(*args, **kwargs):
            return None

        @staticmethod
        def Text(*args, **kwargs):
            return None

    class models:
        Model = _StandaloneModel

    class UserError(Exception):
        pass


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_household_role = fields.Selection(
        [
            ('responsible', 'Responsable'),
            ('partner', 'Partenaire'),
            ('child', 'Enfant'),
            ('other', 'Autre'),
        ],
        string='Household Role',
        default='other',
    )
    x_membership_status = fields.Selection(
        [
            ('inactive', 'Inactif'),
            ('active', 'Actif'),
            ('expired', 'Expiré'),
            ('retired', 'Ancien'),
        ],
        string='Statut membre',
        default='inactive',
    )
    x_membership_end_date = fields.Date(string='Date fin adhésion')
    x_household_manager_id = fields.Many2one(
        'res.partner',
        string='Responsable du ménage',
        compute='_compute_household_manager_id',
        store=True,
    )
    x_household_size = fields.Integer(
        string='Taille du ménage',
        compute='_compute_household_size',
        store=False,
    )
    x_costume_size = fields.Selection(
        [
            ('XS', 'XS'),
            ('S', 'S'),
            ('M', 'M'),
            ('L', 'L'),
            ('XL', 'XL'),
            ('2XL', '2XL'),
            ('3XL', '3XL'),
            ('4XL', '4XL'),
        ],
        string='Taille du costume',
    )

    @staticmethod
    def compute_household_size_flags(active_flags):
        return 1 + sum(1 for flag in active_flags if flag)

    @api.depends('parent_id')
    def _compute_household_manager_id(self):
        for partner in self:
            partner.x_household_manager_id = partner.parent_id or partner

    @api.depends('parent_id', 'child_ids', 'child_ids.active')
    def _compute_household_size(self):
        for partner in self:
            manager = partner.parent_id or partner
            active_flags = [member.active for member in manager.child_ids]
            partner.x_household_size = self.compute_household_size_flags(active_flags)

    def _is_household_responsible(self):
        self.ensure_one()
        if self.parent_id:
            return False
        if not self.x_household_role:
            return True
        return self.x_household_role == 'responsible'

    def get_household_members(self, active_only=True):
        self.ensure_one()
        manager = self.parent_id or self
        members = manager | manager.child_ids
        if active_only:
            members = members.filtered(lambda p: p.active)
        return members

    def _has_member_history(self):
        self.ensure_one()
        if not hasattr(self, 'env'):
            return False

        sale_line_count = self.env['sale.order.line'].sudo().search_count([('member_id', '=', self.id)])
        if sale_line_count:
            return True

        invoice_line_count = self.env['account.move.line'].sudo().search_count([('partner_id', '=', self.id)])
        return bool(invoice_line_count)

    def unlink(self):
        for partner in self:
            if partner._has_member_history():
                raise UserError('This member has history and cannot be deleted. Archive it instead.')
        return super().unlink()
