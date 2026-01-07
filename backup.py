"""
🗄️ Sauvegarde de la base de données - Database Backup Script
==========================================================
Ce script permet de:
1. Se connecter à la base de données Oracle
2. Lire toutes les données de la table inscriptions
3. Les sauvegarder dans un fichier JSON avec date et heure
4. Restaurer les données depuis une sauvegarde

Utilisation:
    python backup.py backup    # Pour créer une sauvegarde
    python backup.py restore   # Pour restaurer la dernière sauvegarde
    python backup.py list      # Pour afficher les sauvegardes disponibles
"""

import oracledb
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# ============================================
# ✅ Étape 1: Charger les paramètres depuis .env
# ============================================
load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")

# Dossier de sauvegarde des backups
BACKUP_FOLDER = "backups"

# ============================================
# ✅ Étape 2: Fonction de connexion à la base de données
# ============================================
def get_connection():
    """Créer une connexion à la base de données Oracle"""
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )

# ============================================
# ✅ Étape 3: Fonction de création de sauvegarde
# ============================================
def create_backup():
    """
    Créer une sauvegarde de la table inscriptions
    Sauvegarde les données dans un fichier JSON avec date et heure
    """
    print("🔄 Création de la sauvegarde en cours...")
    
    try:
        # Connexion à la base de données
        conn = get_connection()
        cursor = conn.cursor()
        
        # Lire toutes les données
        cursor.execute("""
            SELECT id, nom, email, message, date_inscription 
            FROM inscriptions 
            ORDER BY id
        """)
        rows = cursor.fetchall()
        
        # Convertir les données en liste de dictionnaires (JSON-ready)
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'nom': row[1],
                'email': row[2],  # Sera chiffré
                'message': row[3].read() if row[3] else '',
                'date_inscription': str(row[4])
            })
        
        cursor.close()
        conn.close()
        
        # Créer le nom du fichier avec date et heure
        # Exemple: backup_2026-01-02_21-45-00.json
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"backup_{timestamp}.json"
        filepath = os.path.join(BACKUP_FOLDER, filename)
        
        # S'assurer que le dossier backups existe
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
        
        # Sauvegarder les données dans un fichier JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'backup_date': timestamp,
                'table_name': 'inscriptions',
                'record_count': len(data),
                'data': data
            }, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Sauvegarde créée avec succès!")
        print(f"📁 Fichier: {filepath}")
        print(f"📊 Nombre d'enregistrements: {len(data)}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return None

# ============================================
# ✅ Étape 4: Fonction d'affichage des sauvegardes disponibles
# ============================================
def list_backups():
    """Afficher toutes les sauvegardes disponibles"""
    print("📋 Sauvegardes disponibles:")
    print("-" * 50)
    
    if not os.path.exists(BACKUP_FOLDER):
        print("❌ Aucune sauvegarde trouvée")
        return []
    
    files = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.json')])
    
    if not files:
        print("❌ Aucune sauvegarde trouvée")
        return []
    
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(BACKUP_FOLDER, filename)
        size = os.path.getsize(filepath)
        
        # Lire les informations du fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_info = json.load(f)
        
        print(f"{i}. {filename}")
        print(f"   📅 Date: {backup_info['backup_date']}")
        print(f"   📊 Enregistrements: {backup_info['record_count']}")
        print(f"   💾 Taille: {size} bytes")
        print()
    
    return files

# ============================================
# ✅ Étape 5: Fonction de restauration de sauvegarde
# ============================================
def restore_backup(filename=None):
    """
    Restaurer les données depuis une sauvegarde
    Attention: les données actuelles seront supprimées!
    """
    print("🔄 Restauration de la sauvegarde en cours...")
    
    # Si aucun fichier n'est spécifié, utiliser la dernière sauvegarde
    if filename is None:
        files = sorted([f for f in os.listdir(BACKUP_FOLDER) if f.endswith('.json')])
        if not files:
            print("❌ Aucune sauvegarde à restaurer")
            return False
        filename = files[-1]  # Dernière sauvegarde
    
    filepath = os.path.join(BACKUP_FOLDER, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier inexistant: {filepath}")
        return False
    
    try:
        # Lire la sauvegarde
        with open(filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        print(f"📁 Restauration depuis: {filename}")
        print(f"📊 Nombre d'enregistrements: {backup_data['record_count']}")
        
        # Confirmation de l'utilisateur
        confirm = input("⚠️  Attention: les données actuelles seront supprimées! Voulez-vous continuer? (oui/non): ")
        if confirm.lower() not in ['oui', 'yes', 'y']:
            print("❌ Annulé")
            return False
        
        # Connexion à la base de données
        conn = get_connection()
        cursor = conn.cursor()
        
        # Supprimer les données actuelles
        cursor.execute("DELETE FROM inscriptions")
        
        # Insérer les données depuis la sauvegarde
        for record in backup_data['data']:
            cursor.execute("""
                INSERT INTO inscriptions (id, nom, email, message, date_inscription)
                VALUES (:1, :2, :3, :4, TO_TIMESTAMP(:5, 'YYYY-MM-DD HH24:MI:SS.FF'))
            """, (
                record['id'],
                record['nom'],
                record['email'],
                record['message'],
                record['date_inscription']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ {len(backup_data['data'])} enregistrements restaurés avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {e}")
        return False

# ============================================
# ✅ Étape 6: Fonction main - point d'entrée
# ============================================
def main():
    """
    Point d'entrée du script
    Accepte les commandes: backup, restore, list
    """
    print("=" * 50)
    print("🗄️  Système de sauvegarde - Database Backup System")
    print("=" * 50)
    
    # Lire la commande depuis la ligne de commande
    if len(sys.argv) < 2:
        print("\n📌 Utilisation:")
        print("   python backup.py backup   - Créer une sauvegarde")
        print("   python backup.py restore  - Restaurer la dernière sauvegarde")
        print("   python backup.py list     - Afficher les sauvegardes disponibles")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        create_backup()
    elif command == "restore":
        restore_backup()
    elif command == "list":
        list_backups()
    else:
        print(f"❌ Commande inconnue: {command}")
        print("Commandes disponibles: backup, restore, list")

# ============================================
# ✅ Exécution du script
# ============================================
if __name__ == "__main__":
    main()
