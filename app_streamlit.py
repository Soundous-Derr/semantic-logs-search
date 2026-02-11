"""
Interface Web Interactive - Démonstration Streamlit
Moteur de Recherche Sémantique sur Logs Big Data
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="🔍 Moteur de Recherche Sémantique - Logs",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de style
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 0.75rem 1.25rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_search_engine():
    """Charger le moteur de recherche (cached)"""
    try:
        from src.semantic_search import SemanticSearchEngine
        return SemanticSearchEngine()
    except Exception as e:
        st.error(f"Erreur lors du chargement du moteur: {e}")
        return None

def display_log_result(result, index):
    """Afficher un résultat de log avec formatage"""
    col1, col2 = st.columns([0.15, 0.85])
    
    with col1:
        if result.get('log_level') == 'CRITICAL':
            st.error(f"#{index}")
        elif result.get('log_level') == 'ERROR':
            st.warning(f"#{index}")
        else:
            st.info(f"#{index}")
    
    with col2:
        similarity = result.get('similarity', 0) * 100
        st.markdown(f"""
        **Similarité:** {similarity:.1f}%  |  **Niveau:** {result.get('log_level', 'UNKNOWN')}
        
        **Message:** {result.get('text', 'N/A')[:150]}...
        
        **Timestamp:** {result.get('timestamp', 'N/A')}
        """)
    st.divider()

def main():
    # Header
    st.markdown("# 🚀 Moteur de Recherche Sémantique - Logs Big Data")
    st.markdown("### Démonstration TP avancé avec Spark, PostgreSQL et Sentence-Transformers")
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Sélectionnez un cas d'usage:",
        [
            "🏠 Accueil",
            "🔍 Cas 1: Recherche sémantique",
            "👥 Cas 2: Clustering d'erreurs",
            "📊 Cas 3: Analyse temporelle",
            "⚖️ Cas 4: Comparaison sémantique vs mot-clé",
            "📈 Statistiques globales"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📚 Technologies utilisées:
    - **Ingestion**: Apache Spark
    - **Vectorisation**: Sentence-Transformers
    - **Base de données**: PostgreSQL + pgvector
    - **ML**: scikit-learn (K-Means)
    - **Frontend**: Streamlit
    """)
    
    # Contenu principal
    if page == "🏠 Accueil":
        display_home()
    elif page == "🔍 Cas 1: Recherche sémantique":
        display_case_1()
    elif page == "👥 Cas 2: Clustering d'erreurs":
        display_case_2()
    elif page == "📊 Cas 3: Analyse temporelle":
        display_case_3()
    elif page == "⚖️ Cas 4: Comparaison sémantique vs mot-clé":
        display_case_4()
    elif page == "📈 Statistiques globales":
        display_statistics()

def display_home():
    """Page d'accueil"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## 🎓 TP: Recherche Sémantique sur Logs Big Data
        
        ### Objectifs pédagogiques:
        1. **Ingérer** des données massives avec Apache Spark
        2. **Vectoriser** les logs avec Sentence-Transformers
        3. **Indexer** les embeddings dans PostgreSQL+pgvector
        4. **Rechercher** sémantiquement avec similarité cosinus
        5. **Analyser** les patterns d'erreurs récurrentes
        
        ### 4 cas d'usage pratiques:
        - ✅ Retrouver tous les logs similaires à une erreur critique
        - ✅ Identifier les groupes d'erreurs fréquentes
        - ✅ Analyser l'évolution temporelle des erreurs
        - ✅ Comparer recherche sémantique vs mot-clé
        """)
    
    with col2:
        st.info("""
        ### 📊 Architecture
        
        ```
        Dataset (100K logs)
           ↓
        Spark (Phase 2)
           ↓
        Vectorisation (Phase 3)
           ↓
        pgvector (Phase 4)
           ↓
        Recherche Sémantique
        ```
        """)
    
    st.markdown("---")
    
    # Statistiques rapides
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📦 Logs traités", "100,000")
    with col2:
        st.metric("🔢 Dimension embeddings", "384")
    with col3:
        st.metric("⚡ Index type", "IVFFlat")

