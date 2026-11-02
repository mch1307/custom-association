try:
    from odoo import http
    from odoo.http import request
except (ImportError, ModuleNotFoundError):
    http = None
    request = None


if http and getattr(http, 'Controller', None):
    class AssociationFamilyPortal(http.Controller):

        @staticmethod
        def _partner_supports_firstname(partner_model):
            return 'firstname' in getattr(partner_model, '_fields', {})

        @staticmethod
        def _partner_supports_birthdate(partner_model):
            return 'birthdate_date' in getattr(partner_model, '_fields', {})

        @staticmethod
        def _partner_supports_household_role(partner_model):
            return 'x_household_role' in getattr(partner_model, '_fields', {})

        @staticmethod
        def _partner_supports_costume_size(partner_model):
            return 'x_costume_size' in getattr(partner_model, '_fields', {})

        @staticmethod
        def _partner_supports_membership_status(partner_model):
            return 'x_membership_status' in getattr(partner_model, '_fields', {})

        @staticmethod
        def _build_member_vals(
            post,
            include_firstname=False,
            include_birthdate=False,
            include_household_role=False,
            include_costume_size=False,
            parent_id=None,
        ):
            vals = {
                'name': (post.get('name') or '').strip(),
                'email': (post.get('email') or '').strip(),
                'phone': (post.get('phone') or '').strip(),
            }
            if include_firstname:
                vals['firstname'] = (post.get('firstname') or '').strip()
            if include_birthdate:
                vals['birthdate_date'] = post.get('birthdate_date') or False
            if include_household_role:
                vals['x_household_role'] = post.get('x_household_role') or 'other'
            if include_costume_size:
                vals['x_costume_size'] = (post.get('x_costume_size') or '').strip()
            if parent_id:
                vals['parent_id'] = parent_id
            return vals

        def _current_partner(self):
            return request.env.user.partner_id

        def _is_household_responsible(self, partner):
            if not partner or partner.parent_id:
                return False
            if 'x_household_role' not in getattr(partner, '_fields', {}):
                return True
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

            partner_model = request.env['res.partner']

            values = {
                'page_name': 'household',
                'manager': partner,
                'members': self._get_household_members(partner),
                'has_household_role_field': self._partner_supports_household_role(partner_model),
                'has_membership_status_field': self._partner_supports_membership_status(partner_model),
            }
            return request.render('association_family.portal_my_household', values)

        @http.route('/my/household/new', type='http', auth='user', website=True, methods=['GET', 'POST'])
        def portal_household_member_new(self, **post):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            partner_model = request.env['res.partner']
            has_firstname_field = self._partner_supports_firstname(partner_model)
            has_birthdate_field = self._partner_supports_birthdate(partner_model)
            has_household_role_field = self._partner_supports_household_role(partner_model)
            has_costume_size_field = self._partner_supports_costume_size(partner_model)

            if request.httprequest.method == 'POST':
                vals = self._build_member_vals(
                    post,
                    include_firstname=has_firstname_field,
                    include_birthdate=has_birthdate_field,
                    include_household_role=has_household_role_field,
                    include_costume_size=has_costume_size_field,
                    parent_id=partner.id,
                )
                if vals['name']:
                    partner_model.sudo().create(vals)
                    return request.redirect('/my/household')

            values = {
                'page_name': 'household',
                'manager': partner,
                'member': False,
                'has_firstname_field': has_firstname_field,
                'has_birthdate_field': has_birthdate_field,
                'has_household_role_field': has_household_role_field,
                'has_costume_size_field': has_costume_size_field,
            }
            return request.render('association_family.portal_household_member_form', values)

        @http.route('/my/household/<int:member_id>', type='http', auth='user', website=True, methods=['GET', 'POST'])
        def portal_household_member_edit(self, member_id, **post):
            partner = self._current_partner()
            if not self._is_household_responsible(partner):
                return request.redirect('/my')

            partner_model = request.env['res.partner']
            has_firstname_field = self._partner_supports_firstname(partner_model)
            has_birthdate_field = self._partner_supports_birthdate(partner_model)
            has_household_role_field = self._partner_supports_household_role(partner_model)
            has_costume_size_field = self._partner_supports_costume_size(partner_model)

            member = self._get_member_for_manager(partner, member_id)
            if not member:
                return request.redirect('/my/household')

            if request.httprequest.method == 'POST':
                vals = self._build_member_vals(
                    post,
                    include_firstname=has_firstname_field,
                    include_birthdate=has_birthdate_field,
                    include_household_role=has_household_role_field,
                    include_costume_size=has_costume_size_field,
                )
                member.sudo().write(vals)
                return request.redirect('/my/household')

            values = {
                'page_name': 'household',
                'manager': partner,
                'member': member,
                'has_firstname_field': has_firstname_field,
                'has_birthdate_field': has_birthdate_field,
                'has_household_role_field': has_household_role_field,
                'has_costume_size_field': has_costume_size_field,
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
