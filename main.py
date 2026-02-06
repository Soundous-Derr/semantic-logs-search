"""
Pipeline Principal - Orchestre toutes les phases
Exécutez avec: python main.py
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Import des phases
from src.data_exploration import DataExploration
from src.spark_pipeline import SparkLogsPipeline
from src.vectorization import VectorizationPipeline
from src.semantic_search import SemanticSearchEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class MainPipeline:
    def __init__(self, phase=None):
        self.phase = phase
        self.data_raw = Path("data/raw/sample_logs.txt")
        self.data_processed = Path("data/processed_logs")
    
    def validate_environment(self):
        """Vérifie que tout est prêt"""
        print("\n" + "="*70)
        print("✅ VALIDATION DE L'ENVIRONNEMENT")
        print("="*70)
        
        if not self.data_raw.exists():
            print(f"✗ Fichier de données manquant: {self.data_raw}")
            print("  Lancez: python download_data.py")
            return False
        
        print(f"✓ Données trouvées: {self.data_raw}")
        
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'logadmin'),
                password=os.getenv('DB_PASSWORD', 'logsearch2024'),
                database='postgres'
            )
            conn.close()
            print("✓ PostgreSQL + pgvector opérationnel")
        except Exception as e:
            print(f"✗ Erreur PostgreSQL: {e}")
            return False
        
        return True
    
    def run_phase_1(self):
        """Phase 1: Exploration des données"""
        print("\n" + "="*70)
        print("📊 PHASE 1: EXPLORATION DES DONNÉES")
        print("="*70)
        
        explorer = DataExploration(str(self.data_raw))
        explorer.generate_report()
        
        return True
    
    def run_phase_2(self):
        """Phase 2: Ingestion et traitement Spark"""
        print("\n" + "="*70)
        print("🚀 PHASE 2: INGESTION ET TRAITEMENT SPARK")
        print("="*70)
        
        pipeline = SparkLogsPipeline()
        df = pipeline.run_full_pipeline(
            str(self.data_raw),
            str(self.data_processed)
        )
        
        return True
    
    def run_phase_3(self):
        """Phase 3: Vectorisation"""
        print("\n" + "="*70)
        print("🔢 PHASE 3: VECTORISATION ET INDEXATION")
        print("="*70)
        
        pipeline = VectorizationPipeline()
        pipeline.run(str(self.data_processed))
        
        return True
    
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
                ("Phase 1", self.run_phase_1),
                ("Phase 2", self.run_phase_2),
                ("Phase 3", self.run_phase_3),
                ("Phase 4", self.run_phase_4),
            ]
            
            for phase_name, phase_func in phases:
                try:
                    print(f"\n{'='*70}")
                    print(f"▶️  {phase_name}")
                    print(f"{'='*70}")
                    phase_func()
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
        '--setup-only',
        action='store_true',
        help='Seulement vérifier la configuration'
    )
    
    args = parser.parse_args()
    
    pipeline = MainPipeline()
    
    if args.setup_only:
        success = pipeline.validate_environment()
        sys.exit(0 if success else 1)
    
    if args.phase:
        success = pipeline.run_specific_phase(args.phase)
        sys.exit(0 if success else 1)
    
    success = pipeline.run_all_phases()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()