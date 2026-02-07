"""
Phase 3: Génération des embeddings et insertion dans pgvector
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import logging
from .database import VectorDatabase
from .utils import batch_generator, get_logger
import pandas as pd

logger = get_logger(__name__)


class LogVectorizer:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """Initialise le modèle de vectorisation"""
        self.model_name = model_name
        logger.info(f"Chargement du modèle: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"✓ Modèle chargé (dimension: {self.model.get_sentence_embedding_dimension()})")

    def vectorize_logs(self, logs: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Vectorise une liste de logs"""
        # Filtrer les None et vides
        logs = [str(log).strip() for log in logs if log is not None and str(log).strip()]
        
        if not logs:
            logger.warning("Aucun log valide à vectoriser")
            return []
        
        try:
            embeddings = self.model.encode(
                logs,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            logger.info(f"✓ {len(logs)} logs vectorisés")
            return embeddings
        except Exception as e:
            logger.error(f"✗ Erreur vectorisation: {e}")
            return []

    def get_embedding_dimension(self) -> int:
        """Retourne la dimension des embeddings"""
        return self.model.get_sentence_embedding_dimension()


class BatchVectorization:
    def __init__(self, db: VectorDatabase, vectorizer: LogVectorizer, batch_size: int = 100):
        """Gestionnaire de vectorisation par lots"""
        self.db = db
        self.vectorizer = vectorizer
        self.batch_size = batch_size

    def process_logs_from_parquet(self, parquet_path: str):
        """Traite les logs depuis un fichier Parquet avec Spark"""
        try:
            import os
            import sys
            
            # Configuration Java et Hadoop (comme dans Phase 2)
            java_path = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"
            os.environ['JAVA_HOME'] = java_path
            os.environ['HADOOP_HOME'] = r"C:\hadoop"
            os.environ['PYSPARK_PYTHON'] = sys.executable
            os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
            
            import findspark
            findspark.init()
            
            from pyspark.sql import SparkSession
            
            spark = SparkSession.builder \
                .appName("Vectorization") \
                .master("local[*]") \
                .getOrCreate()
            
            df = spark.read.parquet(parquet_path)
            logger.info(f"✓ {df.count()} logs chargés depuis Parquet")
            
            pandas_df = df.toPandas()
            self.process_logs_dataframe(pandas_df)
            
            spark.stop()
            logger.info("✓ Traitement Parquet terminé")
            
        except Exception as e:
            logger.error(f"✗ Erreur traitement Parquet: {e}")
            import traceback
            traceback.print_exc()

    def process_logs_dataframe(self, df):
        """Traite un DataFrame de logs"""
        
        total_logs = len(df)
        processed = 0
        
        for batch in batch_generator(df.to_dict('records'), self.batch_size):
            log_records = []
            for log in batch:
                # Utiliser 'value' si 'original_text' n'existe pas
                original = log.get('original_text') or log.get('value') or ''
                normalized = log.get('normalized_text') or log.get('value') or ''
                
                log_records.append({
                    'original_text': original,
                    'normalized_text': normalized,
                    'log_level': log.get('level') or log.get('log_level', 'UNKNOWN'),
                    'timestamp': log.get('timestamp') or log.get('timestamp_str'),
                    'source_ip': log.get('source_ip')
                })
            
            log_ids = self.db.insert_logs(log_records)
            
            # Utiliser normalized_text ou value pour la vectorisation
            texts = [log.get('normalized_text') or log.get('value') or '' for log in batch]
            embeddings = self.vectorizer.vectorize_logs(texts)
            
            embedding_records = []
            for idx, (log_id, embedding) in enumerate(zip(log_ids, embeddings)):
                if idx < len(log_ids) and embedding is not None:
                    embedding_records.append({
                        'log_id': log_id,
                        'embedding': embedding.tolist(),
                        'model_name': self.vectorizer.model_name
                    })
            
            if embedding_records:
                self.db.insert_embeddings(embedding_records)
            
            processed += len(batch)
            progress = (processed / total_logs) * 100
            logger.info(f"Progression: {processed:,}/{total_logs:,} ({progress:.1f}%)")


class VectorizationPipeline:
    def __init__(self):
        self.db = VectorDatabase()
        self.vectorizer = None
    
    def run(self, parquet_path: str):
        """Exécute le pipeline de vectorisation"""
        
        print("\n" + "="*60)
        print("🔢 VECTORISATION - PHASE 3")
        print("="*60)
        
        if not self.db.connect():
            logger.error("Impossible de se connecter à la base de données")
            return False
        
        try:
            # Créer les tables si elles n'existent pas
            self.db.create_tables()
            
            self.vectorizer = LogVectorizer()
            batch_vectorizer = BatchVectorization(self.db, self.vectorizer)
            batch_vectorizer.process_logs_from_parquet(parquet_path)
            
            stats = self.db.get_statistics()
            print(f"\n✓ Vectorisation complète:")
            print(f"  Total logs: {stats.get('total_logs', 0):,}")
            print(f"  Total embeddings: {stats.get('total_embeddings', 0):,}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur pipeline: {e}")
            return False
            
        finally:
            self.db.disconnect()


if __name__ == "__main__":
    pipeline = VectorizationPipeline()
    pipeline.run("data/processed/logs_parsed")