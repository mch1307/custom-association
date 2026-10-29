from odoo import api, models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    _BANK_TRANSFER_PROVIDER_IDS = {22}
    _BANK_TRANSFER_KEYWORDS = ('wire transfer', 'virement bancaire', 'bank transfer')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if records:
            records._maybe_auto_confirm_association_order()
        return records

    def write(self, vals):
        result = super().write(vals)
        if set(vals).intersection({'state', 'provider_id', 'amount', 'reference'}):
            self._maybe_auto_confirm_association_order()
        return result

    def _maybe_auto_confirm_association_order(self):
        for transaction in self._iter_transactions():
            if not self._is_trigger_transaction(transaction):
                continue

            order = self._find_order_for_transaction(transaction)
            if not order or order.state in ('sale', 'done', 'cancel'):
                continue

            self._confirm_order(order)
            invoice = self._create_or_get_invoice(order)
            self._validate_invoice(invoice)
            self._send_invoice_to_customer(invoice)

    def _iter_transactions(self):
        if hasattr(self, 'ids'):
            return self
        return [self]

    def _is_trigger_transaction(self, transaction):
        if transaction.state != 'pending':
            return False
        if not transaction.amount or transaction.amount <= 0:
            return False
        if not transaction.provider_id:
            return False

        provider = transaction.provider_id
        provider_id = getattr(provider, 'id', False)
        provider_code = (getattr(provider, 'code', '') or '').lower()
        provider_name = (getattr(provider, 'name', '') or '').lower()
        provider_text = f'{provider_code} {provider_name}'

        if provider_id and provider_id not in self._BANK_TRANSFER_PROVIDER_IDS:
            return False
        if provider_code and provider_code not in ('custom', 'bank_transfer'):
            return False
        if not any(keyword in provider_text for keyword in self._BANK_TRANSFER_KEYWORDS):
            return False

        return True

    def _find_order_for_transaction(self, transaction):
        if hasattr(transaction, 'sale_order_ids') and transaction.sale_order_ids:
            return transaction.sale_order_ids[0]

        reference = (getattr(transaction, 'reference', '') or '').strip()
        if not reference:
            return False

        if not hasattr(self, 'env'):
            return False

        SaleOrder = self.env['sale.order']
        for field_name in ('name', 'reference'):
            order = SaleOrder.search([(field_name, '=', reference)], limit=1)
            if order:
                return order
        return False

    def _confirm_order(self, order):
        if order.state in ('draft', 'sent'):
            order.with_context(skip_mail=True).action_confirm()
            order.message_post(body='Commande confirmée automatiquement.')

    def _create_or_get_invoice(self, order):
        invoice = order.invoice_ids[:1] if order.invoice_ids else False
        if invoice:
            return invoice[0] if isinstance(invoice, list) else invoice

        if order.state in ('sale', 'done'):
            created = order._create_invoices()
            if created:
                invoice = created[:1]
                order.message_post(body='Facture créée automatiquement.')
                return invoice[0] if isinstance(invoice, list) else invoice
        return False

    def _validate_invoice(self, invoice):
        if invoice and hasattr(invoice, 'state') and invoice.state == 'draft':
            invoice.action_post()
            invoice.message_post(body='Facture validée automatiquement.')

    def _send_invoice_to_customer(self, invoice):
        if not invoice or not hasattr(self, 'env'):
            return
        if getattr(invoice, 'state', False) != 'posted':
            return
        if getattr(invoice, 'move_type', 'out_invoice') not in ('out_invoice', 'out_refund'):
            return
        if getattr(invoice, 'is_move_sent', False):
            return

        partner = getattr(invoice, 'partner_id', False)
        if not partner or not getattr(partner, 'email', False):
            return

        template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        if not template:
            return

        template.send_mail(
            invoice.id,
            force_send=True,
            raise_exception=False,
            email_values={'email_to': partner.email},
        )
        invoice.message_post(body='Facture envoyée automatiquement au client.')
