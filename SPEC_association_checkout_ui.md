# SPEC - association_checkout_ui

## Contexte

Ce module Odoo personnalise l'experience de checkout website_sale pour un usage association.

Objectifs metier:

- renommer les boutons et etapes du checkout;
- masquer le choix du moyen de paiement quand seul le virement est disponible;
- personnaliser la page de confirmation;
- ajouter un lien direct vers la facture sur la page finale.

## Module cible

- Nom technique: `association_checkout_ui`
- Type: module Odoo (UI website_sale + paiement)
- Version cible: Odoo 19
- Dependances minimales:
  - `website_sale`
  - `payment`
  - `sale_management`
  - `account`

## Perimetre fonctionnel

### 1) Renommage des etapes et boutons du checkout

Le module doit surcharger les libelles visibles par l'utilisateur sur le tunnel de commande:

- labels d'etapes (ex: panier, adresse, paiement, confirmation);
- boutons d'action (ex: continuer, payer, confirmer, retour).

Contraintes:

- ne pas modifier la logique serveur des etapes;
- ne changer que le texte affiche (et classes CSS si necessaire pour style);
- conserver la compatibilite responsive (desktop/mobile).

## Approche technique recommandee

### Vues/QWeb

- Heriter les templates website_sale du checkout et de confirmation via `xpath`.
- Isoler les changements de libelles dans les noeuds concernes.
- Inserer le bloc facture dans la page finale de confirmation.

### Logique Python

- Etendre les modeles ou routes seulement si necessaire pour exposer l'URL facture.
- Ne pas casser le flux standard de transaction/paiement Odoo.
- Gerer explicitement le cas "facture absente".

## Criteres d'acceptation

1. Les textes d'etapes/boutons du checkout affichent les nouveaux libelles attendus.
2. En absence de facture, un message informatif s'affiche sans erreur technique.

## Hors perimetre

- Modification du moteur de paiement Odoo.
- Generation forcee de facture en dehors du flux metier existant.
- Refonte complete du theme website.

## Livrables attendus

- nouveau module `association_checkout_ui`;
- vues XML de surcharge checkout + confirmation;
- tests (au minimum unitaires/integration legere) 
