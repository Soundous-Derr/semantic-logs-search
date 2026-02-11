#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Installation directe de pgvector pour PostgreSQL 17 Windows
Télécharge les binaires depuis les releases GitHub
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import urllib.request
import zipfile

def print_step(step, text):
    print(f"\n{'='*80}")
    print(f"  {step}. {text}")
    print('='*80)

def download_file(url, filename):
    """Télécharge un fichier"""
    print(f"⏳ Téléchargement: {url}")
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"✅ Téléchargé: {filename}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def install_pgvector():
    """Installe pgvector pour PostgreSQL 17"""
    
    print("\n" + "="*80)
    print("  🚀 INSTALLATION DIRECTE DE PGVECTOR")
    print("="*80)
    
    # Chemins
    pg_root = Path("C:/Program Files/PostgreSQL/17")
    pg_lib = pg_root / "lib"
    pg_share = pg_root / "share/extension"
    
    # Vérifier PostgreSQL
    print_step(1, "Vérification de PostgreSQL 17")
    if not pg_root.exists():
        print(f"❌ PostgreSQL 17 non trouvé: {pg_root}")
        return False
    print(f"✅ PostgreSQL 17 trouvé: {pg_root}")
    
    # Solution 1: Chercher pgvector compilé localement
    print_step(2, "Recherche de pgvector préinstallé")
    
    local_vectors = list(pg_lib.glob("vector*.dll"))
    if local_vectors:
        print(f"✅ Trouvé: {local_vectors}")
        return activate_extension()
    
    print("❌ pgvector non trouvé en local")
    
    # Solution 2: Télécharger depuis GitHub Releases
    print_step(3, "Téléchargement des binaires pgvector")
    
    work_dir = Path(".")
    os.chdir(work_dir)
    
    # URL directe des assets pgvector v0.7.4 pour PostgreSQL 17
    # Ces URLs pointent vers les fichiers individuels
    files_to_download = [
        ("https://github.com/pgvector/pgvector/releases/download/v0.7.4/vector.control", "vector.control"),
        ("https://github.com/pgvector/pgvector/releases/download/v0.7.4/vector.sql", "vector--0.7.4.sql"),
    ]
    
    downloaded = True
    for url, filename in files_to_download:
        print(f"\n⏳ Téléchargement: {filename}")
        if download_file(url, filename):
            print(f"✅ {filename} téléchargé")
        else:
            print(f"⚠️  Impossible de télécharger {filename}")
            downloaded = False
    
    if not downloaded:
        print("\n❌ Les fichiers SQL ne pourraient pas être téléchargés")
        print("Essayez une autre approche...")
        return False
    
    # Installer les fichiers SQL
    print_step(4, "Installation des fichiers SQL")
    
    try:
        for local_file in Path(".").glob("vector*"):
            if local_file.suffix in [".control", ".sql"]:
                dest = pg_share / local_file.name
                print(f"⏳ Copie: {local_file.name} → {dest}")
                shutil.copy(local_file, dest)
                print(f"✅ Copié")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # Chercher DLL pgvector
    print_step(5, "Installation de la DLL pgvector")
    
    dll_names = ["vector.dll", "vector-0.7.4.dll", "vector.so"]
    for dll_name in dll_names:
        dll_url = f"https://github.com/pgvector/pgvector/releases/download/v0.7.4/{dll_name}"
        if download_file(dll_url, dll_name):
            dest = pg_lib / dll_name
            try:
                shutil.copy(dll_name, dest)
                print(f"✅ DLL installée: {dest}")
                break
            except Exception as e:
                print(f"⚠️  Impossible de copier {dll_name}: {e}")
    
    # Activer l'extension
    return activate_extension()

def activate_extension():
    """Active l'extension pgvector dans PostgreSQL"""
    print_step(6, "Activation de l'extension pgvector")
    
    try:
        psql_path = Path("C:/Program Files/PostgreSQL/17/bin/psql.exe")
        
        # Créer la base de données si nécessaire
        print("⏳ Création de la base de données (si nécessaire)...")
        cmd = f'"{psql_path}" -U postgres -c "CREATE DATABASE IF NOT EXISTS semantic_logs;"'
        subprocess.run(cmd, shell=True, capture_output=True)
        
        # Activer pgvector
        print("⏳ Activation de pgvector...")
        cmd = f'"{psql_path}" -U postgres -d semantic_logs -c "CREATE EXTENSION IF NOT EXISTS vector;"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Extension pgvector activée!")
            return True
        else:
            print(f"⚠️  Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = install_pgvector()
    
    print("\n" + "="*80)
    if success:
        print("  ✅ PGVECTOR INSTALLÉ AVEC SUCCÈS!")
        print("="*80)
        print("\n➡️  Continuez avec:")
        print("   python SETUP_AND_RUN.py")
        sys.exit(0)
    else:
        print("  ❌ INSTALLATION ÉCHOUÉE")
        print("="*80)
        print("\n📋 Alternatives:")
        print("   1. Utiliser pgAdmin 4 GUI (plus simple)")
        print("   2. Installer manuellement depuis: https://pgvector.org")
        print("   3. Utiliser une base de données alternative (database_alternative.py)")
        sys.exit(1)
