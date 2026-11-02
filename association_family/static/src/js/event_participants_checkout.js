/** @odoo-module */

function isCheckoutContext() {
    const path = window.location.pathname || '';
    if (path.startsWith('/shop/')) {
        return true;
    }
    return Boolean(document.querySelector('#wrapwrap .oe_website_sale, .o_wsale_my_cart'));
}

document.addEventListener('change', function (event) {
    if (!isCheckoutContext()) {
        return;
    }

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
