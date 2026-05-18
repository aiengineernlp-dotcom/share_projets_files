-- ==============================================
-- FICHIER DE COMMANDES SQL
-- ==============================================
--
-- RÔLE PRINCIPAL :
-- --------------
-- Ce fichier phase1_sql_commands.sql contient les commandes SQL nécessaires
-- pour la phase 1 du projet. Il définit :
-- - La structure de la base de données
-- - Les tables et relations
-- - Les index et contraintes
-- - Les requêtes de base
--
-- RELATIONS AVEC LES AUTRES FICHIERS :
-- ---------------------------------
-- - storage/database.py : Gestion de la base de données
-- - storage/models.py : Modèles de données
-- - config/database_config.py : Configuration de la base
-- - data/* : Données à importer
--
-- STRUCTURE DU CONTENU :
-- --------------------
-- Le fichier est organisé en sections :
-- 1. Création des tables
-- 2. Définition des contraintes
-- 3. Création des index
-- 4. Insertion des données initiales
-- 5. Requêtes de base
-- 6. Fonctions et procédures
--
-- IMPORTANCE ET SUPPRESSION :
-- -------------------------
-- Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
-- - Il définit la structure de la base
-- - Il assure la cohérence des données
-- - Il est nécessaire pour l'installation
-- - Il contient les requêtes essentielles
--
-- NOTE DE MAINTENANCE :
-- -------------------
-- - Maintenir à jour avec les changements de schéma
-- - Vérifier la compatibilité des versions
-- - Optimiser les performances
-- - Documenter les modifications
--
-- ==============================================

-- Commandes SQL pour la Phase 1 du projet
-- Ce fichier contient toutes les commandes SQL nécessaires pour la manipulation des données de la Phase 1

-- 1. Création des tables principales
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    url TEXT,
    created_utc REAL,
    subreddit TEXT,
    author TEXT,
    category TEXT,
    second_opinion_score REAL,
    urgency_score REAL,
    medical_relevance_score REAL,
    sentiment_score REAL,
    overall_score REAL,
    country TEXT,
    city TEXT,
    region TEXT,
    latitude REAL,
    longitude REAL
);

-- 2. Création des index pour optimiser les recherches
CREATE INDEX IF NOT EXISTS idx_category ON posts(category);
CREATE INDEX IF NOT EXISTS idx_created_utc ON posts(created_utc);
CREATE INDEX IF NOT EXISTS idx_medical_score ON posts(medical_relevance_score);
CREATE INDEX IF NOT EXISTS idx_urgency ON posts(urgency_score);
CREATE INDEX IF NOT EXISTS idx_second_opinion ON posts(second_opinion_score);
CREATE INDEX IF NOT EXISTS idx_subreddit ON posts(subreddit);

-- 3. Requêtes d'analyse statistique
-- Nombre total de posts
SELECT COUNT(*) as total_posts FROM posts;

-- Distribution par catégorie
SELECT category, COUNT(*) as count
FROM posts
GROUP BY category
ORDER BY count DESC;

-- Distribution par subreddit
SELECT subreddit, COUNT(*) as count
FROM posts
GROUP BY subreddit
ORDER BY count DESC;

-- Posts avec score d'urgence élevé (>0.7)
SELECT id, title, urgency_score, medical_relevance_score
FROM posts
WHERE urgency_score > 0.7
ORDER BY urgency_score DESC;

-- Posts avec demande de deuxième avis (score > 0.5)
SELECT id, title, second_opinion_score, medical_relevance_score
FROM posts
WHERE second_opinion_score > 0.5
ORDER BY second_opinion_score DESC;

-- Distribution géographique
SELECT country, COUNT(*) as count
FROM posts
WHERE country IS NOT NULL
GROUP BY country
ORDER BY count DESC;

-- 4. Requêtes d'analyse temporelle
-- Distribution par mois
SELECT strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as month,
       COUNT(*) as count
FROM posts
GROUP BY month
ORDER BY month DESC;

-- 5. Requêtes d'analyse des scores
-- Moyenne des scores par catégorie
SELECT category,
       AVG(medical_relevance_score) as avg_medical_score,
       AVG(urgency_score) as avg_urgency_score,
       AVG(second_opinion_score) as avg_second_opinion_score
FROM posts
GROUP BY category;

-- 6. Requêtes de nettoyage et maintenance
-- Suppression des doublons
DELETE FROM posts
WHERE id IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (PARTITION BY title, body ORDER BY created_utc) as rn
        FROM posts
    )
    WHERE rn > 1
);

-- Mise à jour des scores nuls
UPDATE posts
SET medical_relevance_score = 0
WHERE medical_relevance_score IS NULL;

UPDATE posts
SET urgency_score = 0
WHERE urgency_score IS NULL;

UPDATE posts
SET second_opinion_score = 0
WHERE second_opinion_score IS NULL;

-- 7. Requêtes d'export pour analyse externe
-- Export des posts urgents
SELECT id, title, body, created_utc, category,
       medical_relevance_score, urgency_score, second_opinion_score
FROM posts
WHERE urgency_score > 0.7
ORDER BY urgency_score DESC;

-- Export des posts par catégorie
SELECT id, title, body, created_utc, category,
       medical_relevance_score, urgency_score, second_opinion_score
FROM posts
WHERE category = 'Standard Second Opinion'
ORDER BY created_utc DESC;

-- 8. Requêtes de validation des données
-- Vérification des posts sans contenu
SELECT id, title, created_utc
FROM posts
WHERE body IS NULL OR body = '';

-- Vérification des scores invalides
SELECT id, title, medical_relevance_score, urgency_score, second_opinion_score
FROM posts
WHERE medical_relevance_score < 0 OR medical_relevance_score > 1
   OR urgency_score < 0 OR urgency_score > 1
   OR second_opinion_score < 0 OR second_opinion_score > 1;

-- 9. Requêtes de statistiques avancées
-- Corrélation entre les scores
SELECT 
    AVG(medical_relevance_score * urgency_score) as correlation_medical_urgency,
    AVG(medical_relevance_score * second_opinion_score) as correlation_medical_second_opinion,
    AVG(urgency_score * second_opinion_score) as correlation_urgency_second_opinion
FROM posts;

-- Distribution des scores
SELECT 
    CASE 
        WHEN medical_relevance_score < 0.2 THEN '0-0.2'
        WHEN medical_relevance_score < 0.4 THEN '0.2-0.4'
        WHEN medical_relevance_score < 0.6 THEN '0.4-0.6'
        WHEN medical_relevance_score < 0.8 THEN '0.6-0.8'
        ELSE '0.8-1.0'
    END as score_range,
    COUNT(*) as count
FROM posts
GROUP BY score_range
ORDER BY score_range;

-- 10. Commandes SQL utilisées pour les questions spécifiques
-- Question: Nombre total de posts et leur catégorisation
SELECT 
    COUNT(*) as total_posts,
    SUM(CASE WHEN category = 'Standard Second Opinion' THEN 1 ELSE 0 END) as second_opinion_posts,
    SUM(CASE WHEN category = 'Quick Consultation Recommended' THEN 1 ELSE 0 END) as quick_consultation_posts
FROM posts;

-- Question: Distribution des posts par langue
SELECT 
    CASE 
        WHEN language = 'en' THEN 'Anglais'
        WHEN language = 'fr' THEN 'Français'
        WHEN language = 'ar' THEN 'Arabe'
        ELSE 'Autre'
    END as langue,
    COUNT(*) as nombre_posts
FROM posts
GROUP BY language
ORDER BY nombre_posts DESC;

-- Question: Posts les plus urgents avec détails
SELECT 
    id,
    title,
    body,
    urgency_score,
    medical_relevance_score,
    category,
    language,
    created_utc
FROM posts
WHERE urgency_score > 0.7
ORDER BY urgency_score DESC
LIMIT 10;

-- Question: Analyse des demandes de deuxième avis par spécialité
SELECT 
    category,
    COUNT(*) as nombre_demandes,
    AVG(urgency_score) as urgence_moyenne,
    AVG(medical_relevance_score) as pertinence_moyenne
FROM posts
WHERE second_opinion_score > 0.5
GROUP BY category
ORDER BY nombre_demandes DESC;

-- Question: Distribution temporelle des demandes de deuxième avis
SELECT 
    strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as mois,
    COUNT(*) as nombre_posts,
    AVG(urgency_score) as urgence_moyenne
FROM posts
WHERE second_opinion_score > 0.5
GROUP BY mois
ORDER BY mois DESC;

-- Question: Analyse des scores de pertinence par subreddit
SELECT 
    subreddit,
    COUNT(*) as nombre_posts,
    AVG(medical_relevance_score) as pertinence_moyenne,
    AVG(urgency_score) as urgence_moyenne
FROM posts
GROUP BY subreddit
HAVING COUNT(*) > 5
ORDER BY pertinence_moyenne DESC;

-- Question: Identification des cas complexes (scores élevés sur plusieurs critères)
SELECT 
    id,
    title,
    medical_relevance_score,
    urgency_score,
    second_opinion_score,
    category
FROM posts
WHERE medical_relevance_score > 0.7
    AND urgency_score > 0.7
    AND second_opinion_score > 0.7
ORDER BY (medical_relevance_score + urgency_score + second_opinion_score) DESC;

-- Question: Analyse des tendances par période
SELECT 
    strftime('%Y-%m-%d', datetime(created_utc, 'unixepoch')) as date,
    COUNT(*) as nombre_posts,
    AVG(urgency_score) as urgence_moyenne,
    AVG(second_opinion_score) as deuxieme_avis_moyen
FROM posts
GROUP BY date
ORDER BY date DESC
LIMIT 30;

-- Question: Distribution géographique des demandes de deuxième avis
SELECT 
    country,
    COUNT(*) as nombre_demandes,
    AVG(urgency_score) as urgence_moyenne
FROM posts
WHERE second_opinion_score > 0.5
    AND country IS NOT NULL
GROUP BY country
ORDER BY nombre_demandes DESC;

-- Question: Analyse des corrélations entre les différents scores
SELECT 
    AVG(medical_relevance_score * urgency_score) as correlation_medical_urgence,
    AVG(medical_relevance_score * second_opinion_score) as correlation_medical_deuxieme_avis,
    AVG(urgency_score * second_opinion_score) as correlation_urgence_deuxieme_avis
FROM posts
WHERE medical_relevance_score > 0.5; 