import psycopg2
from psycopg2.extras import execute_values
import logging

logger = logging.getLogger(__name__)

class VectorDatabase:
    def __init__(self, host='172.17.22.69', database='semantic_logs', user='postgres', password='sound2003', port='5432'):
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
            
            # Table log_embeddings avec pgvector
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_embeddings (
                    id SERIAL PRIMARY KEY,
                    log_id INTEGER REFERENCES logs(id) ON DELETE CASCADE,
                    embedding vector(384),
                    model_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Créer l'index pour la recherche vectorielle (ivfflat pour de bonnes performances)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_log_embeddings_vector 
                ON log_embeddings USING ivfflat (embedding vector_cosine_ops)
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
            query = """
                INSERT INTO logs (original_text, normalized_text, log_level, timestamp, source_ip)
                VALUES %s
                RETURNING id
            """
            values = [
                (
                    log.get('original_text', ''),
                    log.get('normalized_text', ''),
                    log.get('log_level', 'UNKNOWN'),
                    log.get('timestamp'),
                    log.get('source_ip')
                )
                for log in log_records
            ]
            
            execute_values(self.cursor, query, values, fetch=True)
            self.conn.commit()
            
            ids = [row[0] for row in self.cursor.fetchall()]
            logger.info(f"✓ {len(ids)} logs insérés")
            return ids
            
        except Exception as e:
            logger.error(f"✗ Erreur insertion logs: {e}")
            self.conn.rollback()
            return []
    
    def insert_embeddings(self, embedding_records):
        """Insère les embeddings"""
        try:
            query = """
                INSERT INTO log_embeddings (log_id, embedding, model_name)
                VALUES %s
            """
            values = [
                (
                    record['log_id'],
                    record['embedding'],
                    record['model_name']
                )
                for record in embedding_records
            ]
            
            execute_values(self.cursor, query, values)
            self.conn.commit()
            logger.info(f"✓ {len(embedding_records)} embeddings insérés")
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
        """Recherche les logs similaires par similarité cosinus"""
        try:
            self.cursor.execute("""
                SELECT l.id, l.original_text, l.log_level, l.timestamp, 
                       le.embedding <=> %s::vector as distance
                FROM logs l
                JOIN log_embeddings le ON l.id = le.log_id
                ORDER BY le.embedding <=> %s::vector
                LIMIT %s
            """, (query_embedding, query_embedding, limit))
            
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"✗ Erreur recherche: {e}")
            return []
    
    def disconnect(self):
        """Ferme la connexion"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("✓ Déconnecté de PostgreSQL")