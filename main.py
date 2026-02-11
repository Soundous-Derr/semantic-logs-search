"""
Pipeline Principal - Orchestre toutes les phases
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class MainPipeline:
    def __init__(self, sample: bool = False):
        self.data_raw = Path("data/raw/sample_logs.txt")
        self.data_processed = Path("data/processed/logs_parsed")
        self.sample = sample
        self.sample_parquet = Path("data/processed/logs_parsed_sample")
    
    def validate_environment(self):
        """Vérifie que tout est prêt"""
        print("\n" + "="*70)
        print("✅ VALIDATION DE L'ENVIRONNEMENT")
        print("="*70)
        
        if not self.data_raw.exists():
            print(f"✗ Fichier de données manquant: {self.data_raw}")
            return False
        
        print(f"✓ Données trouvées: {self.data_raw}")
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'sound2003'),
                database='semantic_logs',
                port='5432'
            )
            conn.close()
            print("✓ PostgreSQL accessible")
        except Exception as e:
            print(f"✗ Erreur PostgreSQL: {e}")
            return False
        
        return True
    
    def run_phase_1(self):
        """Phase 1: Exploration des données"""
        from src.data_exploration import DataExploration
        
        print("\n" + "="*70)
        print("📊 PHASE 1: EXPLORATION DES DONNÉES")
        print("="*70)
        
        explorer = DataExploration(str(self.data_raw))
        stats = explorer.generate_report()
        return True
    
    def run_phase_2(self):
        """Phase 2: Traitement Spark avec Hadoop"""
        import os
        import sys
        
        # Configuration
        java_path = r"C:\Program Files\Eclipse Adoptium\jdk-17.0.16.8-hotspot"
        os.environ['JAVA_HOME'] = java_path
        os.environ['HADOOP_HOME'] = r"C:\hadoop"
        os.environ['PYSPARK_PYTHON'] = sys.executable
        os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
        
        import findspark
        findspark.init()
        
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import regexp_extract, col
        
        print("\n" + "="*70)
        print("🚀 PHASE 2: INGESTION ET TRAITEMENT SPARK")
        print("="*70)
        
        spark = SparkSession.builder \
            .appName("SemanticLogs") \
            .master("local[*]") \
            .getOrCreate()
        
        # Lecture
        df = spark.read.text("data/raw/sample_logs.txt")
        print(f"✓ {df.count():,} logs chargés")
        
        # Parsing
        df = df.withColumn("timestamp", regexp_extract(col("value"), r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", 1)) \
               .withColumn("level", regexp_extract(col("value"), r"\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]", 1))
        
        # Aperçu
        print("\n📊 Aperçu:")
        df.show(5, truncate=False)
        
        print("\n📈 Distribution:")
        df.groupBy("level").count().orderBy(col("count").desc()).show()
        
        # Sauvegarde Parquet
        os.makedirs("data/processed", exist_ok=True)
        df.write.mode("overwrite").parquet("data/processed/logs_parsed")
        
        print("\n💾 Données sauvegardées: data/processed/logs_parsed")
        spark.stop()
        print("✅ Phase 2 terminée avec succès!")
        return True

    def run_phase_3(self):
        """Phase 3: Vectorisation"""
        from src.vectorization import VectorizationPipeline
        
        print("\n" + "="*70)
        print("🔢 PHASE 3: VECTORISATION ET INDEXATION")
        print("="*70)
        
        pipeline = VectorizationPipeline()
        # Utiliser le bon chemin (échantillon si demandé)
        parquet_path = str(self.sample_parquet) if self.sample else str(self.data_processed)
        return pipeline.run(parquet_path)
    
    def run_phase_4(self):
        """Phase 4: Recherche et analyse"""
        print("\n" + "="*70)
        print("🔍 PHASE 4: RECHERCHE SÉMANTIQUE ET ANALYSE")
        print("="*70)
        
        from src.semantic_search import run_demo
        run_demo()
        return True
    
    def run_all_phases(self):
        """Exécute toutes les phases"""
        start_time = datetime.now()
        
        try:
            if not self.validate_environment():
                logger.error("❌ Environnement invalide")
                return False
            
            phases = [
                ("Phase 1: Exploration", self.run_phase_1),
                ("Phase 2: Traitement Spark", self.run_phase_2),
                ("Phase 3: Vectorisation", self.run_phase_3),
                ("Phase 4: Recherche", self.run_phase_4),
            ]
            
            for phase_name, phase_func in phases:
                try:
                    print(f"\n{'='*70}")
                    print(f"▶️  {phase_name}")
                    print(f"{'='*70}")
                    success = phase_func()
                    if not success:
                        logger.error(f"❌ Échec de {phase_name}")
                        return False
                    # Après la Phase 2, créer un parquet échantillon si demandé
                    if success and phase_name.startswith("Phase 2") and self.sample:
                        try:
                            print("\n⏳ Création d'un parquet échantillon pour accélérer la vectorisation...")
                            # utiliser le Python courant pour exécuter le créateur d'échantillon
                            subprocess.run([sys.executable, "create_sample_parquet.py"], check=True)
                            print("✅ Parquet échantillon créé: data/processed/logs_parsed_sample")
                        except Exception as e:
                            logger.warning(f"⚠️  Échec création du parquet échantillon: {e}")
                except Exception as e:
                    logger.error(f"❌ Erreur dans {phase_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            
            elapsed = (datetime.now() - start_time).total_seconds()
            minutes = elapsed / 60
            
            print("\n" + "="*70)
            print("✅ PIPELINE COMPLÉTÉ AVEC SUCCÈS!")
            print("="*70)
            print(f"Temps total: {minutes:.1f} minutes")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Erreur fatale: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_specific_phase(self, phase_num):
        """Exécute une phase spécifique"""
        phases = {
            1: self.run_phase_1,
            2: self.run_phase_2,
            3: self.run_phase_3,
            4: self.run_phase_4,
        }
        
        if phase_num not in phases:
            logger.error(f"Phase inconnue: {phase_num}")
            return False
        
        try:
            if not self.validate_environment():
                return False
            return phases[phase_num]()
        except Exception as e:
            logger.error(f"Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Pipeline Semantic Logs Search - TP Big Data'
    )
    parser.add_argument(
        '--phase',
        type=int,
        choices=[1, 2, 3, 4],
        help='Exécuter une phase spécifique (1, 2, 3, ou 4)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use a sampled parquet for faster vectorization (creates/uses data/processed/logs_parsed_sample)'
    )
    
    args = parser.parse_args()

    pipeline = MainPipeline(sample=getattr(args, 'sample', False))
    
    if args.phase:
        success = pipeline.run_specific_phase(args.phase)
        sys.exit(0 if success else 1)
    
    success = pipeline.run_all_phases()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()