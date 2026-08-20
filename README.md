# FSB-System — Système d'Information de la Faculté des Sciences de Bizerte

**FSB-System** est une plateforme de gestion administrative universitaire développée pour la **Faculté des Sciences de Bizerte (FSB)**. Le système est conçu comme un outil **admin-only** : les étudiants et enseignants sont gérés comme des entités de données au sein de la plateforme, et non comme des utilisateurs du système.

Ce projet a été réalisé dans le cadre d'un **Projet de Fin d'Année (PFA)**.

---

## 📋 Description

FSB-System centralise l'ensemble des opérations administratives d'une faculté universitaire : gestion des étudiants et enseignants, matières, emplois du temps, absences, notes et moyennes, sessions d'examens, stages, diplômes, et génération de documents officiels. Le système intègre également un **assistant conversationnel multi-agents** basé sur l'API Groq (modèles Llama), capable de répondre à des questions administratives et pédagogiques et d'exécuter directement certaines opérations métier (inscriptions, validations, calculs d'élimination par absences, etc.).

---

## ✨ Fonctionnalités principales

- **Gestion des étudiants et enseignants** — fiches détaillées, navigation par département → filière → classe
- **Gestion des matières (matières)** — affectation aux filières et enseignants
- **Emploi du temps** — grille hebdomadaire interactive avec séances colorées et ajout via modale
- **Absences** — suivi justifié/non justifié, règle d'élimination automatique au seuil de **25 %**
- **Notes et moyennes** — saisie et calcul des moyennes par étudiant/matière
- **Sessions d'examens** — planification et suivi des sessions courantes et futures
- **Stages** — gestion des demandes de stage (statuts multiples : en attente, acceptée, refusée)
- **Diplômes** — génération avec mentions automatiques, recherche, aperçu en temps réel
- **Documents officiels** — attestations et relevés de notes avec QR code et signature
- **Assistant IA multi-agents** — interface de chat unifiée avec routage intelligent vers 5 agents spécialisés :
  | Agent | Rôle |
  |---|---|
  | **Admin** | Questions administratives générales |
  | **Pédagogique** | Informations sur matières, notes, emplois du temps |
  | **Stages** | Informations et suivi des demandes de stage |
  | **Statistiques** | Requêtes analytiques et chiffres clés |
  | **Action** | Opérations réelles en base de données (inscription, validation, calculs) |

---

## 🛠️ Stack technique

- **Backend** : Python 3.12, Django
- **Base de données** : SQLite (choix intentionnel pour un contexte académique mono-utilisateur ; migration vers PostgreSQL possible sans changement de l'ORM)
- **Frontend** : Bootstrap 5, templates Django
- **IA** : API Groq — `llama-3.1-8b-instant` (routage, sorties structurées JSON) et `llama-3.3-70b-versatile` (réponses pédagogiques en français)

---

## 📁 Structure du projet

```

├───accounts
├───administration
├───ai_agents
├───examens
├───fsb_system
├───pedagogie
├───stages
├───static
│   ├───css
│   ├───images
│   └───js
└───templates
|   ├───accounts
|   ├───administration
|   │   ├───enseignants
|   │   └───etudiants
|   ├───ai_agents
|   ├───examens
|   ├───pedagogie
|   │   ├───absences
|   │   ├───edt
|   │   ├───matieres
|   │   └───notes
|   └───stages
├── manage.py
├── fsb_pfa/                 # Configuration du projet Django
│   ├── settings.py
│   ├── urls.py
└── requirements.txt

```

---

## 🚀 Installation

### Prérequis

- Python 3.12+
- pip
- Une clé API [Groq](https://console.groq.com/)

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/<votre-utilisateur>/FSB-System.git
cd FSB-System

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Ajouter votre GROQ_API_KEY dans le fichier fsb_system/settings.py

# 4. Appliquer les migrations
python manage.py migrate

# 5. Lancer le serveur
python manage.py runserver
```

L'application est ensuite accessible sur `http://127.0.0.1:8000/`.
Vous pouvez utiliser respectivement **admin** et **admin** comme identifiant d’utilisateur et mot de passe lors de l’authentification.

---

## 🗄️ Base de données

Le projet utilise **SQLite** par défaut, adapté à un contexte de prototype académique mono-utilisateur. Pour migrer vers **PostgreSQL** en production :

1. Installer `psycopg2-binary`
2. Mettre à jour `DATABASES` dans `settings.py`
3. Relancer les migrations

Aucun changement au niveau du modèle ORM n'est nécessaire.

---

## 🤖 Assistant IA

L'assistant utilise un **routeur interne** qui analyse chaque requête de l'utilisateur et la dirige vers l'agent spécialisé approprié. Les agents informationnels (Admin, Pédagogique, Stages, Statistiques) répondent en langage naturel français, tandis que l'agent **Action** exécute directement des opérations sur la base de données (avec confirmation de l'utilisateur avant toute action sensible).

---

## 👤 Auteurs
Ce projet est un travail de groupe qui a été développé dans un cadre académique.

Développé par **AYA** — Projet de Fin d'Année (PFA), Faculté des Sciences de Bizerte.
