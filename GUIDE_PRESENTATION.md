# 🎓 GUIDE DE PRÉSENTATION - TP Moteur de Recherche Sémantique

## 📋 Format de la démonstration

Vous avez **3 options** pour présenter ce TP:

---

## Option 1️⃣ : **Démonstration Interactive en CLI** (Recommandée)

### ✅ Avantages:
- Simple et rapide à exécuter
- Aucune dépendance web
- Montre bien les résultats réels
- Parfait pour une présentation en classe

### 🚀 Exécution:

```bash
# Activer le venv
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"

# Lancer la démo
python demo_interactive.py
```

### 📊 Ce que vous verrez:

```
================================================================================
🚀 DÉMONSTRATION - Moteur de Recherche Sémantique Big Data
================================================================================

4 CAS D'USAGE À EXPLORER:

   1. Recherche de logs similaires à une erreur
   2. Identification des groupes d'erreurs fréquentes
   3. Analyse de l'évolution temporelle
   4. Comparaison sémantique vs mot-clé
   5. Exécuter tous les cas
   0. Quitter

Choisissez (0-5): 
```

### 💡 Scénario de présentation:

```
┌─────────────────────────────────────────────────┐
│ Choisir option 5 pour exécuter TOUS les cas     │
│ Cela montre:                                    │
│  1. Recherche sémantique (similarité 81-82%)    │
│  2. Clustering K-Means (3-5 clusters)           │
│  3. Distribution temporelle (graphique)         │
│  4. Comparaison approches (5 résultats chacune) │
└─────────────────────────────────────────────────┘
```

---

## Option 2️⃣ : **Interface Web Streamlit**

### ✅ Avantages:
- Visuellement attractive
- Interface interactive et moderne
- Parfait pour une soutenance visuelle
- Tableaux et graphiques intégrés

### 🚀 Exécution:

```bash
# Activer le venv
.\venv\Scripts\Activate.ps1

# Installer streamlit (si nécessaire)
pip install streamlit

# Lancer l'interface
streamlit run app_streamlit.py
```

### 📊 Ce que vous verrez:

```
Interface web avec:
  ├─ 🏠 Page d'accueil (architecture, objectifs)
  ├─ 🔍 Cas 1: Recherche sémantique interactive
  ├─ 👥 Cas 2: Clustering avec graphiques
  ├─ 📊 Cas 3: Analyse temporelle (line chart)
  ├─ ⚖️  Cas 4: Comparaison visuelle
  └─ 📈 Statistiques globales
```

S'ouvrira dans le navigateur à: `http://localhost:8501`

---

## Option 3️⃣ : **Scripts Python simples**

### Pour cas d'usage spécifique:

#### Cas 1 - Recherche sémantique:
```bash
python -c "
from src.semantic_search import SemanticSearchEngine
engine = SemanticSearchEngine()
results = engine.search_by_error('Database timeout', top_k=5)
for r in results:
    print(f\"- {r['text'][:80]}... (similarité: {r['similarity']*100:.1f}%)\")
"
```

#### Cas 2 - Clustering:
```bash
python -c "
from src.semantic_search import SemanticSearchEngine
engine = SemanticSearchEngine()
clusters = engine.find_error_clusters(n_clusters=3)
for cid, info in clusters.items():
    print(f\"Cluster {cid}: {info['size']} logs\")
"
```

---

## 🎯 PLAN DE PRÉSENTATION COMPLET (15-20 minutes)

### ⏰ Timing recommandé:

**1. Introduction (2 min)**
```
- Contexte: Logs massifs difficiles à exploiter
- Objectif: Recherche sémantique efficace
- Approche: Embeddings + vectorisation + index
```

**2. Architecture (3 min)**
```
Montrer le pipeline:
Dataset (100K logs)
    ↓ [Spark - Phase 2]
Traitement batch
    ↓ [Sentence-Transformers - Phase 3]
Vectorisation (384-dim)
    ↓ [PostgreSQL+pgvector - Phase 4]
Index IVFFlat
    ↓
Recherche sémantique
```

**3. Démonstration live (10 min)**

```
Exécuter: python demo_interactive.py

Cas 1 (2 min):
  - Requête: "Database connection timeout"
  - Résultats: 5 logs similaires (81-82%)
  - Montrer que les résultats FONT SENS

Cas 2 (2 min):
  - Clustering K-Means des erreurs
  - 3 clusters avec 1875, 1900, 1225 logs
  - Centroïdes des clusters

Cas 3 (2 min):
  - Distribution temporelle
  - Montrer comment les erreurs évoluent

Cas 4 (2 min):
  - Comparaison sémantique vs mot-clé
  - Montrer la différence fondamentale
```

**4. Conclusions (3 min)**
```
- ✅ Tous les cas d'usage fonctionnent
- ✅ Vectorisation efficace (100K logs en ~80s)
- ✅ Recherche rapide (<1s)
- ✅ Clustering révèle patterns cachés
```

---

## 📊 DONNÉES QUE VOUS PRÉSENTEREZ

### **Cas 1 - Recherche sémantique:**
```
Requête: "Database connection timeout error"

✓ 5 logs similaires trouvés:

  1. [Similarité: 82.09%]
     Level: ERROR
     Texte: 2026-02-06 10:04:12 [ERROR] Database connection 
             timeout after 30 seconds - Host: db-server-7...

  2. [Similarité: 81.95%]
     Level: ERROR
     Texte: 2026-02-06 10:04:13 [ERROR] Database connection 
             timeout after 30 seconds - Host: db-server-7...
  
  ... (3 résultats supplémentaires)
```

