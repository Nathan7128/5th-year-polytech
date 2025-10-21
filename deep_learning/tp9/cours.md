# Application de constraintes sur un modèle de Machine Learning

## Introduction

Dans le problème précédent, on avait entrainé un modèle de régression qui contenait la contrainte sous la forme d'un terme de pénalisation.  
Dans ce chapitre, ce qu'on va faire est différent : on va entrainer un réseau de neuronnes de telle sorte que sa fonction cout prenne des valeurs importantes lorsque la contrainte n'est pas respectée.  

On va faire ceci de deux manières :
1) En modifiant la fonction cout pour appliquer les contraintes
2) En construisant un 2ème réseau de neuronnes qui "force" le premier à appliquer la contrainte

## Application de contraintes en appliquant la fonction coût

C'est la même idée que lorsqu'on applique la méthode de pénalisation : on rajoute un terme à la fonction coût.  
Lorsque les contraintes ne sont pas respectées, ce terme de pénalisation prend des valeurs élevées.  
On va donc devoir être capable de cocher sa propre fonction coût.  
Ceci est possible avec Keras en définissant une fonction qui doit nécessairement se présenter sous la forme suivante :  

```python
def custom_loss(y_true, y_pred):
    # utiliser uniquement des instructions de TensorFlow
    # calculer ici le coût à retourner (par exemple MSE + terme de pénalisation)
    return coût
```

Ensuite, au moment de compiler le modèle, au lieu d'écrire loss='mse' (par exemple) on écrira :

```python
loss = custom_loss (sans guillements et sans paramètres)
```

### Exercice
Faire le modèle de réseau de neuronnes qui apprend la fonction **y = sin(2*pi*x)** avec x € [0, 1].  
Au lieu d'utiliser `loss = 'mse'`, on va coder "à la main" cette fonction cout en définissant la fonction custom_loss qui devra calculer :


C = $$\displaystyle \frac{1}{N}\sum_{i=1}^{N}\left(y_{\mathrm{pred}}^{\,i} - y_{\mathrm{true}}^{\,i}\right)^{2}$$

On devra utiliser les 2 instructions Tensorflow suivantes :
1) tf_square : met les compasantes au carré
2) tf.reduce_mean : fait la moyenne de toutes les composantes d'un tenseur


Imaginons qu'on veuille appliquer la contrainte suivante à notre sinus :  
On veut que le "sinus" ne dépasse pas la valeur 0.5 :  
Il faut donc rajouter un terme à la fonction coût qui va prendre des valeurs importantes lorsque **sin(2*pi*x) > 0.5**.  
Par exemple :  

$$
C = \frac{1}{N}\sum_{i=1}^{N}\left(y_{\mathrm{pred}}^{\,i}-y_{\mathrm{true}}^{\,i}\right)^{2}
\;+\; \frac{1}{N}\sum_{i=1}^{N}\max\!\left(0,\;y_{\mathrm{pred}}^{\,i}-0.5\right)
$$

</div>

## Application de contraintes en conditionnant un réseau de neurones par un autre réseau de neurones

On reprend le même exemple que précédemment, i.e., contraindre un sinus à prendre des valeurs entre -0.5 et +0.5.  
Dans un premier temps, on va entrainer un modèle de classification qui en entrée prend un chiffre y_i € R et en sortie renvoie s_i, tel que :  
**(*)**
- s_i = 0 si |y_i| > 0.5
- s_i = 1 si |y_i| <= 0.5

Pour construire ce modèle, on générera 1000 données (y_i, s_i) i € [|1, 2000|] avec y_i généré aléatoirement entre -2 et 2.  
Et s_i labelisé selon **(*)**.  
On entrainera un modèle qu'on appellera "model2".  
On choisira "accuracy" comme métrique et "binary_crossentropy" comme fonction coût.  
L'idée est la suivante : on met le model2 en série avec le model1 et c'est le model1 qui doit générer un sinus qui respect les contraintes.  
On entraine l'ensemble model1 + model2 de telle sorte que :
- Ce qui sort du model1 doit etre sin(2*pi*x)
- Ce qui sort du model2 doit etre égal à 1 car dans ce cas ça veut dire sa entrée y = sin(2*pi*x) est comprise entre -0.5 et +0.5.
- On rend non-entrainable les paramètres du model2 car il a déjà été entrainé avant.  

