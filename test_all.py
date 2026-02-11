#!/usr/bin/env python
"""
Scripts de test rapides - Sans interface, juste les résultats
Idéal pour vérifier que tout fonctionne avant la présentation
"""

import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR)

def test_database_connection():
    """Tester la connexion à PostgreSQL"""
    print("=" * 80)
    print("TEST 1: Connexion PostgreSQL")
    print("=" * 80)
    
    from src.database import VectorDatabase
    
    db = VectorDatabase()
    if db.connect():
        stats = db.get_statistics()
        print(f"✅ Connexion réussie!")
        print(f"   - Logs en base: {stats['total_logs']:,}")
        print(f"   - Embeddings: {stats['total_embeddings']:,}")
        db.disconnect()
        return True
    else:
        print("❌ Connexion échouée!")
        return False

def test_semantic_search():
    """Tester la recherche sémantique"""
    print("\n" + "=" * 80)
    print("TEST 2: Recherche Sémantique")
    print("=" * 80)
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        # Test avec requête classique
        results = engine.search_by_error("Database connection timeout", top_k=3)
        
        if results:
            print(f"✅ Recherche réussie! {len(results)} résultats")
            for i, r in enumerate(results, 1):
                sim = r.get('similarity', 0) * 100
                print(f"   {i}. [Sim: {sim:.1f}%] {r['text'][:60]}...")
            return True
        else:
            print("❌ Aucun résultat")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_clustering():
    """Tester le clustering"""
    print("\n" + "=" * 80)
    print("TEST 3: Clustering K-Means")
    print("=" * 80)
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        clusters = engine.find_error_clusters(n_clusters=3)
        
        if clusters:
            print(f"✅ Clustering réussi! {len(clusters)} clusters")
            total = sum(c['size'] for c in clusters.values())
            for cid, info in clusters.items():
                print(f"   Cluster {cid}: {info['size']} logs")
            print(f"   Total: {total} logs d'erreur")
            return True
        else:
            print("❌ Clustering échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_temporal_analysis():
    """Tester l'analyse temporelle"""
    print("\n" + "=" * 80)
    print("TEST 4: Analyse Temporelle")
    print("=" * 80)
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        temporal_data = engine.analyze_temporal_evolution("error", days=1)
        
        if temporal_data:
            print(f"✅ Analyse réussie! {len(temporal_data)} jours analysés")
            for date, count in temporal_data.items():
                bar = "█" * (count // 100)
                print(f"   {date}: {bar} ({count} erreurs)")
            return True
        else:
            print("❌ Pas de données")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_keyword_search():
    """Tester la recherche par mot-clé"""
    print("\n" + "=" * 80)
    print("TEST 5: Recherche par Mot-clé")
    print("=" * 80)
    
    from src.semantic_search import SemanticSearchEngine
    
    try:
        engine = SemanticSearchEngine()
        
        results = engine.search_by_keyword("timeout", top_k=3)
        
        if results:
            print(f"✅ Recherche réussie! {len(results)} résultats")
            for i, r in enumerate(results, 1):
                print(f"   {i}. {r['text'][:60]}...")
            return True
        else:
            print("❌ Aucun résultat")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n" + "🧪 SUITE DE TESTS - Moteur de Recherche Sémantique\n")
    
    results = []
    
    # Test 1
    results.append(("Connexion DB", test_database_connection()))
    
    # Test 2
    results.append(("Recherche sémantique", test_semantic_search()))
    
    # Test 3
    results.append(("Clustering", test_clustering()))
    
    # Test 4
    results.append(("Analyse temporelle", test_temporal_analysis()))
    
    # Test 5
    results.append(("Recherche mot-clé", test_keyword_search()))
    
    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES TESTS")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30s} {status}")
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés! Prêt pour la présentation.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) échoué(s)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