### **Cas 2 - Clustering:**
```
✓ 3 clusters identifiés:
  Cluster 0: 1875 logs
  Cluster 1: 1900 logs
  Cluster 2: 1225 logs

Total: 5000 logs d'erreur analysés
```

### **Cas 3 - Analyse temporelle:**
```
Distribution temporelle pour "connection error":

2026-02-06: ████████████████ (1000 erreurs)

Pattern: Erreurs concentrées sur cette période
```

### **Cas 4 - Comparaison:**
```
Requête: "timeout"

Recherche sémantique: 5 résultats
  - Capture tous les logs relatifs aux timeout
  - Même avec formulations différentes

Recherche mot-clé: 5 résultats
  - Uniquement occurrences exactes de "timeout"
  - Peut manquer des variantes
```

---

## 💾 FICHIERS À AVOIR PRÊTS

```
Avant la présentation, assurez-vous d'avoir:

✅ demo_interactive.py      (pour la démo CLI)
✅ app_streamlit.py         (pour l'interface web)
✅ src/semantic_search.py   (moteur de recherche)
✅ src/database.py          (requêtes PostgreSQL)
✅ BILAN_FINAL.md           (référence rapide)
```

---

## 🖥️ CONFIGURATION TERMINAL

### **Pour éviter les erreurs d'encodage UTF-8 sous Windows:**

```powershell
# Avant chaque lancement:
$env:PYTHONIOENCODING="utf-8"

# Puis:
.\venv\Scripts\Activate.ps1
python demo_interactive.py
```

---

## 📝 POINTS CLÉS À ABORDER

### **Pourquoi cette approche est meilleure que la recherche par mot-clé?**

```
Exemple concret:

Requête: "connection problem"

❌ Mot-clé seul: Ne trouve que "connection" + "problem"
   Manque: "timeout", "refused", "unavailable", etc.

✅ Sémantique: Comprend le SENS
   Trouve: Tous les types de problèmes de connexion
   Même avec mots différents
```

### **Défis du Big Data résolus:**

```
1. VOLUME (100K logs)
   → Spark distribue le traitement
   
2. VECTORISATION (384 dimensions)
   → Sentence-Transformers en batch
   
3. RECHERCHE RAPIDE
   → Index IVFFlat (approximé mais rapide)
   
4. PATTERN DETECTION
   → K-Means clustering sur embeddings
```

---

## ✨ TIPS POUR UNE BONNE PRÉSENTATION

### ✅ À FAIRE:
- [x] Tester la démo AVANT (vérifier PostgreSQL)
- [x] Garder le terminal visible
- [x] Montrer les logs réels retournés
- [x] Expliquer les pourcentages de similarité
- [x] Comparer sémantique vs mot-clé côte à côte

### ❌ À ÉVITER:
- [ ] Corriger les erreurs de connexion en live
- [ ] Parler de détails techniques inutiles
- [ ] Ignorer les cas d'usage pratiques
- [ ] Lancer plusieurs démos simultanément

---

## 🎬 SCRIPT DE PRÉSENTATION EXEMPLE

```
"Bonjour, je présente un moteur de recherche sémantique sur logs.

Les systèmes Big Data génèrent des millions de logs par jour.
Trouver une erreur spécifique est très difficile avec la recherche 
par mot-clé classique.

Notre solution utilise:
1. Apache Spark pour ingérer 100,000 logs
2. Sentence-Transformers pour créer des embeddings sémantiques
3. PostgreSQL + pgvector pour indexer et rechercher rapidement
4. Clustering pour identifier patterns d'erreurs

Je vais montrer 4 cas pratiques...

[EXÉCUTER demo_interactive.py]

Comme vous voyez, en cherchant 'Database timeout error', 
on trouve 5 logs SIMILAIRES avec 81-82% de compatibilité.

Les approches traditionnelles ne trouveraient que les logs 
contenant exactement "timeout"...

[CONTINUER AVEC CAS 2, 3, 4]"
```

---

## 🏆 QUESTIONS À ANTICIPER

### **Q: Comment ça fonctionne vraiment?**
R: Les embeddings convertissent chaque log en vecteur de 384 dimensions.
   Deux logs similaires auront des vecteurs proches.
   La distance cosinus mesure cette proximité (0-1).

### **Q: Pourquoi pgvector?**
R: Permet de stocker les embeddings directement dans PostgreSQL
   avec des index spécialisés (IVFFlat) pour recherche rapide.

### **Q: Performance?**
R: Vectorisation: ~80 sec pour 100K logs
   Recherche: <1 sec pour find 5 similaires
   Clustering: ~2 sec pour K-Means sur 5000 logs

### **Q: Scalabilité?**
R: Spark permet de traiter des millions de logs
   pgvector peut indexer des millions d'embeddings
   À tester en prod sur plus gros volumes.

---

## 📚 RÉFÉRENCES À MENTIONNER

```
- Sentence-Transformers: https://www.sbert.net/
- PostgreSQL pgvector: https://github.com/pgvector/pgvector
- Apache Spark: https://spark.apache.org/
- Clustering K-Means: scikit-learn
```

---

**Bon courage pour votre présentation! 🚀**
