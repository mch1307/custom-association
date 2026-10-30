function normalizeText(value) {
    return (value || '').replace(/\s+/g, ' ').trim();
}

function replaceButtonLabel() {
    const candidates = document.querySelectorAll(
        'button[type="submit"], button.btn-primary, button[name*="pay"], button[id*="pay"], a.btn-primary, a[name*="pay"], a[id*="pay"]'
    );
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
    document.querySelectorAll('span, div, h2, p, strong, label, li, a').forEach(function (element) {
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

window.addEventListener('pageshow', applyAssociationLabels);
