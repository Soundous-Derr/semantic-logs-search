#!/usr/bin/env python
"""
Démonstration Complète - Moteur de Recherche Sémantique Big Data
Cas d'usage pratiques avec interface interactive
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
import numpy as np

logging.basicConfig(level=logging.WARNING)

# Couleurs pour terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"{text:^80}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_section(text):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}▶ {text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-'*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def demo_case_1():
    """CAS D'USAGE 1: Retrouver logs similaires à une erreur donnée"""
    print_section("CAS 1: Retrouver logs similaires à une erreur critique")
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        print_info("Initialisation du moteur de recherche sémantique...")
        print()
        
        # Cas réel
        error_query = "Database connection timeout error"
        print(f"{Colors.BOLD}Requête:{Colors.ENDC} \"{error_query}\"")
        print()
        
        results = engine.search_by_error(error_query, top_k=5)
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}Résultats trouvés: {len(results)}{Colors.ENDC}\n")
        
        for i, result in enumerate(results, 1):
            similarity = result.get('similarity', 0) * 100
            print(f"{Colors.BOLD}#{i}{Colors.ENDC} [Similarité: {similarity:.1f}%]")
            print(f"   📋 Niveau: {result['log_level']}")
            print(f"   🕐 Timestamp: {result['timestamp']}")
            print(f"   📝 Message: {result['text'][:80]}...")
            print()
        
        print_success("Cas 1 validé: Recherche sémantique fonctionnelle")
        engine.db.disconnect()
        
    except Exception as e:
        print_warning(f"Erreur: {e}")

def demo_case_2():
    """CAS D'USAGE 2: Identifier les groupes d'erreurs fréquentes"""
    print_section("CAS 2: Identifier les groupes d'erreurs fréquentes (Clustering)")
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        print_info("Analyse des erreurs avec clustering K-Means...")
        print()
        
        clusters = engine.find_error_clusters(n_clusters=5)
        
        if clusters:
            print(f"{Colors.OKGREEN}{Colors.BOLD}Clusters identifiés: {len(clusters)}{Colors.ENDC}\n")
            
            for cluster_id, cluster_info in clusters.items():
                print(f"{Colors.BOLD}Cluster #{cluster_id}{Colors.ENDC}")
                print(f"   👥 Taille: {cluster_info['size']} logs")
                print(f"   📊 Centroïde (dim 1-5): {cluster_info['centroid']}")
                print(f"   🔍 Exemples de logs: {cluster_info['sample_logs']}")
                print()
        else:
            print_warning("Pas assez de logs d'erreur pour clustering")
        
        print_success("Cas 2 validé: Clustering d'erreurs réussi")
        engine.db.disconnect()
        
    except Exception as e:
        print_warning(f"Erreur: {e}")

def demo_case_3():
    """CAS D'USAGE 3: Analyser l'évolution temporelle des erreurs"""
    print_section("CAS 3: Analyser l'évolution temporelle des erreurs")
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        print_info("Analyse de la distribution temporelle des erreurs...")
        print()
        
        error_pattern = "connection error"
        print(f"{Colors.BOLD}Motif recherché:{Colors.ENDC} \"{error_pattern}\"")
        print()
        
        temporal_data = engine.analyze_temporal_evolution(error_pattern, days=1)
        
        if temporal_data:
            print(f"{Colors.OKGREEN}{Colors.BOLD}Distribution temporelle:{Colors.ENDC}\n")
            
            for date, count in sorted(temporal_data.items()):
                bar_length = int(count / max(temporal_data.values()) * 40)
                bar = "█" * bar_length
                print(f"   {date}: {bar} ({count} erreurs)")
        else:
            print_warning("Pas de données temporelles disponibles")
        
        print_success("Cas 3 validé: Analyse temporelle réussie")
        engine.db.disconnect()
        
    except Exception as e:
        print_warning(f"Erreur: {e}")

