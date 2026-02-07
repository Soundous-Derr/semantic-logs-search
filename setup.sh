#!/bin/bash

echo "🚀 Installation du projet Semantic Logs Search"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé"
    exit 1
fi

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer la structure des dossiers
echo "📁 Création des dossiers..."
mkdir -p data/raw data/processed data/logs
mkdir -p tests notebooks reports

# Démarrer PostgreSQL avec Docker
echo "🐳 Démarrage de PostgreSQL + pgvector..."
docker-compose up -d

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
sleep 10

# Créer le fichier .env
if [ ! -f .env ]; then
    echo "⚙️  Création du fichier .env..."
    cp .env.example .env
fi

echo "✅ Installation terminée!"
echo ""
echo "Prochaines étapes:"
echo "1. python download_data.py"
echo "2. python main.py --setup-only"
echo "3. python main.py"