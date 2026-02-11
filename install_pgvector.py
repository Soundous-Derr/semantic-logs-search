#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'installation de pgvector pour PostgreSQL 17 sur Windows
Solution rapide: télécharge et configure pgvector
"""

import os
import sys
import subprocess
import requests
import zipfile
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def download_pgvector_binary():
    """Télécharge les binaires précompilés de pgvector"""
    print_header("📥 Téléchargement des binaires pgvector")
    
    # URL des binaires pgvector pour PostgreSQL 17 (Windows)
    url = "https://github.com/pgvector/pgvector/releases/download/v0.7.4/pgvector-0.7.4-pg17-windows-x64.zip"
    
    try:
        print(f"⏳ Téléchargement depuis: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Sauvegarder
        zip_path = Path("pgvector.zip")
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Téléchargement complet: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"❌ Erreur téléchargement: {e}")
        return None

def extract_and_install(zip_path):
    """Extrait et installe pgvector dans PostgreSQL"""
    print_header("📦 Installation de pgvector")
    
    try:
        # Extraire
        print("⏳ Extraction des fichiers...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall()
        
        # Copier dans le répertoire PostgreSQL
        pg_path = Path("C:/Program Files/PostgreSQL/17")
        if not pg_path.exists():
            print(f"❌ PostgreSQL 17 non trouvé: {pg_path}")
            return False
        
        # Copier les fichiers
        print("⏳ Copie dans PostgreSQL...")
        for file in Path(".").glob("vector.*"):
            dest = pg_path / "lib" / file.name
            print(f"  Copie: {file.name} → {dest}")
            os.system(f'copy "{file}" "{dest}"')
        
        # Copier le fichier de contrôle
        for file in Path(".").glob("*.control"):
            dest = pg_path / "share/extension" / file.name
            print(f"  Copie: {file.name}")
            os.system(f'copy "{file}" "{dest}"')
        
        # Copier les scripts SQL
        for file in Path(".").glob("*.sql"):
            dest = pg_path / "share/extension" / file.name
            print(f"  Copie: {file.name}")
            os.system(f'copy "{file}" "{dest}"')
        
        print("✅ Installation terminée")
        return True
    except Exception as e:
        print(f"❌ Erreur installation: {e}")
        return False

def activate_extension():
    """Active l'extension pgvector dans PostgreSQL"""
    print_header("🔧 Activation de l'extension")
    
    try:
        psql_path = "C:\\Program Files\\PostgreSQL\\17\\bin\\psql.exe"
        cmd = f'"{psql_path}" -U postgres -d semantic_logs -c "CREATE EXTENSION IF NOT EXISTS vector;"'
        
        print(f"⏳ Exécution: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Extension pgvector activée!")
            return True
        else:
            print(f"⚠️  Erreur: {result.stderr}")
            print("Vous pouvez l'activer manuellement via pgAdmin")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print_header("🚀 Installation de pgvector pour PostgreSQL 17")
    print("Cet outil configure pgvector pour la recherche sémantique")
    
    # Option 1: Télécharger les binaires
    print("\n📋 Tentative 1: Téléchargement des binaires précompilés")
    zip_path = download_pgvector_binary()
    
    if zip_path and extract_and_install(zip_path):
        activate_extension()
        print_header("✅ pgvector installé avec succès!")
        return True
    
    # Option 2: Compilation manuelle
    print("\n" + "=" * 80)
    print("  Option 2: Compilation depuis les sources")
    print("=" * 80)
    print("\n⚠️  La compilation est complexe sur Windows.")
    print("Alternatives recommandées:")
    print("\n1. Utiliser le script: install_pgvector.ps1")
    print("   Pour compiler avec Visual Studio Build Tools")
    print("\n2. Utiliser pgAdmin 4 pour installer via GUI:")
    print("   Outils → Extensions")
    print("\n3. Télécharger PostgreSQL avec pgvector préinstallé:")
    print("   https://www.pgadmin.org/download/pgadmin-4-windows/")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n⚠️  Installation automatique échouée")
        print("Voir les alternatives ci-dessus")
        sys.exit(1)
