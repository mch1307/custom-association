try:
    from odoo import models
except (ImportError, ModuleNotFoundError):
    class _StandaloneModel:
        pass

    class models:
        Model = _StandaloneModel


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @staticmethod
    def resolve_invoice_portal_url(order):
        invoice_ids = getattr(order, 'invoice_ids', False)
        if not invoice_ids:
            return False

        invoice = invoice_ids[0] if isinstance(invoice_ids, (list, tuple)) else invoice_ids
        if hasattr(invoice, 'get_portal_url'):
            return invoice.get_portal_url()
        return False

    def get_checkout_invoice_url(self):
        return self.resolve_invoice_portal_url(self)

    def get_checkout_invoice_status(self):
        invoice_ids = getattr(self, 'invoice_ids', False)
        if not invoice_ids:
            return 'none'
        return 'present'
