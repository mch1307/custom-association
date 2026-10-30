document.addEventListener('DOMContentLoaded', function () {
    function applyAssociationLabels() {
        document.querySelectorAll('button[type="submit"], button.btn-primary').forEach(function (button) {
            if ((button.textContent || '').trim() === 'Payer maintenant') {
                button.textContent = 'Confirmer la commande';
            }
        });

        document.querySelectorAll('span, div, h2, p, strong, label').forEach(function (element) {
            if ((element.textContent || '').trim() === 'Paiement') {
                element.textContent = 'Confirmation';
            }
        });
    }

    applyAssociationLabels();

    const observer = new MutationObserver(function () {
        applyAssociationLabels();
    });
    observer.observe(document.body, { childList: true, subtree: true });
});
