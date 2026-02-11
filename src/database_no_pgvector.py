#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Solution rapide: Utiliser une base de données SANS pgvector
Stocke les embeddings en format binaire, calcule les distances en Python
Fonctionne IMMÉDIATEMENT sans installation pgvector
"""

import psycopg2
from psycopg2.extras import execute_values
import logging
import numpy as np
import pickle

logger = logging.getLogger(__name__)

class VectorDatabase:
    """Base de données pour embeddings - version SANS pgvector"""
    
    def __init__(self, host='localhost', database='semantic_logs', user='postgres', password='sound2003', port='5432'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connecte à PostgreSQL"""
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
            logger.error(f"✗ Erreur connexion: {e}")
            return False
    
    def create_tables(self):
        """Crée les tables (SANS pgvector)"""
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
            
            # Table embeddings (BYTEA = format binaire)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_embeddings (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER REFERENCES logs(id) ON DELETE CASCADE,
                    embedding BYTEA NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_log_id 
                ON log_embeddings(log_id)
            """)
            
            self.conn.commit()
            logger.info("✓ Tables créées")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur création tables: {e}")
            self.conn.rollback()
            return False
    
    def insert_logs(self, logs_data):
        """Insère les logs"""
        try:
            ids = []
            for log in logs_data:
                self.cursor.execute("""
                    INSERT INTO logs (timestamp, level, message)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (log['timestamp'], log['level'], log['message']))
                ids.append(self.cursor.fetchone()[0])
            
            self.conn.commit()
            logger.info(f"✓ {len(ids)} logs insérés")
            return ids
        except Exception as e:
            logger.error(f"✗ Erreur insertion: {e}")
            self.conn.rollback()
            return []
    
    def insert_embeddings(self, embeddings_data):
        """Insère les embeddings en format binaire compressé"""
        try:
            for log_id, embedding in embeddings_data:
                # Sérialiser l'embedding numpy en bytes
                embedding_bytes = pickle.dumps(np.array(embedding, dtype=np.float32), protocol=pickle.HIGHEST_PROTOCOL)
                
                self.cursor.execute("""
                    INSERT INTO log_embeddings (log_id, embedding)
                    VALUES (%s, %s)
                """, (log_id, embedding_bytes))
            
            self.conn.commit()
            logger.info(f"✓ {len(embeddings_data)} embeddings insérés")
            return len(embeddings_data)
        except Exception as e:
            logger.error(f"✗ Erreur insertion embeddings: {e}")
            self.conn.rollback()
            return 0
    
    def semantic_search(self, query_embedding, top_k=5, threshold=0.5):
        """
        Recherche sémantique SANS pgvector
        Calcule la similarité cosinus en Python
        """
        try:
            self.cursor.execute("""
                SELECT le.log_id, le.embedding, l.message, l.timestamp, l.level
                FROM log_embeddings le
                JOIN logs l ON le.log_id = l.id
                LIMIT 5000
            """)
            
            results = self.cursor.fetchall()
            similarities = []
            query_vec = np.array(query_embedding, dtype=np.float32)
            
            for log_id, embedding_bytes, message, timestamp, level in results:
                # Désérialiser l'embedding
                embedding = pickle.loads(embedding_bytes)
                
                # Calculer similarité cosinus
                sim = self._cosine_similarity(query_vec, embedding)
                
                if sim >= threshold:
                    similarities.append({
                        'id': log_id,
                        'message': message,
                        'timestamp': timestamp,
                        'level': level,
                        'similarity': float(sim)
                    })
            
            # Trier par similarité
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
        
        except Exception as e:
            logger.error(f"✗ Erreur recherche: {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(a, b):
        """Calcule la similarité cosinus"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def get_embeddings_for_clustering(self, log_level=None, limit=1000):
        """Récupère les embeddings pour clustering"""
        try:
            if log_level:
                query = """
                    SELECT le.log_id, le.embedding
                    FROM log_embeddings le
                    JOIN logs l ON le.log_id = l.id
                    WHERE l.level = %s
                    LIMIT %s
                """
                self.cursor.execute(query, (log_level, limit))
            else:
                query = """
                    SELECT le.log_id, le.embedding
                    FROM log_embeddings le
                    LIMIT %s
                """
                self.cursor.execute(query, (limit,))
            
            rows = self.cursor.fetchall()
            embeddings = []
            log_ids = []
            
            for log_id, embedding_bytes in rows:
                embedding = pickle.loads(embedding_bytes)
                embeddings.append(embedding)
                log_ids.append(log_id)
            
            return np.array(embeddings), log_ids
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return np.array([]), []
    
    def get_error_logs(self, limit=100):
        """Récupère les logs d'erreur"""
        try:
            self.cursor.execute("""
                SELECT id, timestamp, level, message
                FROM logs
                WHERE level IN ('ERROR', 'CRITICAL')
                LIMIT %s
            """, (limit,))
            
            rows = self.cursor.fetchall()
            return [
                {'id': r[0], 'timestamp': r[1], 'level': r[2], 'message': r[3]}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return []
    
    def get_logs_by_level(self, level, limit=100):
        """Récupère les logs par niveau"""
        try:
            self.cursor.execute("""
                SELECT id, timestamp, level, message
                FROM logs
                WHERE level = %s
                LIMIT %s
            """, (level, limit))
            
            rows = self.cursor.fetchall()
            return [
                {'id': r[0], 'timestamp': r[1], 'level': r[2], 'message': r[3]}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return []
    
    def get_log_by_id(self, log_id):
        """Récupère un log par ID"""
        try:
            self.cursor.execute("""
                SELECT id, timestamp, level, message
                FROM logs
                WHERE id = %s
            """, (log_id,))
            
            row = self.cursor.fetchone()
            if row:
                return {'id': row[0], 'timestamp': row[1], 'level': row[2], 'message': row[3]}
            return None
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return None
    
    def search_by_keyword(self, keyword, limit=10):
        """Recherche par mot-clé"""
        try:
            self.cursor.execute("""
                SELECT id, timestamp, level, message
                FROM logs
                WHERE message ILIKE %s
                LIMIT %s
            """, (f"%{keyword}%", limit))
            
            rows = self.cursor.fetchall()
            return [
                {'id': r[0], 'timestamp': r[1], 'level': r[2], 'message': r[3]}
                for r in rows
            ]
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return []
    
    def get_stats(self):
        """Retourne les stats"""
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
