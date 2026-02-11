#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation simplifié - Lance les phases directement
"""

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire au chemin
sys.path.insert(0, str(Path(__file__).parent))

def print_header(text):
    """Affiche un en-tête"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def main():
    os.chdir(Path(__file__).parent)
    
    print_header("🚀 INITIALISATION - Moteur de Recherche Sémantique")
    
    # ÉTAPE 1: Créer les tables
    print_header("ÉTAPE 1: Créer les tables PostgreSQL")
    try:
        from src.database import VectorDatabase
        db = VectorDatabase()
        if not db.connect():
            print("❌ Impossible de se connecter à PostgreSQL")
            print("Vérifiez que PostgreSQL est lancé sur localhost:5432")
            return False
        
        if not db.create_tables():
            print("❌ Erreur création tables")
            return False
        
        print("✅ Tables créées avec succès")
        db.close()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # ÉTAPE 2: Phase 1 - Exploration
    print_header("ÉTAPE 2: Phase 1 - Exploration des données")
    try:
        os.system(f'"{Path(__file__).parent / "venv/Scripts/python.exe"}" main.py --phase 1')
        print("✅ Phase 1 complète")
    except Exception as e:
        print(f"⚠️  Phase 1 erreur: {e}")
    
    time.sleep(2)
    
    # ÉTAPE 3: Phase 2 - Ingestion
    print_header("ÉTAPE 3: Phase 2 - Ingestion Spark")
    try:
        os.system(f'"{Path(__file__).parent / "venv/Scripts/python.exe"}" main.py --phase 2')
        print("✅ Phase 2 complète")
    except Exception as e:
        print(f"⚠️  Phase 2 erreur: {e}")
    
    time.sleep(2)
    
    # ÉTAPE 4: Phase 3 - Vectorisation
    print_header("ÉTAPE 4: Phase 3 - Vectorisation")
    try:
        os.system(f'"{Path(__file__).parent / "venv/Scripts/python.exe"}" main.py --phase 3')
        print("✅ Phase 3 complète")
    except Exception as e:
        print(f"⚠️  Phase 3 erreur: {e}")
    
    time.sleep(2)
    
    # ÉTAPE 5: Vérifier le statut
    print_header("ÉTAPE 5: Vérification du statut")
    try:
        db = VectorDatabase()
        if db.connect():
            stats = db.get_statistics()
            print(f"✅ Logs en base: {stats.get('total_logs', 0)}")
            print(f"✅ Embeddings: {stats.get('total_embeddings', 0)}")
            db.close()
    except Exception as e:
        print(f"⚠️  Impossible vérifier stats: {e}")
    
    # ÉTAPE 6: Lancer la démo
    print_header("ÉTAPE 6: Lancement de la démonstration")
    print("\n✅ BASE DE DONNÉES PRÊTE!\n")
    time.sleep(1)
    
    try:
        os.system(f'"{Path(__file__).parent / "venv/Scripts/python.exe"}" demo_simple.py')
        return True
    except Exception as e:
        print(f"❌ Erreur démo: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print_header("🎉 INITIALISATION COMPLÈTE")
        print("La démonstration a été lancée!")
    else:
        print_header("❌ INITIALISATION ÉCHOUÉE")
        print("Vérifiez les erreurs ci-dessus")
        sys.exit(1)
