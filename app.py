from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import oracledb
import os
from dotenv import load_dotenv  
from flask_limiter import Limiter  
from flask_limiter.util import get_remote_address
from cryptography.fernet import Fernet  




load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)


limiter = Limiter(
    app=app,
    key_func=get_remote_address,  # Identifier l'utilisateur par IP
    default_limits=["200 per day", "50 per hour"]  # Limites par défaut
)

# ============================================
# 🛡️ Security Headers - En-têtes de sécurité
# ============================================
@app.after_request
def add_security_headers(response):
    """
    Ajouter des en-têtes de sécurité à chaque réponse HTTP
    Ces en-têtes protègent contre plusieurs attaques courantes
    """
    
    # 1️⃣ X-Content-Type-Options: nosniff
    # Empêche le navigateur de deviner le type de fichier (MIME sniffing)
    # Protection: empêcher l'exécution de fichiers malveillants comme JavaScript
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # 2️⃣ X-Frame-Options: DENY
    # Empêche l'affichage de votre site dans un iframe sur un autre site
    # Protection: attaques Clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # 3️⃣ X-XSS-Protection: 1; mode=block
    # Active la protection XSS intégrée au navigateur
    # Protection: attaques Cross-Site Scripting
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # 4️⃣ Referrer-Policy: strict-origin-when-cross-origin
    # Contrôle les informations du Referrer envoyées
    # Protection: fuite d'URLs sensibles
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # 5️⃣ Content-Security-Policy
    # Définit les sources de contenu autorisées
    # Protection: chargement de scripts/styles malveillants depuis des sites externes
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "                    # Par défaut: uniquement du même site
        "script-src 'self' 'unsafe-inline'; "     # JavaScript: du site + inline
        "style-src 'self' 'unsafe-inline'; "      # CSS: du site + inline
        "img-src 'self' https: data:; "           # Images: le site + HTTPS + data URLs
        "font-src 'self' https:; "                # Polices: le site + HTTPS
        "frame-ancestors 'none';"                  # Personne ne peut intégrer notre site
    )
    
    # 6️⃣ Permissions-Policy (anciennement Feature-Policy)
    # Contrôle les fonctionnalités du navigateur (caméra, microphone, etc.)
    response.headers['Permissions-Policy'] = (
        "geolocation=(), "      # Bloquer la géolocalisation
        "microphone=(), "       # Bloquer le microphone
        "camera=()"             # Bloquer la caméra
    )
    
    # 7️⃣ Cache-Control pour les pages dynamiques
    # Empêcher le stockage temporaire des données sensibles
    if request.endpoint and 'inscription' in str(request.endpoint):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    
    return response

# Route pour la page d'accueil
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Route pour les autres pages HTML
@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

# ✅ Configuration Oracle - Maintenant sécurisée!
# os.getenv() lit les valeurs du fichier .env

ORACLE_USER = os.getenv("ORACLE_USER")         # Lit ORACLE_USER depuis .env
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD") # Lit ORACLE_PASSWORD depuis .env
ORACLE_DSN = os.getenv("ORACLE_DSN")           # Lit ORACLE_DSN depuis .env

def get_connection():
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )

# ============================================
# ✅ Fonctions de chiffrement - Encryption Functions
# ============================================
# La clé secrète depuis le fichier .env
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

def get_cipher():
    """
    Créer un objet de chiffrement en utilisant la clé secrète
    Fernet = algorithme de chiffrement symétrique (même clé pour chiffrer et déchiffrer)
    """
    return Fernet(ENCRYPTION_KEY.encode())

def encrypt_email(email):
    """
    Chiffrer l'email
    Entrée: aya@gmail.com
    Sortie: gAAAAABh...xyz== (texte chiffré)
    """
    cipher = get_cipher()
    encrypted = cipher.encrypt(email.encode())  # Convertir le texte en bytes puis le chiffrer
    return encrypted.decode()  # Retourner le texte chiffré comme string

def decrypt_email(encrypted_email):
    
    """
    Déchiffrer l'email
    Entrée: gAAAAABh...xyz== (texte chiffré)
    Sortie: aya@gmail.com
    """
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_email.encode())  # Déchiffrer
    return decrypted.decode()  # Retourner le texte original

