try:
    from odoo import api, models
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class api:
        @staticmethod
        def model_create_multi(func):
            return func

    class models:
        Model = _StandaloneModel


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._apply_household_participant_assignment()
        return records

    def write(self, vals):
        result = super().write(vals)
        if set(vals).intersection({'sale_order_line_id', 'partner_id'}):
            self._apply_household_participant_assignment()
        return result

    def _apply_household_participant_assignment(self):
        line_to_regs = {}
        for registration in self:
            line = getattr(registration, 'sale_order_line_id', False)
            if not line:
                continue
            line_to_regs.setdefault(line, self.env['event.registration'])
            line_to_regs[line] |= registration

        for line, new_regs in line_to_regs.items():
            self._assign_line_registrations_to_participants(line, new_regs)

    def _assign_line_registrations_to_participants(self, line, new_regs):
        participant_ids = line.event_participant_ids.ids if line.event_participant_ids else []
        default_member_id = line.member_id.id if line.member_id else False
        if not participant_ids and not default_member_id:
            return

        existing_ids = set(new_regs.ids)
        all_regs = line.event_registration_ids.sorted(lambda r: (r.create_date or r.id, r.id))
        if not all_regs:
            all_regs = new_regs.sorted(lambda r: (r.create_date or r.id, r.id))

        for index, reg in enumerate(all_regs):
            if reg.id not in existing_ids:
                continue
            partner_id = line.pick_event_participant_id(participant_ids, default_member_id, index)
            if partner_id and reg.partner_id.id != partner_id:
                reg.sudo().write({'partner_id': partner_id})
