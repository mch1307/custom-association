try:
    from odoo import http
    from odoo.http import request
    from odoo.addons.website_sale.controllers.main import WebsiteSale
except (ImportError, ModuleNotFoundError):
    http = None
    request = None
    WebsiteSale = object


if http and getattr(http, 'route', None):
    class AssociationFamilyWebsiteSale(WebsiteSale):

        @staticmethod
        def normalize_int_ids(values):
            normalized = []
            for value in values or []:
                try:
                    normalized.append(int(value))
                except (TypeError, ValueError):
                    continue
            return normalized

        @staticmethod
        def filter_allowed_ids(candidate_ids, allowed_ids):
            allowed_set = set(allowed_ids or [])
            selected = []
            for member_id in candidate_ids:
                if member_id not in allowed_set:
                    continue
                if member_id in selected:
                    continue
                selected.append(member_id)
            return selected

        @staticmethod
        def is_event_line(line):
            has_event = line._fields.get('event_id') and line.event_id
            has_ticket = line._fields.get('event_ticket_id') and line.event_ticket_id
            return bool(has_event or has_ticket)

        def _get_household_member_ids_for_order(self, order):
            partner = order.partner_id
            if not partner:
                return []
            manager = partner.parent_id or partner
            return (manager | manager.child_ids).filtered(lambda p: p.active).ids

        @staticmethod
        def order_has_active_lines(order):
            lines = getattr(order, 'order_line', None) or []
            if not lines:
                return False
            for line in lines:
                qty = getattr(line, 'product_uom_qty', 0) or 0
                try:
                    qty = float(qty)
                except (TypeError, ValueError):
                    continue
                if qty > 0:
                    return True
            return False

        @classmethod
        def should_cleanup_empty_draft_order(cls, order):
            if not order:
                return False
            order_state = getattr(order, 'state', False)
            if order_state not in ('draft', 'sent'):
                return False
            if cls.order_has_active_lines(order):
                return False
            return True

        @classmethod
        def cleanup_empty_draft_order(cls, order):
            if not cls.should_cleanup_empty_draft_order(order):
                return False

            try:
                if hasattr(order, 'sudo'):
                    order = order.sudo()
                if hasattr(order, 'unlink'):
                    order.unlink()
                elif hasattr(order, 'action_cancel'):
                    order.action_cancel()
                return True
            except Exception:
                return False

        @http.route('/association_family/cart/line_participants', type='json', auth='public', website=True)
        def association_family_set_line_participants(self, line_id, participant_ids=None, **kwargs):
            if request.env.user._is_public():
                return {'ok': False, 'error': 'Authentication required'}

            order = request.website.sale_get_order()
            if self.should_cleanup_empty_draft_order(order):
                self.cleanup_empty_draft_order(order)
                return {'ok': False, 'error': 'Cart is empty'}
            if not order:
                return {'ok': False, 'error': 'No cart order'}

            try:
                line_id_int = int(line_id)
            except (TypeError, ValueError):
                return {'ok': False, 'error': 'Invalid order line id'}

            line = order.order_line.filtered(lambda l: l.id == line_id_int)[:1]
            if not line:
                return {'ok': False, 'error': 'Order line not found'}
            if not self.is_event_line(line):
                return {'ok': False, 'error': 'Order line is not an event line'}

            normalized_ids = self.normalize_int_ids(participant_ids)
            allowed_ids = self._get_household_member_ids_for_order(order)
            selected_ids = self.filter_allowed_ids(normalized_ids, allowed_ids)

            values = {'event_participant_ids': [(6, 0, selected_ids)]}
            if selected_ids and not line.member_id:
                values['member_id'] = selected_ids[0]

            line.sudo().write(values)
            return {
                'ok': True,
                'line_id': line.id,
                'participant_ids': selected_ids,
            }
