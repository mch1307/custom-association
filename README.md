# Association Auto Confirm

Module Odoo personnalisé pour confirmer automatiquement une commande web lorsqu’un paiement par virement bancaire est enregistré en attente, sans bloquer l’adhésion tant que le paiement réel n’a pas été reçu.

## Objectif

Ce module répond à un besoin d’association :

- une commande issue du site web doit être validée rapidement,
- le paiement bancaire peut arriver plusieurs jours plus tard,
- la transaction reste en attente jusqu’à la réception réelle du virement,
- la facture est créée et validée automatiquement pour conserver le flux standard Odoo.

Le comportement principal est le suivant :

- si une transaction de paiement est créée ou modifiée avec un statut `pending`,
- si le moyen de paiement est un virement bancaire,
- si la commande associée est encore en brouillon,
- alors la commande est confirmée automatiquement,
- une facture client est créée si nécessaire,
- la facture est validée,
- le document de facture est envoyé au client par e-mail dans le flux standard Odoo.

## Périmètre fonctionnel

Le module applique les règles métier suivantes :

- confirmation automatique d’un devis/commande web pour les paiements par virement bancaire ;
- non-intervention sur les autres fournisseurs de paiement (Stripe, PayPal, Mollie, Adyen, cartes bancaires, paiements manuels) ;
- création automatique de la facture après confirmation de la commande ;
- validation immédiate de la facture ;
- conservation de la transaction bancaire en attente jusqu’au paiement réel ;
- conservation du comportement standard Odoo sur les QR code, l’IBAN et la communication structurée.

Le module est implémenté selon la spécification métier décrite dans [SPEC.md](SPEC.md).

## Structure du projet

```text
association-auto-confirm/
├── SPEC.md
├── README.md
└── association_auto_confirm/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   └── payment_transaction.py
    ├── tests/
    │   └── test_payment_transaction.py
    └── views/
        └── payment_confirmation.xml
```

## Composant principal

Le point d’entrée est la classe `PaymentTransaction` héritée de `payment.transaction`.

Elle détecte les transactions déclenchantes et appelle automatiquement :

1. la confirmation de la commande,
2. la création de la facture,
3. la validation de la facture,
4. l’envoi de la facture au client.

## Installation

### Prérequis

- Odoo 19
- module `sale_management`
- module `website_sale`
- module `payment`
- module `account`

### Étapes

1. Copier le dossier `association_auto_confirm` dans le dossier `custom_addons` de votre instance Odoo.
2. Redémarrer Odoo.
3. Mettre à jour la liste des modules.
4. Installer le module `Association Auto Confirm` depuis l’interface Odoo.

## Utilisation

Le module fonctionne lorsque :

- une transaction de paiement est créée ou modifiée,
- son état est `pending`,
- son fournisseur correspond à un virement bancaire,
- la commande liée est encore non confirmée.

Dans ce cas, il confirme automatiquement la commande et génère la facture attendue.

## Tests

Le dépôt contient des tests unitaires pour valider la logique métier sans Odoo réel :

```bash
.\.venv\Scripts\python.exe -m pytest -q association_auto_confirm\tests\test_payment_transaction.py
```

Les tests vérifient notamment :

- confirmation automatique avec virement bancaire,
- non-intervention sur d’autres fournisseurs,
- gestion des montants nuls,
- ordre déjà confirmé,
- validation de facture existante,
- envoi d’email uniquement si le contact a un e-mail.

## Notes de conception

- Le paiement réel est toujours distinct de la transaction de paiement en attente.
- Le module ne crée pas de paiement fictif.
- La transaction reste `pending` jusqu’à la réception du virement bancaire effectif.
- La facture est envoyée selon le flux standard Odoo, sans modifier les instructions de paiement ni le QR EPC.

## Licence

Ce projet est distribué sous licence AGPL-3.
