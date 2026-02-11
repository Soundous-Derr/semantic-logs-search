#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation et lancement de la démonstration
Lance toutes les phases nécessaires puis la démo
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def print_header(text):
    """Affiche un en-tête"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def run_command(cmd, description):
    """Exécute une commande et affiche le statut"""
    print(f"\n⏳ {description}...")
    try:
        # Utiliser le Python du venv
        python_exe = str(Path(__file__).parent / "venv" / "Scripts" / "python.exe")
        
        # Si cmd ne commence pas par 'python', ajouter le chemin python
        if not cmd.startswith('"'):
            full_cmd = f'"{python_exe}" {cmd}'
        else:
            full_cmd = cmd
        
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout:
                print(result.stdout[:500])
            return True
        else:
            print(f"❌ {description} - ERREUR")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    os.chdir(Path(__file__).parent)
    
    print_header("🚀 INITIALISATION DU PROJET - Moteur de Recherche Sémantique")
    
    # Étape 1: Créer les tables
    print("\n📋 ÉTAPE 1: Créer les tables PostgreSQL...")
    cmd = f'"{Path(__file__).parent / "venv/Scripts/python.exe"}" -c "from src.database import VectorDatabase; db = VectorDatabase(); db.connect(); db.create_tables(); db.close(); print(\'✅ Tables créées\')"'
    
    if not run_command(cmd, "Création des tables"):
        print("\n⚠️  Les tables n'ont pas pu être créées.")
        print("Vérifiez que PostgreSQL est lancé sur localhost:5432")
        return False
    
    # Étape 2: Phase 1 - Exploration
    print("\n" + "=" * 80)
    print("  ÉTAPE 2: Phase 1 - Exploration des données")
    print("=" * 80)
    if not run_command("python main.py --phase 1", "Phase 1 (Exploration)"):
        print("⚠️  Phase 1 échouée")
        return False
    
    # Étape 3: Phase 2 - Ingestion
    print("\n" + "=" * 80)
    print("  ÉTAPE 3: Phase 2 - Ingestion Spark")
    print("=" * 80)
    if not run_command("python main.py --phase 2", "Phase 2 (Ingestion)"):
        print("⚠️  Phase 2 échouée")
        return False
    
    # Vérifier qu'on a des données
    print("\n⏳ Vérification des données ingérées...")
    time.sleep(2)
    
    # Étape 4: Phase 3 - Vectorisation
    print("\n" + "=" * 80)
    print("  ÉTAPE 4: Phase 3 - Vectorisation")
    print("=" * 80)
    if not run_command("python main.py --phase 3", "Phase 3 (Vectorisation)"):
        print("⚠️  Phase 3 échouée")
        return False
    
    # Vérifier qu'on a des embeddings
    print("\n⏳ Vérification des embeddings...")
    time.sleep(2)
    
    # Étape 5: Vérifier le statut
    print("\n" + "=" * 80)
    print("  ÉTAPE 5: Vérification du statut")
    print("=" * 80)
    run_command("python check_status.py", "Vérification du statut")
    
    # Étape 6: Lancer la démo
    print("\n" + "=" * 80)
    print("  ÉTAPE 6: Lancement de la démonstration")
    print("=" * 80)
    print("\n✅ BASE DE DONNÉES PRÊTE - Lancement de la démo...\n")
    time.sleep(2)
    
    os.system("python demo_simple.py")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print_header("🎉 INITIALISATION COMPLÈTE")
        print("La démonstration a été lancée avec succès!")
    else:
        print_header("❌ INITIALISATION ÉCHOUÉE")
        print("Vérifiez les erreurs ci-dessus et relancez le script")
        sys.exit(1)
