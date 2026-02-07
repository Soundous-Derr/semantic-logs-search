
"""
Phase 2: Pipeline Spark pour ingestion et traitement massif
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import re
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

class SparkLogsPipeline:
    def __init__(self, app_name="Semantic-Logs-Pipeline"):
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.executor.memory", "2g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "100") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("✓ Spark Session créée")
    
    def load_logs(self, input_path: str, sample_fraction: float = 1.0):
        """Charge les logs depuis un fichier texte"""
        try:
            df = self.spark.read.text(input_path)
            df = df.withColumnRenamed("value", "original_text")
            df = df.filter(col("original_text").isNotNull())
            df = df.filter(col("original_text") != "")
            
            if sample_fraction < 1.0:
                df = df.sample(fraction=sample_fraction, seed=42)
            
            count = df.count()
            print(f"✓ {count:,} logs chargés")
            return df
        except Exception as e:
            logger.error(f"✗ Erreur lors du chargement: {e}")
            return None
    
    def normalize_logs(self, df):
        """Normalise les logs"""
        
        @udf(StringType())
        def normalize(text):
            if text is None:
                return None
            text = ' '.join(text.split())
            text = text.lower()
            return text
        
        df = df.withColumn("normalized_text", normalize(col("original_text")))
        return df
    
    def extract_log_metadata(self, df):
        """Extrait les métadonnées des logs"""
        
        @udf(StringType())
        def extract_level(text):
            if not text:
                return 'UNKNOWN'
            levels = ['critical', 'error', 'warning', 'info', 'debug']
            text_lower = text.lower()
            for level in levels:
                if f'[{level}]' in text_lower or f' {level} ' in text_lower:
                    return level.upper()
            return 'UNKNOWN'
        
        @udf(StringType())
        def extract_ip(text):
            if not text:
                return None
            match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
            return match.group(0) if match else None
        
        @udf(StringType())
        def extract_timestamp(text):
            if not text:
                return None
            patterns = [
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
                r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})',
                r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})'
            ]
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1)
            return None
        
        df = df.withColumn("log_level", extract_level(col("normalized_text")))
        df = df.withColumn("source_ip", extract_ip(col("normalized_text")))
        df = df.withColumn("timestamp_str", extract_timestamp(col("normalized_text")))
        
        return df
    
    def remove_duplicates(self, df, subset=['normalized_text']):
        """Supprime les doublons"""
        initial_count = df.count()
        df = df.dropDuplicates(subset)
        final_count = df.count()
        
        removed = initial_count - final_count
        if initial_count > 0:
            print(f"✓ Doublons supprimés: {removed:,} ({removed/initial_count*100:.1f}%)")
        
        return df
    
    def filter_valid_logs(self, df, min_length=10):
        """Filtre les logs valides"""
        df = df.filter(length(col("original_text")) >= min_length)
        return df
    
    def add_processing_metadata(self, df):
        """Ajoute les métadonnées de traitement"""
        df = df.withColumn("processed_at", current_timestamp())
        df = df.withColumn("log_length", length(col("original_text")))
        df = df.withColumn("word_count", size(split(col("normalized_text"), " ")))
        
        return df
    
    def partition_data(self, df, partition_column='log_level', num_partitions=10):
        """Partitionne les données"""
        df = df.repartition(num_partitions, col(partition_column))
        return df
    
    def save_parquet(self, df, output_path: str):
        """Sauvegarde en format Parquet"""
        df.write.mode("overwrite").parquet(output_path)
        print(f"✓ Données sauvegardées: {output_path}")
    
    def run_full_pipeline(self, input_path: str, output_path: str):
        """Exécute le pipeline complet"""
        
        print("\n" + "="*60)
        print("🚀 PIPELINE SPARK - PHASE 2")
        print("="*60)
        
        print("\n📥 Chargement des logs...")
        df = self.load_logs(input_path)
        
        if df is None:
            logger.error("Échec du chargement des logs")
            return None
        
        print("🧹 Normalisation...")
        df = self.normalize_logs(df)
        
        print("📊 Extraction des métadonnées...")
        df = self.extract_log_metadata(df)
        
        print("🔍 Filtrage des logs valides...")
        df = self.filter_valid_logs(df)
        
        print("🗑️  Suppression des doublons...")
        df = self.remove_duplicates(df)
        
        print("⚙️  Ajout des métadonnées...")
        df = self.add_processing_metadata(df)
        
        print("📦 Partitionnement...")
        df = self.partition_data(df)
        
        print("\n📈 Statistiques finales:")
        final_count = df.count()
        print(f"  Total logs: {final_count:,}")
        
        if final_count > 0:
            df.groupBy("log_level").count().orderBy(desc("count")).show()
        
        print(f"\n💾 Sauvegarde en Parquet...")
        self.save_parquet(df, output_path)
        
        return df
    
    def stop(self):
        """Arrête la session Spark"""
        self.spark.stop()
        logger.info("✓ Spark Session arrêtée")
