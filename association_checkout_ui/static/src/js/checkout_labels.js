function normalizeText(value) {
    return (value || '').replace(/\s+/g, ' ').trim();
}

function isCheckoutContext() {
    const path = window.location.pathname || '';
    if (path.startsWith('/shop/')) {
        return true;
    }
    return Boolean(document.querySelector('.o_wsale_checkout_steps, form[action*="/shop/"]'));
}

function replaceButtonLabel() {
    const candidates = document.querySelectorAll([
        '.o_wsale_payment_form button[type="submit"]',
        '.o_wsale_payment_form .btn-primary',
        'form[action*="/shop/payment"] button[type="submit"]',
        'form[action*="/shop/payment"] .btn-primary',
        'button[name*="pay"]',
        'button[id*="pay"]',
    ].join(', '));

    candidates.forEach(function (button) {
        const current = normalizeText(button.textContent);
        if (!current) {
            return;
        }
        if (current.includes('Payer maintenant')) {
            const labelNode = button.querySelector('span') || button;
            labelNode.textContent = 'Confirmer la commande';
            return;
        }
        if (current === 'Payer') {
            const labelNode = button.querySelector('span') || button;
            labelNode.textContent = 'Commander';
        }
    });
}

function replaceStepLabel() {
    const stepNodes = document.querySelectorAll('.o_wsale_checkout_steps a, .o_wsale_checkout_steps span, .o_wsale_checkout_steps li');
    stepNodes.forEach(function (element) {
        if (normalizeText(element.textContent) === 'Paiement') {
            element.textContent = 'Confirmation';
        }
    });
}

function applyAssociationLabels() {
    replaceButtonLabel();
    replaceStepLabel();
}

function bootstrapAssociationLabels() {
    if (!isCheckoutContext()) {
        return;
    }

    applyAssociationLabels();

    const observer = new MutationObserver(function () {
        applyAssociationLabels();
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Odoo can inject checkout blocks after DOMContentLoaded; retry briefly.
    let attempts = 0;
    const intervalId = setInterval(function () {
        attempts += 1;
        applyAssociationLabels();
        if (attempts >= 20) {
            clearInterval(intervalId);
        }
    }, 300);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrapAssociationLabels);
} else {
    bootstrapAssociationLabels();
}

window.addEventListener('pageshow', function () {
    if (!isCheckoutContext()) {
        return;
    }
    applyAssociationLabels();
});
