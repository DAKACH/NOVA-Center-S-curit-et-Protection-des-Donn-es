-- ============================================
-- Base de données pour le projet d'inscription
-- Système de gestion des inscriptions sécurisé
-- ============================================

-- Suppression de la table si elle existe (optionnel)
-- DROP TABLE inscriptions;

-- Création de la table principale
CREATE TABLE inscriptions (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nom VARCHAR2(100) NOT NULL,
    email VARCHAR2(500) NOT NULL,
    message CLOB,
    date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Description des colonnes:
-- ============================================
-- id               : Identifiant unique auto-incrémenté
-- nom              : Nom de l'utilisateur (max 100 caractères)
-- email            : Email chiffré avec Fernet (max 500 car)
-- message          : Message optionnel (type CLOB pour texte long)
-- date_inscription : Date et heure d'inscription automatique

-- ============================================
-- Exemple d'insertion (pour test):
-- ============================================
-- INSERT INTO inscriptions (nom, email, message) 
-- VALUES ('Test User', 'test@example.com', 'Message de test');

-- ============================================
-- Requêtes utiles:
-- ============================================
-- Voir toutes les inscriptions:
-- SELECT * FROM inscriptions ORDER BY date_inscription DESC;

-- Compter les inscriptions:
-- SELECT COUNT(*) FROM inscriptions;
