# Application web de gestion des bénévoles

## Description

Ce projet consiste à transformer un site web vitrine réalisé pour un
organisme à but non lucratif (OBNL) en une application web permettant de
gérer et de rechercher des candidats au bénévolat.

L'application propose une interface web en français ainsi que des
services REST permettant d'effectuer des opérations CRUD sur les
candidats au bénévolat. Elle offre également une fonctionnalité de
recherche asynchrone avec pagination.



## Fonctionnalités

### Site web vitrine

-   Présentation de l'organisme à but non lucratif.
-   Présentation de sa mission, de ses valeurs et de ses services.
-   Navigation entre les différentes sections du site.
-   Utilisation de HTML5, CSS3 et Bootstrap.
-   Présence de contenu textuel, d'images, de liens externes et d'un
    tableau.
-   Interface entièrement rédigée en français.

### Gestion des candidats au bénévolat

L'application expose des services REST permettant d'effectuer les
opérations suivantes :

-   **Create :** ajouter un candidat au bénévolat.
-   **Read :** consulter un ou plusieurs candidats.
-   **Update :** modifier les informations d'un candidat.
-   **Delete :** supprimer un candidat.

### Recherche de bénévoles

Une page dédiée permet de rechercher des candidats au bénévolat selon :

-   leur prénom ;
-   leur nom ;
-   les deux critères combinés.

Lorsque les deux critères sont vides, l'ensemble des candidats est
retourné.

Les résultats :

-   sont retournés sous la forme d'un tableau JSON par le service REST ;
-   sont affichés dans la même page ;
-   sont chargés de manière asynchrone avec JavaScript ;
-   ne nécessitent ni rafraîchissement de la page ni changement d'URL ;
-   sont paginés avec un maximum de **5 résultats par page**.

### Documentation et validation

-   Documentation des services REST en RAML.
-   Documentation disponible à la route `/api/doc`.
-   Validation des données JSON reçues par les services REST avec JSON
    Schema.
-   Code Python respectant les conventions PEP8.
-   Fichiers sources encodés en UTF-8.

## Technologies utilisées

### Front-end

-   HTML5
-   CSS3
-   Bootstrap
-   JavaScript

### Back-end

-   Python 3
-   Flask
-   Bibliothèques standards de Python
-   JSON Schema, selon l'implémentation utilisée dans le projet
-   RAML pour la documentation des services REST

> Les dépendances Python doivent être listées dans le fichier
> `requirements.txt`.

## Prérequis

Avant de lancer le projet, assurez-vous d'avoir installé :

-   Python 3
-   `pip`
-   Git

Il est recommandé d'utiliser un environnement virtuel Python.

## Installation

### 1. Cloner le projet

``` bash
git clone <URL_DU_REPOSITORY>
cd <NOM_DU_PROJET>
```

### 2. Créer un environnement virtuel

Sur macOS ou Linux :

``` bash
python3 -m venv venv
source venv/bin/activate
```

Sur Windows :

``` bash
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances

``` bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Si le projet utilise un fichier `.env`, créez-le à partir du modèle
fourni :

``` bash
cp .env.example .env
```

Adaptez ensuite les valeurs aux besoins de votre environnement local.

## Exécution de l'application

La commande de démarrage dépend de la structure du projet.

Exemple avec Flask :

``` bash
flask --app app run --debug
```

Ou, si le projet utilise un fichier de démarrage spécifique :

``` bash
python run.py
```

Une fois l'application démarrée, ouvrez l'adresse affichée dans le
terminal, généralement :

``` text
http://127.0.0.1:5000
```

## Documentation de l'API

La documentation RAML des services REST est disponible à l'adresse
suivante :

``` text
http://127.0.0.1:5000/api/doc
```

Les routes exactes de l'API dépendent de l'implémentation du projet.

Exemples de fonctionnalités couvertes :

  Opération   Description
  ----------- --------------------------------------------
  POST        Ajouter un candidat au bénévolat
  GET         Consulter les candidats
  PUT/PATCH   Modifier un candidat
  DELETE      Supprimer un candidat
  GET         Rechercher des candidats par nom et prénom

> Les méthodes HTTP et les chemins exacts doivent être ajustés pour
> correspondre aux routes réellement présentes dans l'application.

## Structure indicative du projet

``` text
projet/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── templates/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/
│
├── schemas/
│
├── docs/
│   └── api.raml
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py
```

Cette structure est indicative. Elle doit être adaptée à l'organisation
réelle du projet.

## Vérification de la qualité du code

Le code Python doit respecter les conventions PEP8.

Pour vérifier le code avec `pycodestyle` :

``` bash
pycodestyle .
```

L'objectif est de ne générer aucune erreur ni aucun avertissement sur
les fichiers Python concernés.

Si `pycodestyle` n'est pas installé dans l'environnement autorisé :

``` bash
pip install pycodestyle
```

> Installez uniquement les bibliothèques autorisées par les exigences du
> cours.

## Gestion des fichiers ignorés

Le fichier `.gitignore` doit notamment exclure les éléments générés
localement ou contenant des informations sensibles :

``` gitignore
venv/
.venv/
__pycache__/
*.py[cod]
.env
.idea/
*.iml
*.log
.DS_Store
```

Le fichier `requirements.txt`, le code source et la documentation du
projet doivent être conservés dans le dépôt Git.
