"""
Génère des logs d'exemple sans tqdm
"""

import os
import random
from pathlib import Path

class LogDataDownloader:
    def __init__(self):
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_sample_logs(self, num_logs=10000):  # Réduit à 10K pour tester
        sample_file = self.data_dir / "sample_logs.txt"
        
        if sample_file.exists():
            print(f"✓ Fichier existe déjà: {sample_file}")
            return str(sample_file)
        
        log_templates = [
            "2026-02-06 10:{minute:02d}:{second:02d} [ERROR] Database connection timeout",
            "2026-02-06 10:{minute:02d}:{second:02d} [WARNING] High memory usage: {memory}%",
            "2026-02-06 10:{minute:02d}:{second:02d} [INFO] User login from IP {ip}",
            "2026-02-06 10:{minute:02d}:{second:02d} [ERROR] Out of memory exception",
            "2026-02-06 10:{minute:02d}:{second:02d} [CRITICAL] System panic detected",
        ]
        
        print(f"Génération de {num_logs:,} logs...")
        
        with open(sample_file, 'w') as f:
            for i in range(num_logs):
                template = random.choice(log_templates)
                log_line = template.format(
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59),
                    memory=random.randint(85, 99),
                    ip=f"192.168.1.{random.randint(1, 255)}"
                )
                f.write(log_line + f" [id:{i}]\n")
        
        file_size_mb = sample_file.stat().st_size / (1024 * 1024)
        print(f"✓ Logs créés: {sample_file} ({file_size_mb:.2f} MB)")
        return str(sample_file)
    
    def run(self):
        print("="*60)
        print("🚀 GÉNÉRATION DES DONNÉES")
        print("="*60)
        self.generate_sample_logs()
        print("✅ Données prêtes!")

if __name__ == "__main__":
    downloader = LogDataDownloader()
    downloader.run()