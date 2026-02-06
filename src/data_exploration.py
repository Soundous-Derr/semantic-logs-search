"""
Phase 1: Analyse et exploration du dataset de logs
Objectif: Étudier le volume, le format et la structure des données
"""

import pandas as pd
import numpy as np
import json
import re
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt

class DataExploration:
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        self.logs = []
        self.stats = {}
        
    def load_logs(self, sample_size=None):
        """Charge les logs depuis un fichier texte"""
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if sample_size:
                self.logs = lines[:sample_size]
            else:
                self.logs = lines
                
            print(f"✓ Chargement: {len(self.logs)} logs")
            return self.logs
        except Exception as e:
            print(f"✗ Erreur lors du chargement: {e}")
            return None
    
    def analyze_log_format(self):
        """Analyse le format des logs"""
        print("\n" + "="*60)
        print("📊 ANALYSE DU FORMAT DES LOGS")
        print("="*60)
        
        samples = self.logs[:5]
        print("\n📄 Exemples de logs:")
        for i, log in enumerate(samples, 1):
            print(f"{i}. {log.strip()[:100]}...")
        
        # Détection du format
        format_types = {
            'apache': 0,
            'syslog': 0,
            'json': 0,
            'text_libre': 0
        }
        
        for log in self.logs[:1000]:
            if 'HTTP' in log or log[0].isdigit() and '.' in log:
                format_types['apache'] += 1
            elif '[' in log and ']' in log:
                format_types['syslog'] += 1
            elif log.startswith('{'):
                format_types['json'] += 1
            else:
                format_types['text_libre'] += 1
        
        print(f"\n📋 Distribution des formats détectés:")
        for fmt, count in format_types.items():
            print(f"   {fmt}: {count}")
    
    def analyze_volume_statistics(self):
        """Analyse les statistiques de volume"""
        print("\n" + "="*60)
        print("📈 STATISTIQUES DE VOLUME")
        print("="*60)
        
        total_logs = len(self.logs)
        total_chars = sum(len(log) for log in self.logs)
        avg_length = total_chars / total_logs if total_logs > 0 else 0
        
        lengths = [len(log) for log in self.logs]
        
        stats = {
            'total_logs': total_logs,
            'total_bytes': total_chars,
            'avg_log_length': avg_length,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0,
            'median_length': float(np.median(lengths)) if lengths else 0,
            'std_length': float(np.std(lengths)) if lengths else 0
        }
        
        print(f"\n📊 Résumé des statistiques:")
        print(f"   Nombre total de logs: {stats['total_logs']:,}")
        print(f"   Taille totale: {stats['total_bytes'] / (1024*1024):.2f} MB")
        print(f"   Longueur moyenne: {stats['avg_log_length']:.0f} caractères")
        print(f"   Longueur min/max: {stats['min_length']} / {stats['max_length']}")
        print(f"   Médiane: {stats['median_length']:.0f}")
        print(f"   Écart-type: {stats['std_length']:.0f}")
        
        self.stats.update(stats)
        return stats
    
    def analyze_error_patterns(self):
        """Détecte les patterns d'erreurs récurrentes"""
        print("\n" + "="*60)
        print("🔍 ANALYSE DES PATTERNS D'ERREURS")
        print("="*60)
        
        error_keywords = ['error', 'exception', 'failed', 'critical', 'warning', 
                         'ERROR', 'FATAL', 'Exception', 'timeout']
        
        error_logs = []
        for log in self.logs:
            if any(keyword.lower() in log.lower() for keyword in error_keywords):
                error_logs.append(log)
        
        error_rate = (len(error_logs) / len(self.logs) * 100) if self.logs else 0
        
        print(f"\n🚨 Résultats:")
        print(f"   Total logs avec erreurs: {len(error_logs):,} ({error_rate:.2f}%)")
        
        if error_logs:
            print(f"\n   Top 5 erreurs détectées:")
            error_counter = Counter()
            for log in error_logs:
                match = re.search(r'(Error|Exception|Failed).*?:', log)
                if match:
                    error_counter[match.group(0)] += 1
            
            for i, (error, count) in enumerate(error_counter.most_common(5), 1):
                print(f"   {i}. {error[:60]}... ({count})")
        
        self.stats['error_count'] = len(error_logs)
        self.stats['error_rate'] = error_rate
        return error_logs
    
    def analyze_temporal_distribution(self):
        """Analyse la distribution temporelle des logs"""
        print("\n" + "="*60)
        print("⏰ DISTRIBUTION TEMPORELLE")
        print("="*60)
        
        timestamps = []
        date_pattern = r'\d{4}-\d{2}-\d{2}|\d{2}/\w+/\d{4}'
        
        for log in self.logs[:10000]:
            match = re.search(date_pattern, log)
            if match:
                timestamps.append(match.group(0))
        
        if timestamps:
            print(f"\n📅 Timestamps trouvés: {len(timestamps)} / {min(10000, len(self.logs))}")
            print(f"   Période: {timestamps[0]} à {timestamps[-1]}")
        else:
            print(f"\n📅 Aucun timestamp détecté dans le format standard")
    
    def analyze_vocabulary(self):
        """Analyse le vocabulaire des logs"""
        print("\n" + "="*60)
        print("📚 ANALYSE DU VOCABULAIRE")
        print("="*60)
        
        words = []
        for log in self.logs[:10000]:
            log_words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', log)
            words.extend(log_words)
        
        vocab_size = len(set(words))
        
        print(f"\n📝 Résultats:")
        print(f"   Vocabulaire unique: {vocab_size:,} mots")
        print(f"   Total mots: {len(words):,}")
        print(f"   Densité: {vocab_size/len(words)*100:.2f}%")
        
        print(f"\n   Top 10 mots les plus fréquents:")
        word_counter = Counter(words)
        for i, (word, count) in enumerate(word_counter.most_common(10), 1):
            print(f"   {i}. '{word}': {count}")
        
        self.stats['vocabulary_size'] = vocab_size
        return words
    
    def generate_report(self):
        """Génère un rapport d'analyse complet"""
        print("\n" + "="*70)
        print("📋 RAPPORT D'ANALYSE - PHASE 1")
        print("="*70)
        
        self.load_logs()
        self.analyze_log_format()
        self.analyze_volume_statistics()
        self.analyze_error_patterns()
        self.analyze_temporal_distribution()
        self.analyze_vocabulary()
        
        print("\n" + "="*70)
        print("📊 CONCLUSIONS ET RECOMMANDATIONS")
        print("="*70)
        
        total = self.stats.get('total_logs', 0)
        volume_mb = self.stats.get('total_bytes', 0) / (1024*1024)
        
        print(f"\n✓ Dataset: {total:,} logs ({volume_mb:.2f} MB)")
        print(f"✓ Format majoritaire: logs textuels/Apache")
        print(f"✓ Taux d'erreurs: {self.stats.get('error_rate', 0):.2f}%")
        print(f"✓ Vocabulaire: {self.stats.get('vocabulary_size', 0):,} mots uniques")
        
        print(f"\n💡 Recommandations Spark:")
        num_partitions = max(4, total // 100000)
        print(f"   - Partitions recommandées: {num_partitions}")
        print(f"   - Batch size (embeddings): 1000 logs")
        print(f"   - Encoding: UTF-8 avec gestion des erreurs")
        
        return self.stats


if __name__ == "__main__":
    explorer = DataExploration("data/raw/sample_logs.txt")
    stats = explorer.generate_report()
    
    with open("data/analysis_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    print("\n✓ Statistiques sauvegardées dans data/analysis_stats.json")