def display_case_1():
    """Cas 1: Recherche sémantique"""
    st.markdown("## 🔍 Cas 1: Retrouver logs similaires à une erreur")
    
    engine = load_search_engine()
    if not engine:
        st.error("Impossible de charger le moteur de recherche")
        return
    
    # Entrée utilisateur
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Entrez une description d'erreur:",
            value="Database connection timeout error",
            help="Ex: 'Authentication failed', 'Memory overflow', etc."
        )
    
    with col2:
        top_k = st.slider("Nombre de résultats:", 1, 10, 5)
    
    if st.button("🔍 Rechercher", key="case1_search"):
        with st.spinner("Recherche en cours..."):
            try:
                results = engine.search_by_error(query, top_k=top_k)
                
                st.success(f"✅ {len(results)} logs similaires trouvés!")
                
                # Afficher les résultats
                st.markdown("### Résultats de la recherche:")
                for i, result in enumerate(results, 1):
                    display_log_result(result, i)
                
                # Statistiques
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_sim = np.mean([r.get('similarity', 0) for r in results]) * 100
                    st.metric("Similarité moyenne", f"{avg_sim:.1f}%")
                with col2:
                    st.metric("Résultats trouvés", len(results))
                with col3:
                    max_sim = max([r.get('similarity', 0) for r in results]) * 100
                    st.metric("Meilleure match", f"{max_sim:.1f}%")
                    
            except Exception as e:
                st.error(f"Erreur lors de la recherche: {e}")

def display_case_2():
    """Cas 2: Clustering d'erreurs"""
    st.markdown("## 👥 Cas 2: Identifier les groupes d'erreurs fréquentes")
    
    engine = load_search_engine()
    if not engine:
        st.error("Impossible de charger le moteur de recherche")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("Clustering K-Means sur les embeddings des logs d'erreur")
    
    with col2:
        n_clusters = st.slider("Nombre de clusters:", 2, 10, 5)
    
    if st.button("🎯 Analyser clusters", key="case2_cluster"):
        with st.spinner("Clustering en cours..."):
            try:
                clusters = engine.find_error_clusters(n_clusters=n_clusters)
                
                if clusters:
                    st.success(f"✅ {len(clusters)} clusters identifiés!")
                    
                    # Afficher les clusters
                    cols = st.columns(len(clusters))
                    for i, (cluster_id, info) in enumerate(clusters.items()):
                        with cols[i % len(cols)]:
                            st.metric(f"Cluster {cluster_id}", f"{info['size']} logs")
                            st.caption(f"Centroïde: {str(info['centroid'][:3])}")
                    
                    # Graphique de distribution
                    st.markdown("### Distribution des clusters:")
                    cluster_data = {
                        f"Cluster {cid}": info['size'] 
                        for cid, info in clusters.items()
                    }
                    st.bar_chart(cluster_data)
                    
                else:
                    st.warning("Pas assez de logs d'erreur pour clustering")
                    
            except Exception as e:
                st.error(f"Erreur lors du clustering: {e}")

def display_case_3():
    """Cas 3: Analyse temporelle"""
    st.markdown("## 📊 Cas 3: Analyser l'évolution temporelle des erreurs")
    
    engine = load_search_engine()
    if not engine:
        st.error("Impossible de charger le moteur de recherche")
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        error_pattern = st.text_input(
            "Motif d'erreur à analyser:",
            value="connection error"
        )
    
    with col2:
        days = st.slider("Période (jours):", 1, 30, 7)
    
    if st.button("📈 Analyser", key="case3_temporal"):
        with st.spinner("Analyse temporelle..."):
            try:
                temporal_data = engine.analyze_temporal_evolution(error_pattern, days=days)
                
                if temporal_data:
                    st.success(f"✅ Analyse sur {len(temporal_data)} jours")
                    
                    # Convertir en dataframe
                    df = pd.DataFrame(
                        list(temporal_data.items()),
                        columns=['Date', 'Nombre d\'erreurs']
                    )
                    
                    # Graphique
                    st.line_chart(df.set_index('Date'))
                    
                    # Tableau
                    st.markdown("### Détails:")
                    st.dataframe(df, use_container_width=True)
                    
                else:
                    st.warning("Pas de données disponibles")
                    
            except Exception as e:
                st.error(f"Erreur lors de l'analyse: {e}")

