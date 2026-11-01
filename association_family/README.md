# Association Family

Module Odoo 19 Community pour gerer les menages (responsable + membres), centraliser la facturation sur le responsable, et attribuer chaque adhesion/produit/inscription evenement a une personne du menage.

## Fonctionnalites

- extension de `res.partner` pour le role menage, statut adhesion, date de fin et taille du menage ;
- gestion portail du menage (liste, ajout, edition, archivage) ;
- attribution par ligne de commande via `sale.order.line.member_id` ;
- integration `event` + `event_sale` avec selection des participants du menage par ligne panier ;
- propagation des adhesions aux beneficiaires lors du paiement de facture selon configuration produit.

## Prerequis

- Odoo 19 Community
- modules: `contacts`, `portal`, `website_sale`, `sale_management`, `account`, `event`, `event_sale`

## Installation

1. Copier `association_family` dans le dossier des addons custom.
2. Redemarrer Odoo.
3. Mettre a jour la liste des modules.
4. Installer `Association Family`.

## Flux evenement (website)

1. Le responsable ajoute des billets evenement au panier.
2. Le panier affiche un bloc `Participants du menage` pour les lignes evenement.
3. La selection est envoyee a `/association_family/cart/line_participants`.
4. Les `event.registration` sont affectees aux membres selectionnes.
5. La page de confirmation affiche un recapitulatif des participants enregistres.

## Tests unitaires

Executer:

```bash
.\.venv\Scripts\python.exe -m pytest -q association_family\tests
```

## Limites connues

- les tests fournis sont des tests unitaires hors runtime Odoo ;
- pour valider completement les vues et securites, ajouter des tests TransactionCase dans une base Odoo de test.
