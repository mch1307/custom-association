odoo.define('association_family.event_participants_checkout', function () {
    'use strict';

    document.addEventListener('change', function (event) {
        const target = event.target;
        if (!target || !target.classList) {
            return;
        }

        if (target.classList.contains('js_association_family_member')) {
            const lineId = target.dataset.lineId;
            const memberId = target.value || false;
            if (!lineId) {
                return;
            }

            fetch('/association_family/cart/line_member', {
                method: 'POST',
                headers: {'Content-Type': 'application/json; charset=utf-8'},
                body: JSON.stringify({line_id: Number(lineId), member_id: memberId}),
            });
        }

        if (target.classList.contains('js_association_family_participants')) {
            const lineId = target.dataset.lineId;
            const selected = Array.from(target.selectedOptions).map(option => Number(option.value));
            if (!lineId) {
                return;
            }

            fetch('/association_family/cart/line_participants', {
                method: 'POST',
                headers: {'Content-Type': 'application/json; charset=utf-8'},
                body: JSON.stringify({line_id: Number(lineId), participant_ids: selected}),
            });
        }
    });
});
