"""
Gestion de la base de données PostgreSQL + pgvector
"""

import psycopg2
from psycopg2.extras import execute_batch
import numpy as np
from typing import List, Dict, Tuple
import logging
import os

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, host=None, user=None, password=None, 
                 db=None, port=None):
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.user = user or os.getenv('DB_USER', 'logadmin')
        self.password = password or os.getenv('DB_PASSWORD', 'logsearch2024')
        self.db = db or os.getenv('DB_NAME', 'semantic_logs')
        self.port = port or int(os.getenv('DB_PORT', 5432))
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Établit la connexion à PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
                port=self.port
            )
            self.cursor = self.conn.cursor()
            logger.info("✓ Connecté à PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur de connexion: {e}")
            return False
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("✓ Déconnecté de PostgreSQL")
    
    def insert_logs(self, logs: List[Dict]) -> List[int]:
        """Insère des logs dans la base de données"""
        query = """
        INSERT INTO logs (original_text, normalized_text, log_level, timestamp, source_ip)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        
        data = []
        for log in logs:
            data.append((
                log.get('original_text'),
                log.get('normalized_text'),
                log.get('log_level'),
                log.get('timestamp'),
                log.get('source_ip')
            ))
        
        try:
            for item in data:
                self.cursor.execute(query, item)
            self.conn.commit()
            logger.info(f"✓ {len(logs)} logs insérés")
            return list(range(1, len(logs) + 1))
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Erreur insertion logs: {e}")
            return []
    
    def insert_embeddings(self, embeddings: List[Dict]) -> bool:
        """Insère les embeddings vectoriels"""
        query = """
        INSERT INTO log_embeddings (log_id, embedding, model_name)
        VALUES (%s, %s, %s)
        """
        
        try:
            for emb in embeddings:
                vector_str = '[' + ','.join(map(str, emb['embedding'])) + ']'
                self.cursor.execute(query, (
                    emb['log_id'],
                    vector_str,
                    emb.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')
                ))
            self.conn.commit()
            logger.info(f"✓ {len(embeddings)} embeddings insérés")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Erreur insertion embeddings: {e}")
            return False
    
    def semantic_search(self, query_embedding: List[float], top_k: int = 10, 
                       threshold: float = 0.5) -> List[Dict]:
        """Effectue une recherche sémantique"""
        vector_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        query = f"""
        SELECT 
            l.id,
            l.original_text,
            l.log_level,
            l.timestamp,
            (le.embedding <=> %s) AS distance,
            (1 - (le.embedding <=> %s)) AS similarity
        FROM logs l
        JOIN log_embeddings le ON l.id = le.log_id
        WHERE (1 - (le.embedding <=> %s)) > %s
        ORDER BY distance ASC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query, (vector_str, vector_str, vector_str, threshold, top_k))
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'id': row[0],
                    'text': row[1],
                    'log_level': row[2],
                    'timestamp': row[3],
                    'distance': float(row[4]) if row[4] else 0,
                    'similarity': float(row[5]) if row[5] else 0
                })
            return results
        except Exception as e:
            logger.error(f"✗ Erreur recherche sémantique: {e}")
            return []
    
    def find_similar_logs(self, log_id: int, top_k: int = 10) -> List[Dict]:
        """Trouve les logs similaires à un log donné"""
        query = """
        SELECT 
            l2.id,
            l2.original_text,
            l2.log_level,
            (le1.embedding <=> le2.embedding) AS distance,
            (1 - (le1.embedding <=> le2.embedding)) AS similarity
        FROM log_embeddings le1
        JOIN log_embeddings le2 ON le1.embedding IS NOT NULL AND le2.embedding IS NOT NULL
        JOIN logs l2 ON le2.log_id = l2.id
        WHERE le1.log_id = %s AND l2.id != %s
        ORDER BY distance ASC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query, (log_id, log_id, top_k))
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'id': row[0],
                    'text': row[1],
                    'log_level': row[2],
                    'distance': float(row[3]) if row[3] else 0,
                    'similarity': float(row[4]) if row[4] else 0
                })
            return results
        except Exception as e:
            logger.error(f"✗ Erreur recherche similaires: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Récupère les statistiques de la base"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM logs")
            total_logs = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM log_embeddings")
            total_embeddings = self.cursor.fetchone()[0]
            
            self.cursor.execute("""
            SELECT log_level, COUNT(*) as count 
            FROM logs 
            GROUP BY log_level
            """)
            level_stats = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            return {
                'total_logs': total_logs,
                'total_embeddings': total_embeddings,
                'by_log_level': level_stats
            }
        except Exception as e:
            logger.error(f"✗ Erreur récupération stats: {e}")
            return {}