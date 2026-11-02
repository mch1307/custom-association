odoo.define('association_family.event_participants_checkout', function (require) {
    'use strict';

    const ajax = require('web.ajax');
    const publicWidget = require('web.public.widget');

    publicWidget.registry.AssociationFamilyEventParticipants = publicWidget.Widget.extend({
        selector: '#association-family-event-participants, #association-family-cart-members',
        events: {
            'change .js_association_family_participants': '_onParticipantsChange',
            'change .js_association_family_member': '_onMemberChange',
        },

        _onParticipantsChange: function (ev) {
            const select = ev.currentTarget;
            const lineId = parseInt(select.dataset.lineId, 10);
            if (!lineId) {
                return;
            }

            const participantIds = [];
            for (const option of select.options) {
                if (option.selected) {
                    participantIds.push(parseInt(option.value, 10));
                }
            }

            ajax.jsonRpc('/association_family/cart/line_participants', 'call', {
                line_id: lineId,
                participant_ids: participantIds,
            });
        },

        _onMemberChange: function (ev) {
            const select = ev.currentTarget;
            const lineId = parseInt(select.dataset.lineId, 10);
            if (!lineId) {
                return;
            }

            ajax.jsonRpc('/association_family/cart/line_member', 'call', {
                line_id: lineId,
                member_id: select.value || false,
            });
        },
    });
});
