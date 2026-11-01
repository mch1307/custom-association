try:
    from odoo import http
    from odoo.http import request
except (ImportError, ModuleNotFoundError):
    http = None
    request = None


if http and request and getattr(http, 'Controller', None):
    class AssociationFamilyPortal(http.Controller):

        def _current_partner(self):
            return request.env.user.partner_id

        def _is_household_responsible(self, partner):
            if not partner or partner.parent_id:
                return False
            if not partner.x_household_role:
                return True
            return partner.x_household_role == 'responsible'

        def _get_household_members(self, manager):
            return (manager | manager.child_ids).sorted(lambda p: (p.parent_id.id or 0, p.name or ''))

        def _get_member_for_manager(self, manager, member_id):
            member = request.env['res.partner'].sudo().browse(member_id)
            if not member.exists():
                return request.env['res.partner']
            if member == manager or member.parent_id == manager:
                return member
            return request.env['res.partner']

        @http.route('/my/household', type='http', auth='user', website=True)
        def portal_my_household(self, **kwargs):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            values = {
                'page_name': 'household',
                'manager': partner,
                'members': self._get_household_members(partner),
            }
            return request.render('association_family.portal_my_household', values)

        @http.route('/my/household/new', type='http', auth='user', website=True, methods=['GET', 'POST'])
        def portal_household_member_new(self, **post):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            if request.httprequest.method == 'POST':
                vals = {
                    'name': (post.get('name') or '').strip(),
                    'firstname': (post.get('firstname') or '').strip(),
                    'email': (post.get('email') or '').strip(),
                    'phone': (post.get('phone') or '').strip(),
                    'birthdate_date': post.get('birthdate_date') or False,
                    'x_household_role': post.get('x_household_role') or 'other',
                    'x_costume_size': (post.get('x_costume_size') or '').strip(),
                    'x_sport_notes': (post.get('x_sport_notes') or '').strip(),
                    'parent_id': partner.id,
                }
                if vals['name']:
                    request.env['res.partner'].sudo().create(vals)
                    return request.redirect('/my/household')

            values = {
                'page_name': 'household',
                'manager': partner,
                'member': False,
            }
            return request.render('association_family.portal_household_member_form', values)

        @http.route('/my/household/<int:member_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
        def portal_household_member_edit(self, member_id, **post):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            member = self._get_member_for_manager(partner, member_id)
            if not member:
                return request.redirect('/my/household')

            if request.httprequest.method == 'POST':
                vals = {
                    'name': (post.get('name') or '').strip(),
                    'firstname': (post.get('firstname') or '').strip(),
                    'email': (post.get('email') or '').strip(),
                    'phone': (post.get('phone') or '').strip(),
                    'birthdate_date': post.get('birthdate_date') or False,
                    'x_household_role': post.get('x_household_role') or 'other',
                    'x_costume_size': (post.get('x_costume_size') or '').strip(),
                    'x_sport_notes': (post.get('x_sport_notes') or '').strip(),
                }
                member.sudo().write(vals)
                return request.redirect('/my/household')

            values = {
                'page_name': 'household',
                'manager': partner,
                'member': member,
            }
            return request.render('association_family.portal_household_member_form', values)

        @http.route('/my/household/<int:member_id>/archive', type='http', auth='user', website=True, methods=['POST'])
        def portal_household_member_archive(self, member_id, **post):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            member = self._get_member_for_manager(partner, member_id)
            if member and member != partner:
                member.sudo().write({'active': False})

            return request.redirect('/my/household')
