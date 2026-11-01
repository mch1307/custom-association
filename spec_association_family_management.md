# Association Family Management

## Spécification fonctionnelle

### Version

1.0

### Cible

Odoo 19 Community

### Objectif

Permettre à une association de gérer des ménages (familles) composés d'un responsable et de plusieurs membres dépendants.

Le responsable doit pouvoir :

- gérer les membres de son ménage depuis le portail ;
- renouveler les adhésions ;
- acheter des billets d'événements ;
- acheter des produits (costumes, t-shirts, etc.) ;
- attribuer systématiquement chaque achat à un membre précis de son ménage.

Le système doit conserver une traçabilité individuelle de tous les membres tout en centralisant les commandes et la facturation sur le responsable.

---

# 1. Principes de conception

## 1.1 Modèle familial

Le module s'appuie sur le modèle natif Odoo :

```text
res.partner.parent_id
res.partner.child_ids
```

Exemple :

Michel Champagne
├── Sophie Champagne
└── Lucas Champagne

Michel est le responsable du ménage.

Sophie et Lucas sont des sous-contacts.
```

Aucune société fictive de type "Famille Champagne" n'est créée.

---

## 1.2 Principe général

Le responsable :

- achète ;
- paie ;
- gère les membres.

Les objets métier (adhésion, billet, costume, équipement, etc.) sont toujours attribués à une personne physique.

---

# 2. Modèle de données

## Extension de res.partner

### Rôle dans le ménage

Champ :

```python
x_household_role
```

Type :

```python
Selection
```

Valeurs :

```text
responsible
partner
child
other
```

Libellés :

```text
Responsable
Conjoint
Enfant
Autre
```

---

### Statut adhésion

Champ :

```python
x_membership_status
```

Type :

```python
Selection
```

Valeurs :

```text
inactive
active
expired
retired
```

Libellés :

```text
Inactif
Actif
Expiré
Ancien
```

---

### Date de fin d'adhésion

Champ :

```python
x_membership_end_date
```

Type :

```python
Date
```

---

### Responsable du ménage

Champ calculé :

```python
x_household_manager_id
```

Règle :

```text
Si parent_id existe :
    parent_id

Sinon :
    partenaire courant
```

---

### Nombre de personnes couvertes

Champ calculé :

```python
x_household_size
```

Calcul :

```text
1 + nombre de sous-contacts actifs
```

---

# 3. Relations implicites

Le système considère automatiquement comme membres du ménage :

```python
partner
+
partner.child_ids
```

Exemple :

```text
Michel
├── Sophie
└── Lucas
```

Résultat :

```text
Ménage = 3 personnes
```

---

# 4. Portail membre

## Nouvelle section

```text
Mon ménage
```

Accessible uniquement au responsable.

---

## Vue principale

Exemple :

```text
Mon ménage

Michel Champagne
Responsable
Adhésion active

Sophie Champagne
Conjoint
Adhésion active

Lucas Champagne
Enfant
Adhésion active
```

---

# 5. Gestion des membres

## Ajouter un membre

Action :

```text
Ajouter un membre
```

Informations :

```text
Nom
Prénom
Date de naissance
Email
Téléphone
Type de membre
Taille costume
Photo
```

Résultat :

```python
parent_id = partenaire responsable
```

---

## Modifier un membre

Le responsable peut modifier :

```text
Coordonnées
Date de naissance
Photo
Taille costume
Informations sportives
```

---

## Désactiver un membre

Action :

```text
Archiver
```

Aucune suppression physique.

Le partenaire passe :

```python
active = False
```

---

# 6. Gestion des adhésions

## Produits

Exemples :

```text
Adhésion Individuelle 2027
Adhésion Familiale 2027
```

---

## Renouvellement via portail

Le responsable clique :

```text
Renouveler mon adhésion
```

Le système affiche :

```text
Personnes couvertes :

✓ Michel Champagne
✓ Sophie Champagne
✓ Lucas Champagne

Total : 3 personnes
```

Liste générée automatiquement à partir du ménage.

---

## Paiement

Une seule commande :

```text
Client facturé = Michel Champagne
```

Une seule facture :

```text
Michel Champagne
```

---

## Activation

Lorsque la facture est payée :

```python
Michel
Sophie
Lucas
```

reçoivent :

```text
Statut : actif
Date expiration : calculée selon le produit
```

---

# 7. Gestion des événements

## Sélection des participants

Lors d'une inscription :

```text
Participants :

☑ Michel Champagne
☑ Sophie Champagne
☐ Lucas Champagne
```

---

## Résultat

Une inscription individuelle est créée pour chaque participant sélectionné.

Exemple :

```text
Michel
Sophie
```

sont inscrits.

Lucas ne l'est pas.

---

# 8. Gestion de la boutique

## Principe fondamental

Tout achat doit être attribué à une personne.

---

## Extension de sale.order.line

Nouveau champ :

```python
member_id
```

Type :

```python
Many2one(res.partner)
```

Objet :

```text
Membre bénéficiaire
```

---

## Exemple

Produit :

```text
Costume Carnaval
```

Affichage :

```text
Attribuer à :

( ) Michel Champagne
( ) Sophie Champagne
(X) Lucas Champagne
```

---

## Résultat

Commande :

```text
Facturé à :
Michel Champagne
```

Ligne :

```text
Costume Carnaval
Attribué à :
Lucas Champagne
```

---

# 9. Consultation du dossier membre

Depuis la fiche partenaire :

```text
Lucas Champagne
```

Le système affiche :

### Adhésions

```text
2025
2026
2027
```

### Événements

```text
Souper Carnaval 2026
Bal du Prince 2027
```

### Produits

```text
Costume 2026
T-shirt Carnaval
```

---

# 10. Règles métier

## RM01

Un responsable peut gérer tous ses sous-contacts.

---

## RM02

Un sous-contact ne peut pas gérer d'autres membres.

---

## RM03

Toutes les factures sont émises au responsable.

---

## RM04

Toute adhésion payée est propagée aux membres concernés.

---

## RM05

Toute inscription à un événement doit être attribuée à une personne.

---

## RM06

Tout produit vendu doit être attribué à une personne.

---

## RM07

Un membre ne peut être supprimé si un historique existe.

---

## RM08

Le responsable ne peut consulter que les membres de son ménage.

---

## RM09

Les bénéficiaires proposés lors d'un achat sont limités au ménage du responsable connecté.

---

# 11. Sécurité

## Groupe Responsable de ménage

Peut :

- consulter son ménage ;
- modifier son ménage ;
- effectuer des achats ;
- renouveler des adhésions ;
- inscrire des participants.

Ne peut pas :

- accéder aux autres ménages ;
- modifier les données administratives de l'association.

---

# 12. Évolutions futures

Prévoir la compatibilité avec :

- Membership
- Event
- Event Sale
- Website Sale
- Portal
- QR SEPA
- Gestion des costumes
- Gestion des équipements
- Gestion des rôles dans le comité

---

# Résumé

Le module introduit la notion de ménage basée sur les sous-contacts natifs Odoo.

Le responsable :

- gère son ménage ;
- paie pour le ménage ;
- effectue les achats.

Les membres :

- disposent de leur propre historique ;
- possèdent leurs propres adhésions ;
- participent individuellement aux événements ;
- reçoivent individuellement les produits et équipements.

Cette approche garantit une facturation centralisée tout en conservant une gestion individuelle complète indispensable à une association.