Le modèle complet va avoir 2 sorties : [y_pred, s_pred]
Le modèle complet sera entainé de telle sorte qu'il minimise C = C1 + C2

$$
C_1 \;=\; \frac{1}{N}\sum_{i=1}^{N}\left(y_{\mathrm{pred}}^{(i)} - \sin\!\bigl(2\pi x_i\bigr)\right)^{2}
$$

$$
C_2 \;=\; \frac{1}{N}\sum_{i=1}^{N}\left(s_{\mathrm{pred}}^{(i)} - 1\right)^{2}
$$

Ensuite, on utilisera uniquement model1 pour savoir s'il génère un sinus qui respecte les contraintes


## Les réseaux GAN (Generative Adversarial Network)

Les réseaux GAN sont des modèles génératifs (comme les autoencodeurs variationnels) dont le but est de générer des données qui ont l'air réelles.  
Comme précédemment, un GAN utilise 3 modèles de réseau de neuronnes :
1) Un classifieur qui devra être entrainé pour classer une donnée réelle ou non réelle.  
Une données réelle vient d'un dataset dont on dispose et une donnée non réelle vient d'un autre réseau qui aura géneré des données non réelles.
2) Un générateur qui doit générer des données qui ont l'air réel.
3) Un modèle GAN qui comporte les deux réseaux de neuronnes précédents mis en série.  
La différence par rapport à l'exemple précédent, c'est que le classifieur (on l'appelle le discriminateur) et le Générateur doivent être entrainés alternativement.  
De la même manière que ce qu'on avait fait pour les auto-encodeurs variationnels, l'entrée du générateur s'appelle l'espace latent et on doit lui fournir en entrée un vecteur x = (x1, x2, ..., xn) tq xi ~ N(0, 1)

**Exemple** :  
On va créer un modèle GAN pour génerer des fausses données sur la courbe d'équation y = x².  
Autrement dit, on veut que le générateur génère des vecteurs y = (y1, y2) tel que ces points soient sur la courbe y2 = y1².  
Les "vrais" points de la base de données d'apprentissage seront exactement sur la courbe d'éq. : y = x²  

### Etapes de codage :  
1) Créer un générateur avec un espace latent de dimension 5 sans le compiler.  
Nommer ce premier modèle Générateur.
2) Créer un classifieur et le compiler.
Nommer ce 2ème modèle Classifieur.
3) Créer le réseau GAN qui met les deux premiers modèles en série et le compiler.
4) Créer une fonction *generate_real_sample(n)*  

**Entrée** : n le nombre de samples qu'on veut générer.  
**Sortie** : X de dimension (n, 2) et y de dimension (n, 1) pour les données réelles et son label (=1)

5) Créer une fonction *generate_fake_sample(generateur, latent_dim = 5, n)  

En sortie, la fonction retournera un vecteur X de fausses données de dimension (n, 2) et y vecteur des labels de dim (n, 1) (=0)

6) Faire le programme principal :  

```pseudo
Pour i ← 0 à N_epoch faire :
    Générer batch_réel ← 1/2 batch de données réelles
    Générer batch_faux ← 1/2 batch de données fausses

    # Entraînement du classifieur
    Entraîner(classifieur, batch_réel, epochs = 1)
    Entraîner(classifieur, batch_faux, epochs = 1)

    # Phase d'entraînement du GAN
    Rendre_paramètres(classifieur, entrainable = Faux)
    Entraîner(GAN, données = batch_faux, y_true = 1, epochs = 1)
    Rendre_paramètres(classifieur, entrainable = Vrai)
FinPour
```

**Paramètres** :
- Nepoch = 8000
- Taille d'un batch de données = 128
- On entrainera le GAN et le classifieur en utilisant la binary cross entropy comme fonction cout

Tous les 200 epochs, on générera 100 "fausses données" et on les représentera par des points dans le plan (y1, y2).  
Sur le même graphe, on représentera la courbe y2 = y1²