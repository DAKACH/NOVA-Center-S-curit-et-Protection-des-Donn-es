# Guide d'Installation et Configuration

## Prérequis Système

### 1. Python
- **Version requise** : Python 3.8 ou supérieur
- **Téléchargement** : [python.org/downloads](https://www.python.org/downloads/)
- Lors de l'installation, cochez **"Add Python to PATH"**

### 2. Oracle Database
- **Version** : Oracle Database XE 21c (ou version compatible)
- **Téléchargement** : [Oracle Database XE](https://www.oracle.com/database/technologies/xe-downloads.html)
- **Oracle Instant Client** (si nécessaire) : [Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)

---

## Installation des Dépendances Python

Ouvrez un terminal (CMD ou PowerShell) et exécutez la commande suivante :

```bash
pip install flask flask-cors oracledb python-dotenv flask-limiter cryptography
```

### Liste des Bibliothèques

| Bibliothèque | Fonction |
|--------------|----------|
| `flask` | Framework web Python |
| `flask-cors` | Gestion des requêtes Cross-Origin (CORS) |
| `oracledb` | Connexion à Oracle Database |
| `python-dotenv` | Lecture des variables d'environnement (.env) |
| `flask-limiter` | Protection contre les attaques par force brute |
| `cryptography` | Chiffrement des données sensibles (emails) |

---

## Configuration du Fichier .env

Créez un fichier nommé `.env` dans le dossier `project/` avec le contenu suivant :

```env
ORACLE_USER=votre_utilisateur
ORACLE_PASSWORD=votre_mot_de_passe
ORACLE_DSN=localhost/XEPDB1
ENCRYPTION_KEY=votre_cle_de_chiffrement_32_caracteres
```

### Génération de la Clé de Chiffrement

Exécutez ce script Python pour générer une clé valide :

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Copiez la clé générée et collez-la dans `ENCRYPTION_KEY`.

---

## Configuration de la Base de Données Oracle

### Création de la Table

Connectez-vous à Oracle SQL*Plus et exécutez :

```sql
CREATE TABLE inscriptions (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom VARCHAR2(100) NOT NULL,
    email VARCHAR2(500) NOT NULL,
    message CLOB,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Lancement de l'Application

### Démarrer le Serveur Flask

```bash
cd project
python app.py
```

Le serveur sera accessible sur : **http://localhost:5000**

---

## Structure du Projet

```
project/
├── app.py              # Application Flask principale
├── backup.py           # Script de sauvegarde de la base de données
├── .env                # Variables d'environnement (à créer)
├── index.html          # Page d'accueil
├── contact.html        # Page de contact
├── formations.html     # Page des formations
├── apropos.html        # Page à propos
├── css/                # Fichiers de styles CSS
├── js/                 # Fichiers JavaScript
└── backups/            # Dossier des sauvegardes
```

---

## Utilisation du Script de Sauvegarde

```bash
# Créer une sauvegarde
python backup.py backup

# Lister les sauvegardes disponibles
python backup.py list

# Restaurer la dernière sauvegarde
python backup.py restore
```

---

## Résolution des Problèmes Courants

### Erreur de connexion Oracle
- Vérifiez que Oracle Database est en cours d'exécution
- Vérifiez les informations de connexion dans `.env`
- DSN typique : `localhost/XEPDB1` ou `localhost:1521/XEPDB1`

### Erreur "Module not found"
```bash
pip install --upgrade pip
pip install flask flask-cors oracledb python-dotenv flask-limiter cryptography
```

### Erreur de clé de chiffrement
- Assurez-vous que `ENCRYPTION_KEY` est une clé Fernet valide de 32 bytes encodée en base64

---

## Contact

Pour toute question technique, veuillez contacter l'équipe de développement.
