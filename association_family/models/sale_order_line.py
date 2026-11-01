try:
    from odoo import api, fields, models
    from odoo.exceptions import ValidationError
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class api:
        @staticmethod
        def model_create_multi(func):
            return func

        @staticmethod
        def constrains(*args, **kwargs):
            def _wrap(func):
                return func
            return _wrap

    class fields:
        @staticmethod
        def Many2one(*args, **kwargs):
            return None

        @staticmethod
        def Many2many(*args, **kwargs):
            return None

            @staticmethod
            def Many2many(*args, **kwargs):
                return None

    class models:
        Model = _StandaloneModel

    class ValidationError(Exception):
        pass


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_partner_id = fields.Many2one(
        'res.partner',
        related='order_id.partner_id',
        string='Order Partner',
        store=True,
        readonly=True,
    )
    member_id = fields.Many2one(
        'res.partner',
        string='Beneficiary Member',
        domain="['|', ('id', '=', order_partner_id), ('parent_id', '=', order_partner_id)]",
        help='Household member receiving this product or service.',
    )
    event_participant_ids = fields.Many2many(
        'res.partner',
        string='Event Participants',
        relation='sale_order_line_event_participant_rel',
        column1='sale_order_line_id',
        column2='partner_id',
        domain="['|', ('id', '=', order_partner_id), ('parent_id', '=', order_partner_id)]",
        help='Household members selected as participants for event registrations.',
    )

    @staticmethod
    def is_member_allowed(order_partner_id, member_parent_id, member_id):
        return member_id == order_partner_id or member_parent_id == order_partner_id

    @staticmethod
    def pick_event_participant_id(participant_ids, default_member_id, sequence_index):
        if participant_ids:
            if sequence_index < len(participant_ids):
                return participant_ids[sequence_index]
            return participant_ids[-1]
        return default_member_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('member_id'):
                continue
            if vals.get('order_partner_id'):
                vals['member_id'] = vals['order_partner_id']
        return super().create(vals_list)

    @api.constrains('member_id', 'order_partner_id')
    def _check_member_belongs_to_household(self):
        for line in self:
            if not line.member_id or not line.order_partner_id:
                continue
            if not self.is_member_allowed(line.order_partner_id.id, line.member_id.parent_id.id, line.member_id.id):
                raise ValidationError('Beneficiary must belong to the household of the billed customer.')
