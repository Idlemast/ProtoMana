# ProtoMana — Projet ALSI61

Système de gestion de stock et de catalogue produits (Retail / E-commerce).

**Équipe :** WAN William · LO Hsiao-Wen-Paul · RAKOTOARIVELO Teddy

---

## Stack technique

| Composant       | Version                              |
| --------------- | ------------------------------------ |
| Python          | 3.10+                                |
| Django          | 6.0.5                                |
| Base de données | MySQL 8.0+                           |
| CSS             | Tailwind CSS 4 (via django-tailwind) |
| Driver MySQL    | PyMySQL                              |

---

## Prérequis

- Python 3.10 ou supérieur
- MySQL 8.0 ou supérieur (local ou distant)
- pip

> Node.js et npm ne sont **pas** requis, Tailwind est compilé via `pytailwindcss`.

---

## Installation

### 1. Dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Variables d'environnement

Soit copier ``.env`` ou changer ``.env.example`` en ``.env``

```bash
cp .env.example .env
```

Ouvrir `.env` et renseigner :

```env
DB_NAME=db_efrei_project
DEBUG=True
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 3. Base de données

```bash
# Pour créer la base de données et les migrations de Django
python manage.py createdb --drop
# Avec CMD uniquement, pas Powershell, pour insérer les données de script_creation.sql vers la base de données
mysql -u root -p db_efrei_project < script_creation.sql
```

### 6. Compiler le CSS

```bash
python manage.py tailwind build
```

### 7. Lancer l'application

```bash
# Développement hot reload CSS + serveur en un seul terminal
python manage.py dev

# OU deux terminaux séparés
python manage.py tailwind start    # terminal 1 — recompile CSS à chaque modif
python manage.py runserver         # terminal 2
```

Accéder à l'application : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Architecture

```
django_app/
├── config/               # Configuration Django (settings, urls)
│   ├── __init__.py       # Initialisation PyMySQL
│   ├── settings.py
│   └── urls.py
├── app/                  # Logique métier
│   ├── models.py         # 10 modèles ORM
│   ├── views.py          # ~45 vues CBV (CRUD + stats)
│   ├── forms.py          # 13 formulaires + TailwindFormMixin
│   ├── urls.py           # 48 routes
│   ├── admin.py          # Interface d'administration
│   └── management/
│       └── commands/
│           └── dev.py    # Commande `python manage.py dev`
├── templates/            # Templates HTML
│   ├── base.html
│   └── products/         # 16 templates
├── theme/                # App Tailwind CSS (django-tailwind)
│   └── static_src/src/
│       └── styles.css    # Point d'entrée CSS
├── script_creation.sql   # Schéma + données + triggers MySQL
├── requetes.sql          # 15 requêtes SQL d'exemple
├── requirements.txt
└── .env.example
```

---

## Fonctionnalités

| Module              | Fonctionnalités                                                                   |
| ------------------- | --------------------------------------------------------------------------------- |
| **Produits**        | CRUD, recherche AJAX (nom, description, catégorie, prix), filtre "Sans catégorie" |
| **SKU / Variantes** | CRUD, gestion inline depuis le formulaire produit                                 |
| **Stock**           | CRUD, ajustement direct depuis la fiche produit, redirection contextuelle         |
| **Catégories**      | CRUD hiérarchique (parent / enfant)                                               |
| **Lieux**           | CRUD, types : Store / Warehouse / Outlet                                          |
| **Commandes**       | CRUD complet, articles inline, calcul des totaux                                  |
| **Clients**         | CRUD, email unique                                                                |
| **Statistiques**    | KPI globaux, distribution par catégorie, top 5 prix, catégories stratégiques      |

---

## Commandes utiles

```bash
# Développement
python manage.py dev                  # tailwind start + runserver (un terminal)
python manage.py tailwind start       # recompilation CSS en watch mode
python manage.py runserver            # serveur Django seul

# Build
python manage.py tailwind build       # compile le CSS pour la production

# Base de données
python manage.py createdb                      # crée la base MySQL + migrate
python manage.py createdb --drop               # supprime et recrée la base + migrate
python manage.py createdb --drop --no-migrate  # supprime et recrée sans migrer
python manage.py migrate                       # applique les migrations
python manage.py migrate --fake-initial        # synchronise Django avec des tables déjà existantes
python manage.py makemigrations                # génère les migrations
```

---

## Base de données

Le schéma MySQL inclut :

- **4 triggers** : blocage stock négatif, prix auto sur `order_items`, vérification disponibilité avant commande, décrémentation stock au paiement
- **2 fonctions stockées** : `get_order_total(order_id)`, `get_total_stock(sku_id)`

---

## Développement

Les secrets restent **toujours** dans `.env`, jamais dans le code ni dans git.

Pour contribuer : modifier `app/views.py` pour les vues, `app/models.py` pour le schéma, `templates/` pour le rendu. Le CSS se recompile automatiquement en mode `dev`.
