import streamlit as st

st.set_page_config(
    page_title="Documentation - Orchestrateur IA",
    page_icon="book",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    .doc-section { 
        background: white; 
        padding: 1.25rem; 
        border-radius: 8px; 
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .agent-card {
        border-left: 4px solid;
        padding: 1rem;
        margin: 1rem 0;
        background: #f8fafc;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("Documentation - Orchestrateur IA")
st.caption("Guide d'utilisation du système multi-agents")

# Aperçu
st.markdown('<div class="doc-section">', unsafe_allow_html=True)
st.header("Présentation")
st.markdown("""
Le système repose sur un **orchestrateur agentique** piloté par un **état global évolutif**. 

Un agent de raisonnement central planifie dynamiquement les étapes, tandis que des agents spécialisés exécutent des actions ciblées (analyse, extraction, recherche). 

Les résultats sont évalués par un agent de validation capable de déclencher des **corrections** ou des **itérations supplémentaires** jusqu'à satisfaction de critères d'arrêt explicites.
""")
st.markdown('</div>', unsafe_allow_html=True)

# Agents
st.markdown('<div class="doc-section">', unsafe_allow_html=True)
st.header("Les Agents")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="agent-card" style="border-color: #3b82f6;">
        <h4>Analyse Documentaire</h4>
        <p><strong>Rôle</strong> : Analyse et résumé de documents</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Résumés en français</li>
            <li>Extraction de points clés</li>
            <li>Réponse aux questions sur le document</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="agent-card" style="border-color: #2c5282;">
        <h4>Générateur de Rapports</h4>
        <p><strong>Rôle</strong> : Génération de rapports d'étude</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Synthèse multi-agents complexe</li>
            <li>Rapports Markdown professionnels</li>
            <li>Structure d'analyse stratégique</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="agent-card" style="border-color: #10b981;">
        <h4>Extracteur de Données</h4>
        <p><strong>Rôle</strong> : Extraction de données structurées</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Dates, montants, noms</li>
            <li>Tableaux et listes</li>
            <li>Entités nommées</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="agent-card" style="border-color: #8b5cf6;">
        <h4>Moteur de Raisonnement</h4>
        <p><strong>Rôle</strong> : Raisonnement et planification</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Analyse de problèmes complexes</li>
            <li>Création de plans d'action</li>
            <li>Prise de décision</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="agent-card" style="border-color: #f59e0b;">
        <h4>Contrôleur de Qualité</h4>
        <p><strong>Rôle</strong> : Validation et fiabilité</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Vérification de la qualité des résultats</li>
            <li>Détection d'erreurs (hallucinations)</li>
            <li>Feedback constructif</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="agent-card" style="border-color: #00d2ff;">
        <h4>Chercheur Web</h4>
        <p><strong>Rôle</strong> : Recherche d'informations externes</p>
        <p><strong>Capacités</strong> :</p>
        <ul>
            <li>Décomposition de requêtes complexes</li>
            <li>Recherche multi-sources automatique</li>
            <li>Vérification croisée des informations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Usage Examples
st.markdown('<div class="doc-section">', unsafe_allow_html=True)
st.header("Exemples d'Utilisation")

tab1, tab2, tab3, tab4 = st.tabs(["Analyse Stratégique", "Recherche & Veille", "Extraction Structurée", "Validation Itérative"])

with tab1:
    st.subheader("Analyse Documentaire & Rapports")
    st.markdown("""
    Combinez l'analyse de documents avec la génération de rapports structurés.
    """)
    st.code("""
# Avec un PDF chargé :
"Analyse ce rapport annuel et génère un rapport d'étude complet."
"Identifie les risques stratégiques mentionnés dans ce document."
"Résume les conclusions techniques pour une audience de direction."
    """, language="text")

with tab2:
    st.subheader("Recherche Web & Cross-Verification")
    st.markdown("""
    Interrogez le web pour des informations en temps réel avec synthèse multi-sources.
    """)
    st.code("""
"Quelles sont les dernières avancées en IA générative cette semaine ?"
"Compare les prix du marché pour les solutions Cloud actuelles."
"Fais une recherche sur l'évolution de la réglementation RGPD en 2024."
    """, language="text")

with tab3:
    st.subheader("Intelligence de Données")
    st.markdown("""
    Extraction précise de données complexes au format structuré.
    """)
    st.code("""
"Extrait les indicateurs financiers clés sous forme de tableau."
"Liste toutes les entités juridiques citées et leurs dates d'effet."
"Identifie et structure les montants de facturation mentionnés."
    """, language="text")

with tab4:
    st.subheader("Contrôle Qualité & Auto-Correction")
    st.markdown("""
    Utilisez la boucle de validation pour garantir la fiabilité des réponses.
    """)
    st.code("""
"Vérifie la conformité de ce résumé avec les points clés du document."
"Analyse la neutralité du rapport généré précédemment."
"Valide l'exactitude des dates extraites par rapport au texte source."
    """, language="text")

st.markdown('</div>', unsafe_allow_html=True)

# Technical Info
st.markdown('<div class="doc-section">', unsafe_allow_html=True)
st.header("Informations Techniques")

st.markdown("""
| Composant | Technologie |
|-----------|-------------|
| Frontend | Streamlit |
| LLM Backend | Google Gemini API |
| Architecture | Multi-Agent Orchestration |
| Format de rapport | Markdown (.md) |
""")

st.info("**Conseil**: Pour de meilleurs résultats, soyez précis dans vos requêtes et chargez des documents PDF de bonne qualité.")
st.markdown('</div>', unsafe_allow_html=True)

# Pied de page
st.divider()
st.caption("© 2026 Orchestrateur IA - Usage Interne")