# ============================================
# ✅ Fonctions de validation des entrées
# ============================================
import re  # Bibliothèque pour les expressions régulières (Regex)

def validate_name(name):

    """
    Valider le nom
    - Doit être présent
    - Longueur entre 2 et 100 caractères
    - Contient uniquement des lettres (pas de chiffres ou symboles dangereux)
    """
    if not name or not isinstance(name, str):
        return False, "Le nom est requis"
    
    name = name.strip()  # Supprimer les espaces en trop
    
    if len(name) < 2:
        return False, "Le nom est trop court (minimum 2 caractères)"
    
    if len(name) > 100:
        return False, "Le nom est trop long (maximum 100 caractères)"
    
    # Seulement des lettres et espaces (arabes, français, anglais)
    if not re.match(r'^[\u0600-\u06FFa-zA-ZÀ-ÿ\s]+$', name):
        return False, "Le nom doit contenir uniquement des lettres"
    
    return True, name

def validate_email(email):
    
    """
    Valider l'email
    - Doit être dans un format correct: example@domain.com
    """
    if not email or not isinstance(email, str):
        return False, "L'email est requis"
    
    email = email.strip().lower()  # Nettoyer et convertir en minuscules
    
    # Pattern Regex pour vérifier le format de l'email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Le format de l'email est incorrect"
    
    if len(email) > 150:
        return False, "L'email est trop long"
    
    return True, email

def validate_message(message):
    """
    Valider le message
    - Optionnel mais s'il existe, il ne doit pas dépasser 1000 caractères
    """
    if not message:
        return True, ""  # Le message est optionnel
    
    if not isinstance(message, str):
        return False, "Le message doit être un texte"
    
    message = message.strip()
    
    if len(message) > 1000:
        return False, "Le message est trop long (maximum 1000 caractères)"
    
    return True, message

# Route pour recevoir les inscriptions
# ✅ Rate Limit: maximum 5 requêtes par minute par IP

@app.route('/inscription', methods=['POST'])
@limiter.limit("5 per minute")  # 🛡️ Protection contre les requêtes répétées
def inscription():
    try:
        data = request.json
        
        # ✅ Étape 1: Extraire les données
        nom_raw = data.get('name')
        email_raw = data.get('email')
        message_raw = data.get('message')
        
        # ✅ Étape 2: Valider chaque champ
        is_valid, nom = validate_name(nom_raw)
        if not is_valid:
            return jsonify({'success': False, 'message': nom}), 400  # 400 = Bad Request
        
        is_valid, email = validate_email(email_raw)
        if not is_valid:
            return jsonify({'success': False, 'message': email}), 400
        
        is_valid, message = validate_message(message_raw)
        if not is_valid:
            return jsonify({'success': False, 'message': message}), 400
        
        # ✅ Étape 3: Maintenant les données sont propres et sécurisées, on les sauvegarde
        conn = get_connection()
        cursor = conn.cursor()
        
        # 🔐 Étape 4: Chiffrer l'email avant de le sauvegarder
        encrypted_email = encrypt_email(email)
        
        cursor.execute(
            "INSERT INTO inscriptions (nom, email, message) VALUES (:1, :2, :3)",
            (nom, encrypted_email, message)  # ✅ On sauvegarde l'email chiffré
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Inscription réussie!'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route pour voir toutes les inscriptions
@app.route('/inscriptions', methods=['GET'])
def get_inscriptions():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, email, message, date_inscription FROM inscriptions ORDER BY date_inscription DESC")
        rows = cursor.fetchall()
        
        inscriptions = []
        for row in rows:
            # 🔐 Déchiffrer l'email avant de l'envoyer
            try:
                decrypted_email = decrypt_email(row[2])
            except:
                decrypted_email = row[2]  # Si non chiffré (anciennes données)
            
            inscriptions.append({
                'id': row[0],
                'nom': row[1],
                'email': decrypted_email,  # ✅ L'email original après déchiffrement
                'message': row[3].read() if row[3] else '',  # CLOB
                'date_inscription': str(row[4])
            })
        
        cursor.close()
        conn.close()
        return jsonify(inscriptions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Serveur Flask démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)