def display_case_4():
    """Cas 4: Comparaison sémantique vs mot-clé"""
    st.markdown("## ⚖️ Cas 4: Comparer recherche sémantique vs mot-clé")
    
    engine = load_search_engine()
    if not engine:
        st.error("Impossible de charger le moteur de recherche")
        return
    
    query = st.text_input(
        "Requête à comparer:",
        value="timeout",
        help="Ex: 'connection', 'memory', 'permission', etc."
    )
    
    if st.button("⚖️ Comparer", key="case4_compare"):
        with st.spinner("Comparaison en cours..."):
            try:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🧠 Recherche Sémantique")
                    semantic_results = engine.search_by_error(query, top_k=5)
                    st.info(f"**{len(semantic_results)} résultats** par similarité")
                    
                    for i, r in enumerate(semantic_results[:3], 1):
                        sim = (r.get('similarity', 0) * 100)
                        st.write(f"{i}. [{sim:.0f}%] {r['text'][:60]}...")
                
                with col2:
                    st.markdown("### 🔎 Recherche par Mot-clé")
                    keyword_results = engine.search_by_keyword(query, top_k=5)
                    st.info(f"**{len(keyword_results)} résultats** par occurrence")
                    
                    for i, r in enumerate(keyword_results[:3], 1):
                        st.write(f"{i}. {r['text'][:60]}...")
                
                # Analyse
                st.markdown("---")
                st.markdown("### 📊 Analyse comparative:")
                
                comparison_data = {
                    'Approche': ['Sémantique', 'Mot-clé'],
                    'Résultats': [len(semantic_results), len(keyword_results)]
                }
                st.bar_chart(pd.DataFrame(comparison_data).set_index('Approche'))
                
                st.markdown("""
                **Différences clés:**
                - 🧠 **Sémantique**: Capture le sens, même sans le mot exact
                - 🔎 **Mot-clé**: Cherche les occurrences exactes
                - 🎯 **Sémantique**: Mieux pour logs mal orthographiés
                - ⚡ **Mot-clé**: Plus rapide pour recherche exacte
                """)
                
            except Exception as e:
                st.error(f"Erreur lors de la comparaison: {e}")

def display_statistics():
    """Page des statistiques globales"""
    st.markdown("## 📈 Statistiques Globales")
    
    try:
        from src.database import VectorDatabase
        
        db = VectorDatabase()
        if not db.connect():
            st.error("Impossible de se connecter à la base de données")
            return
        
        stats = db.get_statistics()
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Logs en base", f"{stats['total_logs']:,}")
        with col2:
            st.metric("🔢 Embeddings", f"{stats['total_embeddings']:,}")
        with col3:
            if stats['total_logs'] > 0:
                coverage = (stats['total_embeddings'] / stats['total_logs']) * 100
                st.metric("📊 Couverture", f"{coverage:.1f}%")
        with col4:
            st.metric("🚀 Version", "1.0")
        
        # Informations techniques
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏗️ Architecture")
            st.info("""
            - **Framework**: Apache Spark 3.5
            - **Embeddings**: Sentence-Transformers
            - **Dimension**: 384
            - **Index**: IVFFlat (Cosinus)
            - **Base**: PostgreSQL + pgvector
            """)
        
        with col2:
            st.markdown("### ⚙️ Configuration")
            st.info("""
            - **Modèle**: all-MiniLM-L6-v2
            - **Batch size**: 1000
            - **Distance**: Cosinus
            - **Operator**: <=>
            """)
        
        # Phases complétées
        st.markdown("---")
        st.markdown("### ✅ Phases du TP")
        
        phases = [
            ("Phase 1: Exploration", "Complétée"),
            ("Phase 2: Ingestion Spark", "Complétée"),
            ("Phase 3: Vectorisation", "Complétée"),
            ("Phase 4: Recherche sémantique", "Complétée"),
        ]
        
        for phase, status in phases:
            st.success(f"✅ {phase} - {status}")
        
        db.disconnect()
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {e}")

if __name__ == "__main__":
    main()
