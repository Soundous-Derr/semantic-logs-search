"""
Phase 4: Recherche sémantique et analyse avancée
"""

from database import VectorDatabase
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from typing import List, Dict
import numpy as np
import logging
from utils import get_logger

logger = get_logger(__name__)

class SemanticSearchEngine:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """Initialise le moteur de recherche sémantique"""
        self.db = VectorDatabase()
        self.model = SentenceTransformer(model_name)
        self.db.connect()
    
    def search_by_error(self, error_description: str, top_k: int = 10) -> List[Dict]:
        """Cas d'usage 1: Retrouver tous les logs similaires à une erreur donnée"""
        print(f"\n🔍 Recherche sémantique pour: '{error_description}'")
        
        query_embedding = self.model.encode(error_description)
        results = self.db.semantic_search(query_embedding.tolist(), top_k=top_k, threshold=0.5)
        
        print(f"✓ {len(results)} logs similaires trouvés:")
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. [Similarité: {result['similarity']:.2%}]")
            print(f"     Level: {result['log_level']}")
            print(f"     Texte: {result['text'][:100]}...")
        
        return results
    
    def find_error_clusters(self, n_clusters: int = 10) -> Dict:
        """Cas d'usage 2: Identifier les groupes d'erreurs fréquentes"""
        print(f"\n👥 Clustering des erreurs (k={n_clusters})...")
        
        query = """
        SELECT l.id, le.embedding, l.original_text, l.log_level
        FROM log_embeddings le
        JOIN logs l ON le.log_id = l.id
        WHERE l.log_level = 'ERROR'
        LIMIT 10000
        """
        
        self.db.cursor.execute(query)
        results = self.db.cursor.fetchall()
        
        if not results:
            logger.warning("Aucun log d'erreur trouvé")
            return {}
        
        log_ids = [row[0] for row in results]
        embeddings = np.array([np.fromstring(str(row[1]), sep=',') for row in results])
        
        kmeans = KMeans(n_clusters=min(n_clusters, len(results)), random_state=42)
        kmeans.fit(embeddings)
        
        clusters = {}
        for cluster_id in range(len(set(kmeans.labels_))):
            mask = kmeans.labels_ == cluster_id
            cluster_logs = [log_ids[i] for i, m in enumerate(mask) if m]
            clusters[cluster_id] = {
                'size': len(cluster_logs),
                'centroid': kmeans.cluster_centers_[cluster_id].tolist(),
                'logs': cluster_logs[:5]
            }
        
        print(f"\n✓ {len(clusters)} clusters identifiés:")
        for cluster_id, info in clusters.items():
            print(f"  Cluster {cluster_id}: {info['size']} logs")
        
        return clusters
    
    def temporal_analysis(self, error_pattern: str, timeframe_days: int = 7) -> Dict:
        """Cas d'usage 3: Analyser l'évolution temporelle des erreurs similaires"""
        print(f"\n📅 Analyse temporelle (derniers {timeframe_days} jours)...")
        
        query_embedding = self.model.encode(error_pattern)
        results = self.db.semantic_search(query_embedding.tolist(), top_k=1000, threshold=0.5)
        
        if not results:
            logger.warning("Aucun log trouvé pour ce pattern")
            return {}
        
        temporal_data = {}
        for result in results:
            timestamp = result.get('timestamp', 'unknown')
            if timestamp:
                temporal_data[timestamp] = temporal_data.get(timestamp, 0) + 1
        
        print(f"\n✓ Distribution temporelle:")
        for timestamp, count in sorted(temporal_data.items())[:10]:
            print(f"  {timestamp}: {count} erreurs")
        
        return temporal_data
    
    def compare_with_keyword_search(self, query: str, top_k: int = 10) -> Dict:
        """Compare recherche sémantique vs recherche par mots-clés"""
        print(f"\n🔬 Comparaison: Sémantique vs Mot-clé")
        print(f"   Requête: '{query}'")
        
        query_embedding = self.model.encode(query)
        semantic_results = self.db.semantic_search(query_embedding.tolist(), top_k=top_k)
        
        semantic_ids = set(r['id'] for r in semantic_results)
        
        print(f"\n✓ Résultats:")
        print(f"  Recherche sémantique: {len(semantic_results)} résultats")
        print(f"  Top résultats: {len(semantic_ids)}")
        
        return {
            'semantic': semantic_results,
            'count': len(semantic_results)
        }
    
    def close(self):
        """Ferme la connexion à la base"""
        self.db.disconnect()


def run_demo():
    """Démo des 4 cas d'usage"""
    
    engine = SemanticSearchEngine()
    
    print("\n" + "="*70)
    print("🚀 DÉMONSTRATION - RECHERCHE SÉMANTIQUE")
    print("="*70)
    
    print("\n" + "-"*70)
    print("📌 CAS 1: Retrouver logs similaires à une erreur donnée")
    print("-"*70)
    engine.search_by_error("Database connection timeout error", top_k=5)
    
    print("\n" + "-"*70)
    print("📌 CAS 2: Identifier les groupes d'erreurs fréquentes")
    print("-"*70)
    clusters = engine.find_error_clusters(n_clusters=5)
    
    print("\n" + "-"*70)
    print("📌 CAS 3: Analyser l'évolution des erreurs")
    print("-"*70)
    engine.temporal_analysis("connection error", timeframe_days=7)
    
    print("\n" + "-"*70)
    print("📌 CAS 4: Comparer recherche sémantique vs mot-clé")
    print("-"*70)
    comparison = engine.compare_with_keyword_search("timeout", top_k=5)
    
    engine.close()


if __name__ == "__main__":
    run_demo()