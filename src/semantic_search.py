"""
Phase 4: Recherche sémantique et analyse avancée
"""

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from typing import List, Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class SemanticSearchEngine:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """Initialise le moteur de recherche sémantique"""
        from src.database import VectorDatabase
        
        self.db = VectorDatabase()
        self.model = SentenceTransformer(model_name)
        if not self.db.connect():
            raise ConnectionError("Impossible de se connecter à la base de données")
    
    def search_by_error(self, error_description: str, top_k: int = 10) -> List[Dict]:
        """Cas d'usage 1: Retrouver tous les logs similaires à une erreur donnée"""
        print(f"\n🔍 Recherche sémantique pour: '{error_description}'")
        
        query_embedding = self.model.encode(error_description)
        results = self.db.semantic_search(query_embedding.tolist(), top_k=top_k, threshold=0.3)
        
        print(f"✓ {len(results)} logs similaires trouvés:")
        for i, result in enumerate(results[:5], 1):
            print(f"\n  {i}. [Similarité: {result['similarity']:.2%}]")
            print(f"     Level: {result['log_level']}")
            print(f"     Texte: {result['text'][:100]}...")
        
        return results
    
    def find_error_clusters(self, n_clusters: int = 5) -> Dict:
        """Cas d'usage 2: Identifier les groupes d'erreurs fréquentes"""
        print(f"\n👥 Clustering des erreurs (k={n_clusters})...")
        
        query = """
        SELECT l.id, le.embedding, l.original_text, l.log_level
        FROM log_embeddings le
        JOIN logs l ON le.log_id = l.id
        WHERE l.log_level IN ('ERROR', 'CRITICAL', 'FATAL')
        LIMIT 5000
        """
        
        try:
            self.db.cursor.execute(query)
            results = self.db.cursor.fetchall()
            
            if not results or len(results) < n_clusters:
                logger.warning("Pas assez de logs d'erreur pour le clustering")
                return {}
            
            log_ids = [row[0] for row in results]
            # Parser le format vector de PostgreSQL
            embeddings = []
            for row in results:
                emb_str = row[1]
                if isinstance(emb_str, str):
                    emb_str = emb_str.strip('[]')
                    emb = [float(x) for x in emb_str.split(',')]
                    embeddings.append(emb)
            
            embeddings = np.array(embeddings)
            
            kmeans = KMeans(n_clusters=min(n_clusters, len(results)), random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)
            
            clusters = {}
            for cluster_id in range(len(set(labels))):
                mask = labels == cluster_id
                cluster_logs = [log_ids[i] for i, m in enumerate(mask) if m]
                clusters[cluster_id] = {
                    'size': len(cluster_logs),
                    'centroid': kmeans.cluster_centers_[cluster_id].tolist()[:5],
                    'sample_logs': cluster_logs[:3]
                }
            
            print(f"\n✓ {len(clusters)} clusters identifiés:")
            for cluster_id, info in clusters.items():
                print(f"  Cluster {cluster_id}: {info['size']} logs")
            
            return clusters
            
        except Exception as e:
            logger.error(f"Erreur clustering: {e}")
            return {}
    
    def temporal_analysis(self, error_pattern: str, timeframe_days: int = 7) -> Dict:
        """Cas d'usage 3: Analyser l'évolution temporelle des erreurs similaires"""
        print(f"\n📅 Analyse temporelle pour: '{error_pattern}'")
        
        query_embedding = self.model.encode(error_pattern)
        results = self.db.semantic_search(query_embedding.tolist(), top_k=1000, threshold=0.4)
        
        if not results:
            logger.warning("Aucun log trouvé pour ce pattern")
            return {}
        
        # Grouper par date
        from collections import defaultdict
        temporal_data = defaultdict(int)
        
        for result in results:
            timestamp = result.get('timestamp')
            if timestamp:
                date_key = str(timestamp)[:10]  # YYYY-MM-DD
                temporal_data[date_key] += 1
        
        sorted_data = dict(sorted(temporal_data.items()))
        
        print(f"\n✓ Distribution temporelle ({len(sorted_data)} jours):")
        for date, count in list(sorted_data.items())[:10]:
            print(f"  {date}: {count} erreurs")
        
        return sorted_data
    
    def compare_with_keyword_search(self, query: str, top_k: int = 10) -> Dict:
        """Compare recherche sémantique vs recherche par mots-clés"""
        print(f"\n🔬 Comparaison: Sémantique vs Mot-clé")
        print(f"   Requête: '{query}'")
        
        query_embedding = self.model.encode(query)
        semantic_results = self.db.semantic_search(query_embedding.tolist(), top_k=top_k)
        
        # Recherche par mot-clé simple
        keyword_query = f"%{query.lower()}%"
        self.db.cursor.execute("""
            SELECT id, original_text, log_level, timestamp
            FROM logs
            WHERE normalized_text LIKE %s
            LIMIT %s
        """, (keyword_query, top_k))
        
        keyword_results = []
        for row in self.db.cursor.fetchall():
            keyword_results.append({
                'id': row[0],
                'text': row[1],
                'log_level': row[2],
                'timestamp': row[3]
            })
        
        print(f"\n✓ Résultats:")
        print(f"  Recherche sémantique: {len(semantic_results)} résultats")
        print(f"  Recherche par mot-clé: {len(keyword_results)} résultats")
        
        return {
            'semantic': semantic_results,
            'keyword': keyword_results,
            'semantic_count': len(semantic_results),
            'keyword_count': len(keyword_results)
        }
    
    def close(self):
        """Ferme la connexion à la base"""
        self.db.disconnect()


def run_demo():
    """Démo des cas d'usage"""
    
    engine = SemanticSearchEngine()
    
    print("\n" + "="*70)
    print("🚀 DÉMONSTRATION - RECHERCHE SÉMANTIQUE")
    print("="*70)
    
    try:
        print("\n" + "-"*70)
        print("📌 CAS 1: Retrouver logs similaires à une erreur donnée")
        print("-"*70)
        engine.search_by_error("Database connection timeout error", top_k=5)
        
        print("\n" + "-"*70)
        print("📌 CAS 2: Identifier les groupes d'erreurs fréquentes")
        print("-"*70)
        clusters = engine.find_error_clusters(n_clusters=3)
        
        print("\n" + "-"*70)
        print("📌 CAS 3: Analyser l'évolution des erreurs")
        print("-"*70)
        engine.temporal_analysis("connection error", timeframe_days=7)
        
        print("\n" + "-"*70)
        print("📌 CAS 4: Comparer recherche sémantique vs mot-clé")
        print("-"*70)
        engine.compare_with_keyword_search("timeout", top_k=5)
        
    finally:
        engine.close()


if __name__ == "__main__":
    run_demo()