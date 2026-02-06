"""
Télécharge les datasets publics LogHub (HDFS, Hadoop, etc.)
"""

import os
import requests
import gzip
import shutil
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogDataDownloader:
    def __init__(self):
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_sample_logs(self):
        """Génère des logs d'exemple"""
        
        print("\n" + "="*60)
        print("🔧 Génération de logs d'exemple")
        print("="*60)
        
        sample_file = self.data_dir / "sample_logs.txt"
        
        if sample_file.exists():
            print(f"✓ Fichier d'exemple existe déjà: {sample_file}")
            return
        
        log_templates = [
            "2026-02-06 10:23:45 [ERROR] Database connection timeout after 30 seconds",
            "2026-02-06 10:24:12 [WARNING] High memory usage detected: 92% utilization",
            "2026-02-06 10:25:01 [INFO] User login successful from IP 192.168.1.100",
            "2026-02-06 10:26:33 [ERROR] Out of memory exception in process PID 5432",
            "2026-02-06 10:27:45 [ERROR] Permission denied: access to /var/secure/data",
            "2026-02-06 10:28:10 [CRITICAL] System panic: kernel error detected",
            "2026-02-06 10:29:22 [WARNING] Disk space low: 5% remaining",
            "2026-02-06 10:30:01 [ERROR] Network interface eth0 down",
            "2026-02-06 10:31:15 [INFO] Database backup completed successfully",
            "2026-02-06 10:32:44 [ERROR] Connection refused on port 5432",
            "2026-02-06 10:33:52 [WARNING] SSL certificate will expire in 30 days",
            "2026-02-06 10:34:27 [ERROR] Invalid user authentication attempt",
        ]
        
        print(f"✍️  Génération de 100,000 logs d'exemple...")
        with open(sample_file, 'w') as f:
            for i in range(100000):
                log = log_templates[i % len(log_templates)]
                f.write(log + f" [occurrence {i}]\n")
        
        file_size_mb = sample_file.stat().st_size / (1024 * 1024)
        logger.info(f"✓ Logs d'exemple créés: {sample_file} ({file_size_mb:.2f} MB)")
    
    def run(self):
        """Exécute le téléchargement complet"""
        
        print("\n" + "="*70)
        print("🚀 TÉLÉCHARGEMENT DES DONNÉES")
        print("="*70)
        
        self.generate_sample_logs()
        
        print("\n✅ Données prêtes pour le traitement!")


if __name__ == "__main__":
    downloader = LogDataDownloader()
    downloader.run()