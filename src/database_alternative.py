# -*- coding: utf-8 -*-
"""
Alternative pour PostgreSQL SANS pgvector extension
Stocke les embeddings en tant que bytea (format binaire compressé)
La logique sémantique reste identique
"""

import psycopg2
from psycopg2.extras import execute_values
import logging
import numpy as np
import pickle

logger = logging.getLogger(__name__)

class VectorDatabaseAlternative:
    """Version qui n'utilise PAS l'extension pgvector"""
    
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
    
    def create_tables_alternative(self):
        """Crée les tables SANS pgvector"""
        try:
            # Table logs
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    timestamp VARCHAR(30),
                    level VARCHAR(20),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table embeddings (sans type vector, utilise BYTEA)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_embeddings (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER REFERENCES logs(id) ON DELETE CASCADE,
                    embedding BYTEA NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index simple
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_log_id 
                ON log_embeddings(log_id)
            """)
            
            self.conn.commit()
            logger.info("✓ Tables créées (version sans pgvector)")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur création tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_logs(self, logs_data):
        """Insère les logs"""
        try:
            rows = [(log['timestamp'], log['level'], log['message']) 
                    for log in logs_data]
            
            ids = []
            for ts, level, msg in rows:
                self.cursor.execute("""
                    INSERT INTO logs (timestamp, level, message)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (ts, level, msg))
                ids.append(self.cursor.fetchone()[0])
            
            self.conn.commit()
            logger.info(f"✓ {len(ids)} logs insérés")
            return ids
        except Exception as e:
            logger.error(f"✗ Erreur insertion logs: {e}")
            self.conn.rollback()
            return []
    
    def insert_embeddings(self, embeddings_data):
        """
        Insère les embeddings en format binaire compressé
        embeddings_data: [(log_id, embedding_array), ...]
        """
        try:
            inserted = 0
            for log_id, embedding in embeddings_data:
                # Convertir numpy array en bytes (format compact)
                embedding_bytes = pickle.dumps(embedding, protocol=pickle.HIGHEST_PROTOCOL)
                
                self.cursor.execute("""
                    INSERT INTO log_embeddings (log_id, embedding)
                    VALUES (%s, %s)
                """, (log_id, embedding_bytes))
                inserted += 1
            
            self.conn.commit()
            logger.info(f"✓ {inserted} embeddings insérés")
            return inserted
        except Exception as e:
            logger.error(f"✗ Erreur insertion embeddings: {e}")
            self.conn.rollback()
            return 0
    
    def search_similar(self, query_embedding, top_k=5, threshold=0.5):
        """
        Recherche sémantique en calcul Python (sans pgvector)
        """
        try:
            self.cursor.execute("""
                SELECT le.log_id, le.embedding, l.message
                FROM log_embeddings le
                JOIN logs l ON le.log_id = l.id
                LIMIT 1000
            """)
            
            results = self.cursor.fetchall()
            similarities = []
            
            for log_id, embedding_bytes, message in results:
                # Décoder l'embedding
                embedding = pickle.loads(embedding_bytes)
                
                # Calculer la similarité cosinus
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                if similarity >= threshold:
                    similarities.append({
                        'log_id': log_id,
                        'message': message,
                        'similarity': similarity
                    })
            
            # Trier par similarité décroissante
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"✗ Erreur recherche: {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(a, b):
        """Calcule la similarité cosinus entre deux vecteurs"""
        a = np.array(a)
        b = np.array(b)
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return np.dot(a, b) / (norm_a * norm_b)
    
    def get_log_by_id(self, log_id):
        """Récupère un log par ID"""
        try:
            self.cursor.execute("SELECT * FROM logs WHERE id = %s", (log_id,))
            row = self.cursor.fetchone()
            if row:
                return {'id': row[0], 'timestamp': row[1], 'level': row[2], 'message': row[3]}
            return None
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return None
    
    def get_stats(self):
        """Retourne les statistiques de la base"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM logs")
            log_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM log_embeddings")
            embedding_count = self.cursor.fetchone()[0]
            
            return {
                'logs': log_count,
                'embeddings': embedding_count,
                'dimension': 384
            }
        except:
            return {'logs': 0, 'embeddings': 0, 'dimension': 0}
    
    def close(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
