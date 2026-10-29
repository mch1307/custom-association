import importlib.util
import sys
import types
import unittest
from pathlib import Path


odoo_module = types.ModuleType('odoo')


class DummyModel:
    pass


odoo_module.api = types.SimpleNamespace(model_create_multi=lambda func: func)
odoo_module.fields = object()
odoo_module.models = types.SimpleNamespace(Model=DummyModel)
sys.modules.setdefault('odoo', odoo_module)

module_path = Path(__file__).resolve().parents[1] / 'models' / 'payment_transaction.py'
spec = importlib.util.spec_from_file_location('association_auto_confirm.payment_transaction', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PaymentTransaction = module.PaymentTransaction


class FakeInvoice:
    _sequence = 0

    def __init__(self, state='draft', move_type='out_invoice', partner=None, is_move_sent=False):
        FakeInvoice._sequence += 1
        self.id = FakeInvoice._sequence
        self.state = state
        self.move_type = move_type
        self.partner_id = partner or types.SimpleNamespace(email='client@example.com')
        self.is_move_sent = is_move_sent
        self.messages = []

    def action_post(self):
        self.state = 'posted'

    def message_post(self, body):
        self.messages.append(body)


class FakeOrder:
    def __init__(self, state='draft', website_id=True, origin='website_sale.order', invoice_ids=None):
        self.state = state
        self.website_id = website_id
        self.origin = origin
        self.invoice_ids = invoice_ids or []
        self.messages = []

    def with_context(self, **kwargs):
        return self

    def action_confirm(self):
        self.state = 'sale'

    def message_post(self, body):
        self.messages.append(body)

    def _create_invoices(self):
        invoice = FakeInvoice()
        self.invoice_ids = [invoice]
        return [invoice]


class FakeProvider:
    def __init__(self, code='bank_transfer', name='Bank Transfer'):
        self.code = code
        self.name = name


class FakeTemplate:
    def __init__(self):
        self.sent = []

    def send_mail(self, invoice_id, force_send=True, raise_exception=False, email_values=None):
        self.sent.append(
            {
                'invoice_id': invoice_id,
                'force_send': force_send,
                'raise_exception': raise_exception,
                'email_values': email_values or {},
            }
        )


class FakeEnv:
    def __init__(self, template=None):
        self.template = template

    def ref(self, xmlid, raise_if_not_found=False):
        if xmlid == 'account.email_template_edi_invoice':
            return self.template
        return None


class PaymentTransactionLogicTests(unittest.TestCase):

    def _build_transaction(self, *, state='pending', amount=100, order_state='draft', provider_code='bank_transfer', origin='website_sale.order', existing_invoice=None):
        order = FakeOrder(state=order_state, website_id=True, origin=origin, invoice_ids=[existing_invoice] if existing_invoice else [])
        transaction = PaymentTransaction.__new__(PaymentTransaction)
        transaction.state = state
        transaction.amount = amount
        transaction.sale_order_ids = [order]
        transaction.provider_id = FakeProvider(code=provider_code, name='Bank Transfer')
        transaction.mail_template = FakeTemplate()
        transaction.env = FakeEnv(template=transaction.mail_template)
        return transaction, order

    def test_pending_bank_transfer_web_order_confirms_and_invoices(self):
        transaction, order = self._build_transaction()

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(order.state, 'sale')
        self.assertTrue(any('Commande confirmée automatiquement.' in message for message in order.messages))
        self.assertEqual(len(order.invoice_ids), 1)
        self.assertEqual(order.invoice_ids[0].state, 'posted')
        self.assertTrue(any('Facture validée automatiquement.' in message for message in order.invoice_ids[0].messages))
        self.assertEqual(len(transaction.mail_template.sent), 1)
        self.assertEqual(transaction.mail_template.sent[0]['invoice_id'], order.invoice_ids[0].id)
        self.assertTrue(any('Facture envoyée automatiquement au client.' in message for message in order.invoice_ids[0].messages))

    def test_other_payment_provider_is_ignored(self):
        transaction, order = self._build_transaction(provider_code='stripe')

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.invoice_ids, [])

    def test_zero_amount_is_ignored(self):
        transaction, order = self._build_transaction(amount=0)

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.invoice_ids, [])

    def test_already_confirmed_order_is_ignored(self):
        transaction, order = self._build_transaction(order_state='sale')

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(order.state, 'sale')
        self.assertEqual(order.invoice_ids, [])

    def test_existing_invoice_is_validated(self):
        existing_invoice = FakeInvoice(state='draft')
        transaction, order = self._build_transaction(existing_invoice=existing_invoice)

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(existing_invoice.state, 'posted')
        self.assertTrue(any('Facture validée automatiquement.' in message for message in existing_invoice.messages))
        self.assertEqual(len(transaction.mail_template.sent), 1)

    def test_invoice_not_sent_when_partner_has_no_email(self):
        partner_without_email = types.SimpleNamespace(email=False)
        existing_invoice = FakeInvoice(state='draft', partner=partner_without_email)
        transaction, order = self._build_transaction(existing_invoice=existing_invoice)

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(existing_invoice.state, 'posted')
        self.assertEqual(len(transaction.mail_template.sent), 0)

    def test_invoice_not_sent_when_already_marked_sent(self):
        existing_invoice = FakeInvoice(state='draft', is_move_sent=True)
        transaction, order = self._build_transaction(existing_invoice=existing_invoice)

        transaction._maybe_auto_confirm_association_order()

        self.assertEqual(existing_invoice.state, 'posted')
        self.assertEqual(len(transaction.mail_template.sent), 0)


if __name__ == '__main__':
    unittest.main()
