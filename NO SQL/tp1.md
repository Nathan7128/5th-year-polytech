# MongoDB : partie 1

**Binôme** : Nathan, Talbot-Simon, Guillet


### Q1 : Créer la base de données CoursesBio contenant la collection ProduitBio

<u>**Commandes**</u>

```bash
use CoursesBio
db.createCollection("ProduitsBio")
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

On crée la base de nom CoursesBio avec la commande : use CoursesBio.  
La collection ProduitsBio est créé au moyen de la commande db.createCollection("ProduitsBio ").  
La variable db représente une instance de la base de données


<u>**Vérification**</u>

```bash
db
show collections
```


### Q2 : Insérer dans la collection ProduitBio, 3 produits bios. Chaque produit bio se caractérise par un nom, une catégorie (ex : Fruits, Légumes, Boissons, Epicerie) et un prix (en euros). Vérifier que la collection contient bien tous ces documents.

<u>**Commandes**</u>

```bash
db.ProduitsBio.insertMany([
	{"nom" : "Avocat", "categorie" : "fruit", "prix" : 2.5},
	{"nom" : "Fraise", "categorie" : "fruit", "prix" : 5},
	{"nom" : "Salade", "categorie" : "légume", "prix" : 1.5}
])
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

On ajoute une liste de documents à la collection ProduitsBio.


<u>**Vérification**</u>

```bash
db.ProduitsBio.find()
```


### Q3 : Insérer un produit nommé « Pomme Bio Gala » de la catégorie Fruits et au prix de 3.20€/kg, au moyen d’un objet JavaScript.

<u>**Commandes**</u>

```bash
var ProduitBio = {}
ProduitBio.nom = "Pomme Bio Gala"
ProduitBio.categorie = "Fruits"
ProduitBio.prix = 3.2 
db.ProduitsBio.insert(ProduitBio)
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

On ajoute un document correspondant à Pomme Bio Gala à la collection ProduitsBio.


<u>**Vérification**</u>

```bash
db.ProduitsBio.find()
```


### Q4 : Corriger le prix de la Pomme Bio Gala à 2.90€/kg et ajouter le champ origine : « France ».

<u>**Commandes**</u>

```bash
var modif = db.ProduitsBio.findOne({"nom" : "Pomme Bio Gala"})
modif.prix = 2.9
modif.origine = "France"
db.ProduitsBio.save(modif)
```


<u>**Résultat**</u>
 

<u>**Explication**</u>

On instancie une variable pour modifier le fruit en question, puis modifie le champ prix et ajoute le champ origine, avant de sauvegarder les modifications.


<u>**Vérification**</u>

```bash
db.ProduitsBio.find()
```


### Q5 : Afficher le prix et l’origine du produit Pomme Bio Gala.

<u>**Commandes**</u>

```bash
db.ProduitsBio.find({"nom" : "Pomme Bio Gala"}, {_id: 0, "prix" : 1,"origine" : 1})
```


<u>**Résultat**</u>
 

<u>**Explication**</u>

On cherche a récupérer uniquement les champs prix et origine du document Pomme Bio Gala.


<u>**Vérification**</u>

```bash
```


### Q6 : Donner les produits dont le prix est inférieur à 5 €.

<u>**Commandes**</u>

```bash
db.ProduitsBio.find({"prix" : {"$lt" : 5}})
```


<u>**Résultat**</u>
 

<u>**Explication**</u>

On filtre les produits dont le prix est inférieur à 5€ via l’opérateur $lt


<u>**Vérification**</u>

```bash
```

### Q7 : [Titre de la question 7]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 7
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 7.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 7
```

### Q8 : [Titre de la question 8]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 8
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 8.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 8
```

### Q9 : [Titre de la question 9]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 9
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 9.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 9
```

### Q10 : [Titre de la question 10]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 10
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 10.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 10
```

### Q11 : [Titre de la question 11]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 11
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 11.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 11
```

### Q12 : [Titre de la question 12]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 12
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 12.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 12
```

### Q13 : [Titre de la question 13]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 13
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 13.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 13
```

### Q14 : [Titre de la question 14]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 14
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 14.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 14
```

### Q15 : [Titre de la question 15]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 15
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 15.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 15
```

### Q16 : [Titre de la question 16]

<u>**Commandes**</u>

```bash
# Insérer ici les commandes MongoDB pour la question 16
```

<u>**Résultat**</u>
 

<u>**Explication**</u>

Brève explication de ce que font les commandes pour la question 16.


<u>**Vérification**</u>

```bash
# Commandes de vérification pour la question 16
```