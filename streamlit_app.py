"""
Interface Streamlit pour l'agent de veille technologique NLP - Version corrigée
"""
import streamlit as st
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging

# Import de l'agent corrigé
from agent import TechWatchAgent, run_targeted_search, run_tech_watch_cycle
from config import config, NLP_KEYWORDS, MAX_SEARCH_RESULTS

# Configuration de la page
st.set_page_config(
    page_title="AI Agent de Veille Technologique NLP",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .report-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitApp:
    def __init__(self):
        self.init_session_state()
        
    def init_session_state(self):
        """Initialise les variables de session"""
        if 'agent' not in st.session_state:
            st.session_state.agent = None
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
        if 'reports' not in st.session_state:
            st.session_state.reports = []
        if 'config' not in st.session_state:
            st.session_state.config = {
                'domains': NLP_KEYWORDS[:5],  # Premiers 5 mots-clés
                'max_results': MAX_SEARCH_RESULTS,
                'language': 'fr'
            }

    def initialize_agent(self):
        """Initialise l'agent IA"""
        if st.session_state.agent is None:
            try:
                with st.spinner("🤖 Initialisation de l'agent IA..."):
                    st.session_state.agent = TechWatchAgent()
                    time.sleep(1)  # Simulation d'initialisation
                st.success("✅ Agent IA initialisé avec succès!")
                return True
            except Exception as e:
                st.error(f"❌ Erreur d'initialisation de l'agent: {e}")
                return False
        return True

    def render_sidebar(self):
        """Rendu de la barre latérale"""
        st.sidebar.header("🔧 Configuration")
        
        # Status de l'agent
        if st.session_state.agent:
            st.sidebar.success("🤖 Agent: Actif")
        else:
            st.sidebar.error("🤖 Agent: Non initialisé")
        
        # Configuration des domaines
        st.sidebar.subheader("Domaines de veille")
        selected_keywords = st.sidebar.multiselect(
            "Sélectionner les mots-clés NLP",
            options=NLP_KEYWORDS,
            default=st.session_state.config['domains']
        )
        st.session_state.config['domains'] = selected_keywords
        
        # Paramètres
        st.sidebar.subheader("Paramètres")
        st.session_state.config['max_results'] = st.sidebar.slider(
            "Nombre max de résultats", 5, 20, st.session_state.config['max_results']
        )
        
        # Statistiques
        st.sidebar.subheader("📊 Statistiques")
        st.sidebar.metric("Recherches effectuées", len(st.session_state.search_history))
        st.sidebar.metric("Rapports générés", len(st.session_state.reports))
        
        # Bouton d'initialisation
        if st.sidebar.button("🔄 Réinitialiser Agent"):
            st.session_state.agent = None
            st.sidebar.info("Agent réinitialisé")

    def render_main_header(self):
        """Rendu de l'en-tête principal"""
        st.markdown('<h1 class="main-header">🤖 AI Agent de Veille Technologique NLP</h1>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>🔍 Recherche</h3>
                <p>Recherche ciblée</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Analyse</h3>
                <p>Analyse automatique</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📝 Synthèse</h3>
                <p>Rapports intelligents</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3>🔔 Veille</h3>
                <p>Surveillance continue</p>
            </div>
            """, unsafe_allow_html=True)

    def run_search(self, query: str):
        """Lance une recherche ciblée"""
        if not self.initialize_agent():
            return None
        
        with st.spinner(f"🔍 Recherche en cours: {query}..."):
            try:
                # Utiliser la fonction de recherche ciblée
                results = run_targeted_search(query, st.session_state.config['max_results'])
                
                # Ajouter à l'historique
                st.session_state.search_history.append({
                    'query': query,
                    'timestamp': datetime.now(),
                    'results_count': results.get('analyzed_count', 0),
                    'total_found': results.get('total_found', 0)
                })
                
                return results
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la recherche: {str(e)}")
                return None

    def render_search_interface(self):
        """Interface de recherche"""
        st.header("🔍 Recherche Ciblée")
        
        # Initialiser l'agent si nécessaire
        if not st.session_state.agent:
            if st.button("🚀 Initialiser l'Agent"):
                self.initialize_agent()
        
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input(
                "Entrez votre requête de recherche", 
                placeholder="Ex: dernières avancées en IA générative",
                key="search_query"
            )
        with col2:
            search_button = st.button("🔍 Rechercher", type="primary")
        
        if search_button and query:
            results = self.run_search(query)
            
            if results and not results.get('error'):
                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ Recherche terminée</h4>
                    <p><strong>Requête:</strong> {query}</p>
                    <p><strong>Résultats trouvés:</strong> {results.get('total_found', 0)}</p>
                    <p><strong>Documents analysés:</strong> {results.get('analyzed_count', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Affichage des résultats
                if results.get('results'):
                    st.subheader("📄 Résultats d'analyse")
                    
                    for i, result in enumerate(results['results']):
                        analysis = result.get('analysis', {})
                        relevance_score = analysis.get('relevance_score', 0)
                        
                        # Couleur selon le score de pertinence
                        if relevance_score >= 8:
                            color = "🟢"
                        elif relevance_score >= 6:
                            color = "🟡"
                        else:
                            color = "🔴"
                        
                        with st.expander(f"{color} {result.get('title', f'Document {i+1}')} - Score: {relevance_score}/10"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write("**Résumé d'analyse:**")
                                st.write(analysis.get('summary', 'Pas de résumé disponible'))
                                
                                if analysis.get('nlp_domains'):
                                    st.write("**Domaines NLP:**")
                                    st.write(", ".join(analysis['nlp_domains']))
                                
                                if analysis.get('techniques'):
                                    st.write("**Techniques mentionnées:**")
                                    st.write(", ".join(analysis['techniques']))
                                
                                if result.get('url'):
                                    st.markdown(f"[🔗 Lire l'article complet]({result['url']})")
                            
                            with col2:
                                st.metric("Score de pertinence", f"{relevance_score}/10")
                                st.metric("Score d'innovation", f"{analysis.get('novelty_score', 0)}/10")
                                st.write(f"**Mots extraits:** {len(result.get('content', '').split())}")
            
            elif results and results.get('error'):
                st.markdown(f"""
                <div class="error-box">
                    <h4>❌ Erreur de recherche</h4>
                    <p>{results['error']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Aucun résultat trouvé pour cette requête")

    def render_full_cycle_interface(self):
        """Interface pour le cycle complet de veille"""
        st.header("🤖 Cycle Complet de Veille")
        
        st.info("""
        🔄 **Cycle complet de veille technologique:**
        1. **Recherche** sur les mots-clés configurés
        2. **Extraction** du contenu des articles
        3. **Analyse** NLP automatique
        4. **Génération** de rapport de synthèse
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Configuration du cycle")
            use_custom_keywords = st.checkbox("Utiliser des mots-clés personnalisés")
            
            if use_custom_keywords:
                custom_keywords = st.text_area(
                    "Mots-clés (un par ligne)",
                    value="\n".join(st.session_state.config['domains']),
                    height=100
                )
                keywords_list = [k.strip() for k in custom_keywords.split('\n') if k.strip()]
            else:
                keywords_list = st.session_state.config['domains']
                st.write("**Mots-clés sélectionnés:**")
                for kw in keywords_list:
                    st.write(f"• {kw}")
        
        with col2:
            st.subheader("Lancement du cycle")
            if st.button("🚀 Lancer le Cycle Complet", type="primary"):
                if not self.initialize_agent():
                    return
                
                with st.spinner("🔄 Exécution du cycle complet de veille..."):
                    try:
                        # Lancer le cycle complet
                        report = run_tech_watch_cycle(keywords_list if use_custom_keywords else None)
                        
                        if report and 'error_message' not in report.get('metadata', {}):
                            # Succès
                            st.success("✅ Cycle de veille terminé avec succès!")
                            
                            # Ajouter aux rapports
                            st.session_state.reports.append({
                                'id': report.get('metadata', {}).get('report_id', 'unknown'),
                                'timestamp': datetime.now(),
                                'type': 'Cycle complet',
                                'summary': report.get('summary', {}),
                                'report_data': report
                            })
                            
                            # Afficher le résumé
                            summary = report.get('summary', {})
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Documents analysés", summary.get('total_documents_analyzed', 0))
                            with col2:
                                st.metric("Documents pertinents", summary.get('relevant_documents', 0))
                            with col3:
                                st.metric("Taux de pertinence", f"{summary.get('relevance_rate', 0):.1%}")
                            with col4:
                                st.metric("Score moyen", f"{summary.get('average_relevance_score', 0):.1f}/10")
                            
                            # Insights principaux
                            if 'insights' in report:
                                insights = report['insights']
                                
                                if insights.get('top_nlp_domains'):
                                    st.subheader("🔥 Domaines NLP tendances")
                                    for domain, count in insights['top_nlp_domains']:
                                        st.write(f"• **{domain}**: {count} mentions")
                                
                                if insights.get('high_impact_papers'):
                                    st.subheader("📑 Papers à impact élevé")
                                    for paper in insights['high_impact_papers'][:3]:
                                        st.write(f"**{paper.get('title', 'Sans titre')}** (Score: {paper.get('relevance_score', 0)}/10)")
                            
                        else:
                            # Erreur
                            error_msg = report.get('metadata', {}).get('error_message', 'Erreur inconnue')
                            st.error(f"❌ Erreur lors du cycle: {error_msg}")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur critique: {str(e)}")

    def render_reports(self):
        """Interface des rapports"""
        st.header("📊 Rapports de Veille")
        
        if st.session_state.reports:
            # Sélection du rapport
            report_options = [
                f"{r['type']} - {r['timestamp'].strftime('%d/%m/%Y %H:%M')}" 
                for r in st.session_state.reports
            ]
            
            selected_idx = st.selectbox("Sélectionner un rapport", range(len(report_options)), format_func=lambda x: report_options[x])
            
            if selected_idx is not None:
                selected_report = st.session_state.reports[selected_idx]
                report_data = selected_report.get('report_data', {})
                
                # Affichage du rapport
                st.subheader(f"📄 {selected_report['type']}")
                st.write(f"**Généré le:** {selected_report['timestamp'].strftime('%d/%m/%Y à %H:%M')}")
                
                # Résumé
                summary = report_data.get('summary', {})
                if summary:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Documents analysés", summary.get('total_documents_analyzed', 0))
                    with col2:
                        st.metric("Documents pertinents", summary.get('relevant_documents', 0))
                    with col3:
                        st.metric("Score moyen", f"{summary.get('average_relevance_score', 0):.1f}/10")
                
                # Download du rapport
                if st.button("💾 Télécharger le rapport JSON"):
                    st.download_button(
                        label="Télécharger",
                        data=json.dumps(report_data, indent=2, ensure_ascii=False),
                        file_name=f"rapport_{selected_report['id']}.json",
                        mime="application/json"
                    )
        else:
            st.info("📝 Aucun rapport généré. Lancez une recherche ou un cycle complet pour générer des rapports.")

    def render_analytics(self):
        """Interface d'analytics"""
        st.header("📈 Analytics")
        
        if st.session_state.search_history:
            # Graphique des recherches dans le temps
            df_searches = pd.DataFrame(st.session_state.search_history)
            df_searches['date'] = pd.to_datetime(df_searches['timestamp']).dt.date
            searches_by_date = df_searches.groupby('date').size().reset_index(name='count')
            
            fig = px.line(
                searches_by_date, 
                x='date', 
                y='count',
                title="Évolution des Recherches",
                labels={'date': 'Date', 'count': 'Nombre de Recherches'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau des recherches récentes
            st.subheader("🔍 Recherches Récentes")
            recent_searches = df_searches.tail(10)[['query', 'timestamp', 'results_count', 'total_found']]
            st.dataframe(recent_searches, use_container_width=True)
        else:
            st.info("📊 Aucune donnée d'analytics disponible. Effectuez quelques recherches pour voir les statistiques.")

    def run(self):
        """Lance l'application"""
        self.render_sidebar()
        self.render_main_header()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4 = st.tabs(["🔍 Recherche Ciblée", "🤖 Cycle Complet", "📊 Rapports", "📈 Analytics"])
        
        with tab1:
            self.render_search_interface()
        
        with tab2:
            self.render_full_cycle_interface()
        
        with tab3:
            self.render_reports()
        
        with tab4:
            self.render_analytics()

def main():
    """Point d'entrée principal"""
    try:
        app = StreamlitApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Erreur critique de l'application: {e}")
        st.write("Vérifiez que tous les modules sont correctement installés et configurés.")

if __name__ == "__main__":
    main()