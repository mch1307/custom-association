import sys
import types
from pathlib import Path
from types import SimpleNamespace


odoo = types.ModuleType('odoo')
odoo.models = types.SimpleNamespace(Model=type('Model', (), {}))
sys.modules.setdefault('odoo', odoo)

from association_checkout_ui.models.sale_order import SaleOrder


class DummyInvoice:
    def __init__(self, portal_url):
        self.portal_url = portal_url

    def get_portal_url(self):
        return self.portal_url


def test_resolve_invoice_portal_url_returns_url():
    order = SimpleNamespace(invoice_ids=[DummyInvoice('/my/invoices/123')])
    assert SaleOrder.resolve_invoice_portal_url(order) == '/my/invoices/123'


def test_resolve_invoice_portal_url_without_invoice_returns_false():
    order = SimpleNamespace(invoice_ids=[])
    assert SaleOrder.resolve_invoice_portal_url(order) is False


def test_get_checkout_invoice_status_without_invoice_is_none():
    order = SimpleNamespace(invoice_ids=[])
    assert SaleOrder.resolve_invoice_portal_url(order) is False


def test_checkout_template_uses_association_labels():
    js_path = Path(__file__).resolve().parents[1] / 'static' / 'src' / 'js' / 'checkout_labels.js'
    js = js_path.read_text(encoding='utf-8')
    assert 'Confirmer la commande' in js
    assert 'Confirmation' in js
    assert 'Payer maintenant' in js
    assert 'Paiement' in js
    assert 'Commander' in js
    assert "current === 'Payer'" in js
