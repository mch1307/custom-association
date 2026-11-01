try:
    from odoo import fields, models
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class fields:
        @staticmethod
        def Boolean(*args, **kwargs):
            return None

        @staticmethod
        def Selection(*args, **kwargs):
            return None

        @staticmethod
        def Integer(*args, **kwargs):
            return None

    class models:
        Model = _StandaloneModel


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    x_is_membership_product = fields.Boolean(
        string='Membership Product',
        help='When enabled, paid invoices for this product activate memberships.',
    )
    x_membership_scope = fields.Selection(
        [
            ('individual', 'Individual'),
            ('household', 'Household'),
        ],
        string='Membership Scope',
        default='individual',
    )
    x_membership_duration_months = fields.Integer(
        string='Membership Duration (Months)',
        default=12,
    )
