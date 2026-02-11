# 🎯 COMMENT FAIRE LA DÉMONSTRATION

## ⚡ Quick Start (2 minutes)

```bash
# 1. Activer l'environnement
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"

# 2. Lancer la démo simple
python demo_simple.py
```

C'est tout! Vous verrez tous les cas d'usage fonctionner.

---

## 🎨 3 Options de Démonstration

### **Option 1: Démo Simple (Recommandée) ⭐**

```bash
python demo_simple.py
```

**Affiche:**
- ✅ 4 cas d'usage séquentiels
- ✅ Résultats réels avec logs et pourcentages
- ✅ Statistiques comparatives
- ✅ Temps d'exécution

**Avantages:**
- Pas de dépendances extra
- Clair et professionnel
- Parfait pour une présentation en classe

---

### **Option 2: Démo Interactive (Menu)**

```bash
python demo_interactive.py
```

**Affiche:**
- Menu interactif coloré
- Choix des cas d'usage
- Exécution individuelle ou ensemble

**Avantages:**
- Plus de contrôle
- Choisir ce qu'on montre
- Interface attrayante

---

### **Option 3: Interface Web (Streamlit)**

```bash
pip install streamlit
streamlit run app_streamlit.py
```

**Affiche:**
- Interface web moderne
- Graphiques interactifs
- Tableaux de données
- Page d'accueil avec architecture

**Avantages:**
- Très visuellement attractif
- Parfait pour une vidéo/soutenance
- S'ouvre dans le navigateur

---

## 📋 Avant la Présentation

### Checklist:

```
☑️ PostgreSQL est démarré et accessible
☑️ Venv activé
☑️ PYTHONIOENCODING=utf-8 défini
☑️ Tester une démo: python demo_simple.py
☑️ Vérifier que tout fonctionne
☑️ Avoir GUIDE_PRESENTATION.md à proximité
```

### Vérifier la base:

```bash
python -c "
from src.database import VectorDatabase
db = VectorDatabase()
if db.connect():
    stats = db.get_statistics()
    print(f'✅ {stats[\"total_logs\"]:,} logs')
    print(f'✅ {stats[\"total_embeddings\"]:,} embeddings')
else:
    print('❌ Pas de connexion PostgreSQL')
"
```

---

## ⏱️ Timing pour la Présentation

### **Structure 20 minutes:**

```
0-2 min:   Introduction et contexte
2-5 min:   Architecture (montrer diagramme)
5-7 min:   Cas 1 - Recherche sémantique
7-9 min:   Cas 2 - Clustering d'erreurs
9-11 min:  Cas 3 - Analyse temporelle
11-13 min: Cas 4 - Comparaison
13-15 min: Résultats et conclusions
15-20 min: Questions/discussions
```

---

## 🚀 Commandes Exactes à Copier-Coller

### Pour demo simple:
```powershell
cd C:\Users\ADMIN\Desktop\semantic-logs-search
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"
python demo_simple.py
```

### Pour demo interactive:
```powershell
cd C:\Users\ADMIN\Desktop\semantic-logs-search
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"
python demo_interactive.py
```

### Pour Streamlit:
```powershell
cd C:\Users\ADMIN\Desktop\semantic-logs-search
.\venv\Scripts\Activate.ps1
pip install streamlit
streamlit run app_streamlit.py
```

---

## 📊 Ce Que Vous Verrez

### **Cas 1 - Résultats attendus:**
```
Requête: "Database connection timeout error"

✓ 5 logs similaires trouvés:

1. [Similarité: 82.09%] ERROR
   2026-02-06 10:04:12 [ERROR] Database connection timeout...

2. [Similarité: 81.95%] ERROR
   2026-02-06 10:04:13 [ERROR] Database connection timeout...

... (3 autres résultats)

Similarité moyenne: 81.93%
```

### **Cas 2 - Résultats attendus:**
```
✓ 3 clusters identifiés:

Cluster 0:
   Taille: 1875 logs
   Centroïde (dims 1-5): [0.234, -0.123, 0.456, ...]

Cluster 1:
   Taille: 1900 logs
   Centroïde (dims 1-5): [0.100, 0.200, -0.350, ...]

Cluster 2:
   Taille: 1225 logs
   Centroïde (dims 1-5): [-0.180, 0.340, 0.210, ...]

Total analysé: 5000 logs d'erreur
```

### **Cas 3 - Résultats attendus:**
```
Motif recherché: "connection error"

✓ Distribution temporelle:

2026-02-06: ████████████████ (1000 erreurs)
```

### **Cas 4 - Résultats attendus:**
```
Requête: "timeout"

1️⃣  RECHERCHE SÉMANTIQUE
✓ 5 résultats par similarité

1. [81.5%] Database connection timeout...
2. [80.2%] Network timeout on port 8080...
3. [79.8%] API call timeout after 30s...

2️⃣  RECHERCHE PAR MOT-CLÉ
✓ 5 résultats par occurrence

1. Database connection timeout after...
2. Network timeout on port 8080...
3. API call timeout after 30s...

DIFFÉRENCES CLÉS:
• Sémantique capture le SENS
• Mot-clé cherche occurrences exactes
```

---

## 🛠️ Dépannage

### **Erreur: "Connection refused"**
```
→ PostgreSQL n'est pas lancé
→ Vérifier que le serveur est accessible
```

### **Erreur: "charmap codec"**
```
→ Définir PYTHONIOENCODING="utf-8" avant de lancer
```

### **Erreur: "Module not found"**
```
→ Vérifier que le venv est activé
→ Vérifier que pip install a fonctionné
```

### **Pas de résultats en base**
```
→ Les phases 2 et 3 n'ont pas été exécutées
→ Lancer: python main.py --phase 2
→ Puis:   python main.py --phase 3
→ Puis la démo
```

---

## 📈 Métriques de Performance Attendues

| Métrique | Valeur |
|----------|--------|
| Connexion DB | <1s |
| Recherche sémantique | 0.5-2s |
| Clustering K-Means | 2-5s |
| Analyse temporelle | <1s |
| Comparaison | <1s |

---

## 💡 Points à Bien Expliquer

### **Pourquoi les embeddings?**
```
- Convertissent du texte en vecteurs numériques
- Logs similaires → vecteurs proches
- Distance cosinus mesure la similarité
```

### **Pourquoi pgvector?**
```
- Stockage natif des embeddings
- Index IVFFlat pour recherche rapide
- Scalable pour millions d'embeddings
```

### **Pourquoi clustering?**
```
- Groupe les logs similaires
- Révèle les patterns d'erreurs
- Aide à la détection d'anomalies
```

---

## ✨ Final Check List

Avant de présenter:

- [ ] Base de données accessible
- [ ] Venv activé
- [ ] PYTHONIOENCODING défini
- [ ] Tester une démo complète
- [ ] Avoir le GUIDE_PRESENTATION.md
- [ ] Préparer des exemples de requêtes
- [ ] Tester le navigateur (si Streamlit)
- [ ] Avoir une sauvegarde de la démo en vidéo

---

## 🎬 Bon courage! 🚀

Vous avez tout ce qu'il faut pour une excellente présentation!
