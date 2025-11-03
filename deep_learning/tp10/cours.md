# Les modèles de diffusion

## I) Le principe des modèles de diffusion

Les modèles de diffusion sont des modèles génératifs.  
L'idée est la suivante : on suppose qu'on a une image dont on bruite chaque pixel de sorte qu'à la fin du processus de bruitage, on obtienne une observation d'une v.a. de loi N(0, 1) pour chaque pixel.  
L'idée des modèles de diffusion est de construire un réseau de neurones qui permet de faire l'opérateur inverse de débruitage.  
L'opération de bruitage se fait en T étapes indicées par $t \in [0, T]$.  
On suppose qu'un pixel non bruité de l'image est x0.  
Les étapes de bruitage s'écrivent :  

$$
x_{t+1} \;=\; \sqrt{1-\beta_t}\,x_t \;+\; \sqrt{\beta_t}\,\varepsilon_{t+1} \tag{*}
$$

avec $\varepsilon_{t+1} \in N(0, 1)$  
$\varepsilon_{t}$ est un réel strictement positif qui prend des petites valeurs ($\varepsilon_{t} \in [10^{-4}, 0.02]$) et $\varepsilon_{t}$ croit linéairement avec t.  
On peut montrer que la formule (*) donne :  

$$
x_{t} \;=\; \sqrt{1-\overline{\alpha_t}}\,x_0 \;+\; \sqrt{\overline{\beta'_t}}\,\varepsilon_{t} \tag{**}
$$

avec $\overline{\beta'_t} \sim \mathcal{N}(0,1)$  
$$
\overline{\alpha_t} \;=\; \prod_{s=1}^{t} \alpha_s
$$
$$
\overline{\beta_t} = 1 - \overline{\alpha_t}
$$

## II) Processus de débruitage

On va entrainer un réseau de neurones pour que comparaissent $x_0, x_t$ et t il soit capable de calculer $\varepsilon'_{t}$

Pour générer la base de données, on tire au hasard un instant $t \in [0, T]$, on utilise toutes les images du dataset ($x_0$), on génère un nombre aléatoire 
avec $\varepsilon'_{t} \sim \mathcal{N}(0,1)$, et on applique la formule (**) qui permet d'isoler $\varepsilon'_{t}$ en fonction de $x_0, x_t$ et t.  

### <u>Time embedding :</u>  
$\forall t \in [0, 50]$ cette donnée d'entrée doit avoir la même importance.  
Donc on transforme cet entier en une valeur (ici de dimension 32).  

### <u>Le processus de débruitage :</u>  
On applique la formule (**) à t = t - 1 :  
$$
x_{t-1} \;=\; \sqrt{\overline{\alpha_{t-1}}}\,x_0 \;+\; \sqrt{\overline{\beta_{t-1}}}\,\varepsilon'_{t-1} \tag{***}
$$
$$
x_{t} \;=\; \sqrt{\overline{\alpha_{t}}}\,x_0 \;+\; \sqrt{\overline{\beta_{t}}}\,\varepsilon'_{t}
$$
$$
x_{0} \;=\; \frac{\alpha_{t} \;-\; \sqrt{\overline{\beta_{t}}}\,\varepsilon'_{t}}{\overline{\alpha_{t}}}
$$  
On remplace $\varepsilon'_{t}$ par son approximation $\varepsilon'_{t} (\theta)$ :
$$
x_{0} \;=\; \frac{x_{t} \;-\; \sqrt{\overline{\beta_{t}}}\,\varepsilon_{t}(\theta)}{\sqrt{\overline{\alpha_{t}}}}
$$  
$$
x_{0} \;=\; \sqrt{\overline{\alpha_{t-1}}}\,\frac{x_{t} \;-\; \sqrt{\overline{\beta_{t}}}\,\varepsilon_{t}(\theta, x_t, t)}{\sqrt{\overline{\alpha_{t}}}} + {\beta_{t-1}}\,\varepsilon'_{t-1} \tag{****}
$$  
C'est cette formule qui va permettre de débruiter une image.  


### <u>Codage :</u>(pour le débruitage)  
Générer 500 points (matrice de dimension 500x2) contenant des observations de v.a. iid de loi N(0, 1).  
Prendre T = 50 (50 pas de temps pour l'étape de débruitage).  
! Lorsque vous faites model_predict, ne pas oublier de normaliser t par $\frac{t}{T}$.  
Faire model_predict avec ($x_t$, $\frac{t}{T}$) en entrée pour estimer $\varepsilon_{t}(\theta, x_t, t)$.  
Appliquer la formule (****) T fois.  
On remplace $\varepsilon'_{t}$ par son approximation $\varepsilon_{t}(\theta)$ :
$$
x_{0} \;=\; \frac{x_{t} \;-\; \sqrt{\overline{\beta_{t}}}\,\varepsilon'_{t}(\theta)}{\sqrt{\overline{\alpha_{t}}}}
$$