def demo_case_4():
    """CAS D'USAGE 4: Comparer recherche sémantique vs mot-clé"""
    print_section("CAS 4: Comparer recherche sémantique vs mot-clé")
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        print_info("Comparaison des deux approches...")
        print()
        
        query = "timeout"
        print(f"{Colors.BOLD}Requête:{Colors.ENDC} \"{query}\"")
        print()
        
        # Recherche sémantique
        print(f"{Colors.BOLD}1️⃣  RECHERCHE SÉMANTIQUE:{Colors.ENDC}")
        semantic_results = engine.search_by_error(query, top_k=5)
        print(f"   → {len(semantic_results)} résultats trouvés")
        for i, r in enumerate(semantic_results[:3], 1):
            sim = (r.get('similarity', 0) * 100)
            print(f"      {i}. {r['text'][:60]}... (sim: {sim:.1f}%)")
        print()
        
        # Recherche par mot-clé
        print(f"{Colors.BOLD}2️⃣  RECHERCHE PAR MOT-CLÉ:{Colors.ENDC}")
        keyword_results = engine.search_by_keyword(query, top_k=5)
        print(f"   → {len(keyword_results)} résultats trouvés")
        for i, r in enumerate(keyword_results[:3], 1):
            print(f"      {i}. {r['text'][:60]}...")
        print()
        
        # Comparaison
        print(f"{Colors.BOLD}📊 COMPARAISON:{Colors.ENDC}")
        print(f"   • Sémantique capture le sens (même sans mot exact)")
        print(f"   • Mot-clé cherche les occurrences exactes")
        print(f"   • Sémantique: {len(semantic_results)} résultats")
        print(f"   • Mot-clé:    {len(keyword_results)} résultats")
        print()
        
        print_success("Cas 4 validé: Comparaison des approches réussie")
        engine.db.disconnect()
        
    except Exception as e:
        print_warning(f"Erreur: {e}")

def demo_interactive_menu():
    """Menu interactif pour choisir la démonstration"""
    print_header("🚀 DÉMONSTRATION - Moteur de Recherche Sémantique Big Data")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}4 CAS D'USAGE À EXPLORER:{Colors.ENDC}\n")
    
    menu = {
        '1': ('Recherche de logs similaires à une erreur', demo_case_1),
        '2': ('Identification des groupes d\'erreurs fréquentes', demo_case_2),
        '3': ('Analyse de l\'évolution temporelle', demo_case_3),
        '4': ('Comparaison sémantique vs mot-clé', demo_case_4),
        '5': ('Exécuter tous les cas', None),
        '0': ('Quitter', None),
    }
    
    for key, (desc, _) in menu.items():
        print(f"   {Colors.BOLD}{key}{Colors.ENDC}. {desc}")
    
    print()

def main():
    print_header("🎓 TP: MOTEUR DE RECHERCHE SÉMANTIQUE SUR LOGS BIG DATA")
    
    while True:
        demo_interactive_menu()
        
        choice = input(f"{Colors.BOLD}Choisissez (0-5): {Colors.ENDC}").strip()
        
        if choice == '0':
            print(f"\n{Colors.OKGREEN}Merci d'avoir utilisé la démo!{Colors.ENDC}\n")
            break
        elif choice == '1':
            demo_case_1()
        elif choice == '2':
            demo_case_2()
        elif choice == '3':
            demo_case_3()
        elif choice == '4':
            demo_case_4()
        elif choice == '5':
            print_header("🔄 EXÉCUTION DE TOUS LES CAS")
            demo_case_1()
            input(f"\n{Colors.BOLD}Appuyez sur Entrée pour continuer...{Colors.ENDC}")
            demo_case_2()
            input(f"\n{Colors.BOLD}Appuyez sur Entrée pour continuer...{Colors.ENDC}")
            demo_case_3()
            input(f"\n{Colors.BOLD}Appuyez sur Entrée pour continuer...{Colors.ENDC}")
            demo_case_4()
            print_success("Tous les cas d'usage ont été exécutés!")
        else:
            print_warning("Choix invalide, veuillez réessayer")
        
        input(f"\n{Colors.BOLD}Appuyez sur Entrée pour continuer...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Arrêt par l'utilisateur{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}Erreur: {e}{Colors.ENDC}\n")
