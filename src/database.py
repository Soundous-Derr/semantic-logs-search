import psycopg2
from psycopg2.extras import execute_values
import logging
import numpy as np
import pickle

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, host='localhost', database='semantic_logs', user='postgres', password='sound2003', port='5432'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connecte à la base de données"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            logger.info("✓ Connecté à PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur connexion PostgreSQL: {e}")
            return False
    
    def create_tables(self):
        """Crée les tables si elles n'existent pas"""
        try:
            # Table logs
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    original_text TEXT,
                    normalized_text TEXT,
                    log_level VARCHAR(20),
                    timestamp TIMESTAMP,
                    source_ip VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table log_embeddings (SANS pgvector - utilise BYTEA)
            # Fonctionne immédiatement sans installation supplémentaire
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_embeddings (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER REFERENCES logs(id) ON DELETE CASCADE,
                    embedding BYTEA NOT NULL,
                    model_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index simple (sans pgvector)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_log_embeddings_log_id 
                ON log_embeddings (log_id)
            """)
            
            self.conn.commit()
            logger.info("✓ Tables créées/vérifiées")
            return True
            
        except Exception as e:
            logger.error(f"✗ Erreur création tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_logs(self, log_records):
        """Insère des logs et retourne les IDs"""
        try:
            ids = []
            for log in log_records:
                self.cursor.execute("""
                    INSERT INTO logs (original_text, normalized_text, log_level, timestamp, source_ip)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    log.get('original_text', ''),
                    log.get('normalized_text', ''),
                    log.get('log_level', 'UNKNOWN'),
                    log.get('timestamp'),
                    log.get('source_ip')
                ))
                ids.append(self.cursor.fetchone()[0])
            
            self.conn.commit()
            logger.info(f"✓ {len(ids)} logs insérés")
            return ids
            
        except Exception as e:
            logger.error(f"✗ Erreur insertion logs: {e}")
            self.conn.rollback()
            return []
    
    def insert_embeddings(self, embedding_records):
        """Insère les embeddings en format binaire compressé (SANS pgvector)"""
        try:
            inserted = 0
            for record in embedding_records:
                # Convertir l'embedding numpy en bytes compressés
                embedding_array = np.array(record['embedding'], dtype=np.float32)
                embedding_bytes = pickle.dumps(embedding_array, protocol=pickle.HIGHEST_PROTOCOL)
                
                self.cursor.execute("""
                    INSERT INTO log_embeddings (log_id, embedding, model_name)
                    VALUES (%s, %s, %s)
                """, (
                    record['log_id'],
                    embedding_bytes,
                    record['model_name']
                ))
                inserted += 1
            
            self.conn.commit()
            logger.info(f"✓ {inserted} embeddings insérés")
            return True
            
        except Exception as e:
            logger.error(f"✗ Erreur insertion embeddings: {e}")
            self.conn.rollback()
            return False
    
    def get_statistics(self):
        """Récupère les statistiques"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM logs")
            total_logs = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM log_embeddings")
            total_embeddings = self.cursor.fetchone()[0]
            
            return {
                'total_logs': total_logs,
                'total_embeddings': total_embeddings
            }
        except Exception as e:
            logger.error(f"✗ Erreur récupération stats: {e}")
            return {'total_logs': 0, 'total_embeddings': 0}
    
    def search_similar(self, query_embedding, limit=10):
        """Recherche les logs similaires par similarité cosinus (SANS pgvector)"""
        try:
            query_vec = np.array(query_embedding, dtype=np.float32)
            
            self.cursor.execute("""
                SELECT l.id, l.original_text, l.log_level, l.timestamp, le.embedding
                FROM logs l
                JOIN log_embeddings le ON l.id = le.log_id
                LIMIT 5000
            """)
            
            results = []
            for row in self.cursor.fetchall():
                log_id, text, level, timestamp, embedding_bytes = row
                
                # Désérialiser l'embedding
                embedding = pickle.loads(embedding_bytes)
                
                # Calculer la similarité cosinus
                norm_a = np.linalg.norm(query_vec)
                norm_b = np.linalg.norm(embedding)
                
                if norm_a > 0 and norm_b > 0:
                    similarity = float(np.dot(query_vec, embedding) / (norm_a * norm_b))
                else:
                    similarity = 0.0
                
                # Convertir en distance pour compatibilité
                distance = 1 - similarity
                
                results.append((log_id, text, level, timestamp, distance, similarity))
            
            # Trier par similarité (distance décroissante = similarité croissante)
            results.sort(key=lambda x: x[4])  # Trier par distance
            
            return results[:limit]
        except Exception as e:
            logger.error(f"✗ Erreur recherche: {e}")
            return []
    
    def semantic_search(self, query_embedding, top_k=10, threshold=0.5):
        """Recherche sémantique avec similarité cosinus (SANS pgvector)"""
        try:
            query_vec = np.array(query_embedding, dtype=np.float32)
            similarities = []
            
            self.cursor.execute("""
                SELECT l.id, l.original_text, l.log_level, l.timestamp, le.embedding
                FROM logs l
                JOIN log_embeddings le ON l.id = le.log_id
                LIMIT 10000
            """)
            
            for row in self.cursor.fetchall():
                log_id, text, level, timestamp, embedding_bytes = row
                
                # Désérialiser l'embedding
                embedding = pickle.loads(embedding_bytes)
                
                # Calculer la similarité cosinus
                norm_a = np.linalg.norm(query_vec)
                norm_b = np.linalg.norm(embedding)
                
                if norm_a > 0 and norm_b > 0:
                    similarity = float(np.dot(query_vec, embedding) / (norm_a * norm_b))
                else:
                    similarity = 0.0
                
                # Appliquer le seuil
                if similarity >= threshold:
                    similarities.append({
                        'id': log_id,
                        'text': text,
                        'log_level': level,
                        'timestamp': timestamp,
                        'similarity': similarity
                    })
            
            # Trier par similarité décroissante
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"✗ Erreur recherche sémantique: {e}")
            return []
    
    def get_log_by_id(self, log_id):
        """Récupère un log par son ID"""
        try:
            self.cursor.execute("""
                SELECT id, original_text, normalized_text, log_level, timestamp, source_ip
                FROM logs
                WHERE id = %s
            """, (log_id,))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'original_text': row[1],
                    'normalized_text': row[2],
                    'log_level': row[3],
                    'timestamp': row[4],
                    'source_ip': row[5]
                }
            return None
        except Exception as e:
            logger.error(f"✗ Erreur récupération log: {e}")
            return None
    
    def get_error_logs(self, limit=1000):
        """Récupère les logs d'erreur"""
        try:
            self.cursor.execute("""
                SELECT l.id, l.original_text, l.log_level, l.timestamp
                FROM logs l
                WHERE l.log_level IN ('ERROR', 'CRITICAL', 'FATAL', 'WARNING')
                ORDER BY l.timestamp DESC
                LIMIT %s
            """, (limit,))
            
            results = self.cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'text': row[1],
                    'log_level': row[2],
                    'timestamp': row[3]
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"✗ Erreur récupération erreurs: {e}")
            return []
    
    def get_logs_by_level(self, level, limit=1000):
        """Récupère les logs d'un niveau spécifique"""
        try:
            self.cursor.execute("""
                SELECT l.id, l.original_text, l.log_level, l.timestamp
                FROM logs l
                WHERE l.log_level = %s
                ORDER BY l.timestamp DESC
                LIMIT %s
            """, (level, limit))
            
            results = self.cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'text': row[1],
                    'log_level': row[2],
                    'timestamp': row[3]
                }
                for row in results
            ]
        except Exception as e:
            logger.error(f"✗ Erreur récupération logs: {e}")
            return []
    
    def get_embeddings_for_clustering(self, log_level=None, limit=5000):
        """Récupère les embeddings pour clustering"""
        try:
            if log_level:
                self.cursor.execute("""
                    SELECT l.id, le.embedding, l.original_text, l.log_level
                    FROM log_embeddings le
                    JOIN logs l ON le.log_id = l.id
                    WHERE l.log_level = %s
                    LIMIT %s
                """, (log_level, limit))
            else:
                self.cursor.execute("""
                    SELECT l.id, le.embedding, l.original_text, l.log_level
                    FROM log_embeddings le
                    JOIN logs l ON le.log_id = l.id
                    LIMIT %s
                """, (limit,))
            
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"✗ Erreur récupération embeddings: {e}")
            return []
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("✓ Déconnecté de PostgreSQL")
    
    def close(self):
        """Alias pour disconnect"""
        self.disconnect()