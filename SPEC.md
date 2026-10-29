# Spécification fonctionnelle détaillée
## Module Odoo 19 - Association Auto Confirm

### Version
1.0

### Contexte

Le flux eCommerce standard d'Odoo n'est pas adapté au fonctionnement d'une association utilisant principalement le virement bancaire.

Dans le fonctionnement actuel :

```text
Commande Web
    ↓
Transaction bancaire créée
    ↓
Etat = En attente
    ↓
Devis
    ↓
Attente du paiement
    ↓
Confirmation manuelle
```

Pour Les Arallumés, la réception du paiement peut intervenir plusieurs jours après l'inscription. La commande doit néanmoins être considérée comme valide dès l'inscription.

Objectifs métier
Objectif principal

Transformer automatiquement un devis issu du site web en commande confirmée dès que le membre termine le processus d'inscription.

Le paiement reste attendu mais ne bloque plus l'enregistrement de l'adhésion.

Règles métier
RM-001 - Déclenchement

Le module doit intervenir lorsqu'une transaction de paiement est créée avec les conditions suivantes :

Origine : Boutique en ligne
ET
Mode de paiement : Virement bancaire
ET
Etat transaction : En attente (Pending)

RM-002 - Confirmation automatique de la commande

Lorsque RM-001 est satisfaite :

Etat du devis = Draft


La commande doit être automatiquement confirmée.

Résultat :

Draft
↓
Sale Order

RM-003 - Non-intervention sur les autres moyens de paiement

Le module ne doit pas modifier :

Stripe
PayPal
Mollie
Adyen
Cartes bancaires
Paiements manuels

Ces fournisseurs conservent leur comportement natif.

RM-004 - Création automatique de la facture

Après confirmation de la commande :

Commande
↓
Facture


Une facture client doit être créée automatiquement.

RM-005 - Validation automatique de la facture

La facture créée doit être immédiatement validée.

Résultat :

Facture brouillon
↓
Facture comptabilisée

RM-006 - Facture non payée

La facture doit rester :

Non payée


Le module ne crée pas de paiement fictif.

RM-007 - Conservation de la transaction bancaire

La transaction bancaire doit rester :

En attente


jusqu'à la réception réelle du virement.

RM-008 - QR EPC

Le module ne modifie pas :

l'IBAN
la communication structurée
le QR EPC
les instructions de paiement

Le comportement standard Odoo doit être conservé.

RM-009 - E-mail envoyé au membre

Après création de la facture :

Le flux standard Odoo d'envoi des documents doit être conservé.

Le membre doit recevoir :

Numéro de facture
Montant
Instructions de paiement
Lien vers la facture
QR EPC disponible dans le portail

RM-010 - Paiement réel obligatoire

L'activation du membre ne doit jamais être basée sur :

Transaction Pending


Seule la réception du paiement bancaire reste une preuve de paiement.

Gestion des adhésions
RM-011 - Statut membre

Les statuts possibles sont :

Prospect
En attente de paiement
Actif
Expiré

RM-012 - Nouveau membre

Lors de la création d'une commande d'adhésion :

Statut membre = En attente de paiement

RM-013 - Réception du paiement

Lorsqu'une facture est réconciliée :

Facture = Payée


Le statut devient :

Actif


Cette règle sera implémentée dans une version ultérieure.

Gestion des familles
RM-014 - Facturation familiale

Une famille est représentée par :

Famille Champagne


de type :

Société


Les membres sont rattachés à la famille :

Famille Champagne
├── Mic Champagne
├── Membre 2
└── Membre 3

RM-015 - Payeur unique

Les factures sont toujours établies pour :

Famille Champagne


et jamais pour les membres individuels.

RM-016 - Commande multi-membres

Une même commande peut contenir :

1 Cotisation adulte
2 Cotisations enfant


Une seule facture est générée.

Gestion des événements
RM-017 - Compatibilité événements

Le module doit fonctionner de manière identique pour :

Adhésions
Événements
Voyages
Soupers
Activités

Tout produit vendu via le site web est traité de la même manière.

RM-018 - Inscriptions multi-articles

Une commande peut contenir simultanément :

Cotisation annuelle
+
Participation souper
+
Participation voyage


Une seule commande et une seule facture sont créées.

Cas d'exclusion

Le module ne doit rien faire lorsque :

CE-001
Transaction annulée

CE-002
Transaction en erreur

CE-003
Commande non issue du site web

CE-004
Commande déjà confirmée

CE-005
Facture déjà créée

CE-006
Montant de la transaction = 0 €

Exigences techniques
RT-001

Le module doit être compatible avec :

Odoo Community 19

RT-002

Le module ne doit pas modifier :

website_sale
sale_management
account
payment

Aucune modification du code standard Odoo n'est autorisée.

RT-003

L'implémentation doit utiliser l'héritage Odoo (_inherit).

RT-004

Le module doit être désinstallable sans impact sur les données existantes.

RT-005

Le module doit journaliser les actions suivantes :

Commande confirmée automatiquement
Facture créée automatiquement
Facture validée automatiquement


dans le chatter de la commande.

Scénario nominal
Mic Champagne
↓
Ajoute une adhésion au panier
↓
Choisit Virement bancaire
↓
Valide la commande
↓
Transaction S00012 créée
↓
Etat = En attente
↓
Commande automatiquement confirmée
↓
SO00012 créée
↓
Facture FAC/2026/00003 créée
↓
Facture validée
↓
QR EPC disponible
↓
Paiement reçu quelques jours plus tard
↓
Facture payée
↓
Membre actif

Critères d'acceptation
Avant installation du module
Devis : S00012
Transaction : En attente
Facture : Aucune

Après installation du module
Commande : SO00012
Transaction : En attente
Facture : FAC/2026/00003
Etat facture : Non payée
QR EPC : Présent

Validation finale

Le membre doit pouvoir :

Finaliser son inscription
Recevoir une commande confirmée
Recevoir une facture valide
Utiliser le QR EPC
Payer ultérieurement par virement

sans intervention manuelle de l'administrateur.

Roadmap
Version 1.1

Activation automatique du statut membre après paiement de la facture.

Version 1.2

Relances automatiques des factures impayées :

J+7
J+14
J+30
Version 1.3

Gestion avancée des familles :

Responsable familial
Paiement centralisé
Renouvellement groupé
Version 1.4

Tableau de bord association :

Membres actifs
Membres en attente
Cotisations impayées
Événements à venir

Tu peux enregistrer ce contenu dans `SPECIFICATION.md` à la racine du module afin de documenter le besoin fonctionnel avant le développement.