# 🚀 Moteur de Recherche Sémantique et Analytique sur Logs Big Data

**TP Avancé - Module Bases de Données Avancées**

![Status](https://img.shields.io/badge/status-Functional-brightgreen)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Spark](https://img.shields.io/badge/spark-3.5-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)

## 🎯 Objectifs

✅ Ingérer 500K+ logs massifs  
✅ Vectoriser avec Sentence-Transformers  
✅ Stocker dans PostgreSQL + pgvector  
✅ Recherche sémantique rapide  
✅ Analyser automatiquement les patterns  

## 🚀 Quick Start

```bash
# 1. Clone & Setup
git clone https://github.com/Soundous-Derr/semantic-logs-search.git
cd semantic-logs-search

# 2. Installation
chmod +x setup.sh
./setup.sh

# 3. Données
python download_data.py

# 4. Pipeline
python main.py