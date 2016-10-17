### Lisibilité du code :
- Séparation des classes: deux lignes vides
- Séparation des methodes de class: une ligne vide
- Séparation des fonctions: deux lignes vides

### Documentation du code :
- Documenter les fonctions (paramètres, fonctionnement, ce qu'elle renvoie)
- Ne pas hésiter à laisser une ligne de commentaire dans le code, décrivant brièvement le fonctionnement d'algorithme plus compliqué/plus longs

### Nomenclature :
- Toutes les variables et msgid (traduction) sont écrites en minuscules avec un '_' (underscore) comme séparateur

### Réutilisation du code :
- Ne pas créer de fonctions qui renvoient plus d'un seul paramètre (perte de contrôle sur ce que fait la fonction et perte de réutilisation du code)
- Ne pas faire de copier/coller ; tout code dupliqué ou faisant la même chose doit être implémenté dans une fonction documentée qui est réutilisable
- Ne pas utiliser de 'magic_number' (constante non déclarée dans une variable). Par exemple, pas de -1, 1994, 2015 dans le code, mais déclarer en haut du fichier des variables sous la forme LIMIT_START_DATE=1994, LIMIT_END_DATE=2015, etc.

### Performance :
- Ne pas faire d'appel à la DB (pas de queryset) dans une boucle 'for' :
    - Récupérer toutes les données nécessaires en une seule requête avant d'effectuer des opérations sur les attributs renvoyés par le Queryset
    - Si la requête doit récupérer des données dans plusieurs tables, utiliser le select_related fourni par Django (https://docs.djangoproject.com/en/1.9/ref/models/querysets/#select-related)
    - Forcer l'évaluation du Queryset avant d'effectuer des récupération de données avec *list(a_queryset)* 

### Modèle :
- Chaque fichier décrivant un modèle doit se trouver dans le répertoire *'models'*
- Chaque fichier contenant une classe du modèle ne peut renvoyer que des instances du modèle qu'elle déclare. Autrement dit, un fichier my_model.py contient une classe MyModel() et des méthodes qui ne peuvent renvoyer que des records venant de MyModel
- Un modèle ne peut pas avoir un champs de type "ManyToMany" ; il faut toujours construire une table de liaison, qui contiendra les FK vers les modèles composant la relation ManyToMany.

### Vue :
- Ne pas faire appel à des méthodes de queryset dans les views (pas de MyModel.filter(...) ou MyModel.order_by() dans les vues). C'est la responsabilité du modèle d'appliquer des filtres et tris sur ses queryset. Il faut donc créer une fonction dans le modèle qui renvoie une liste de records filtrés sur base des paramètres entrés (find_by_(), search(), etc.).
- Ajouter les annotations pour sécuriser les méthodes dans les vues (user_passes_tests, login_required, require_permission)

### Formulaire :
- Utiliser les objets Forms fournis par Django (https://docs.djangoproject.com/en/1.9/topics/forms/)

### Sécurité :
- Ne pas laisser de données sensibles/privées dans les commentaires/dans le code
- Dans les URL (url.py), on ne peut jamais passer l'id d'une personne en paramètre (par ex. '?tutor_id' ou '/score_encoding/print/34' sont à éviter! ). 
- Dans le cas d'insertion/modification des données venant de l'extérieur (typiquement fichiers excels), s'assurer que l'utilisateur qui injecte des données a bien tous les droits sur ces données qu'il désire injecter. Cela nécessite une implémentation d'un code de vérification.

### Pull request :
- Ne fournir qu'un seul fichier de migration par issue/branche (fusionner tous les fichiers de migrations que vous avez en local en un seul fichier)

### Ressources et dépendances :
- Ne pas faire de référence à des librairie/ressources externes ; ajouter la librairie utilisée dans le dossier 'static'
