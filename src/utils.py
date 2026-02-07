"""
Utilitaires communs pour tout le pipeline
"""

import logging
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_logger(name: str) -> logging.Logger:
    """Crée un logger configuré"""
    return logging.getLogger(name)

def normalize_log(log: str) -> str:
    """Normalise un log pour le traitement"""
    if not log:
        return ""
    log = log.strip()
    log = ' '.join(log.split())
    return log

def extract_timestamp(log: str) -> str:
    """Extrait le timestamp d'un log"""
    patterns = [
        r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, log)
        if match:
            return match.group(1)
    return None

def extract_log_level(log: str) -> str:
    """Extrait le niveau de log"""
    levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
    
    for level in levels:
        if f'[{level}]' in log or f' {level} ' in log:
            return level
    return 'UNKNOWN'

def extract_ip_address(log: str) -> str:
    """Extrait l'adresse IP d'un log"""
    pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    match = re.search(pattern, log)
    return match.group(0) if match else None

def save_json(data: Any, filepath: str) -> None:
    """Sauvegarde des données en JSON"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    get_logger(__name__).info(f"Données sauvegardées: {filepath}")

def load_json(filepath: str) -> Any:
    """Charge des données depuis JSON"""
    with open(filepath, 'r') as f:
        return json.load(f)

def batch_generator(items: List, batch_size: int):
    """Générateur pour traiter les données par lots"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]

def calculate_similarity_metrics(vector1: List[float], vector2: List[float]) -> Dict[str, float]:
    """Calcule les métriques de similarité entre deux vecteurs"""
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    
    cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    euclidean = np.linalg.norm(v1 - v2)
    manhattan = np.sum(np.abs(v1 - v2))
    
    return {
        'cosine_similarity': float(cosine),
        'euclidean_distance': float(euclidean),
        'manhattan_distance': float(manhattan)
    }