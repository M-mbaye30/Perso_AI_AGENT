import streamlit as st
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv(override=True)

# Imports du Cœur
from core.llm_client import GeminiClient
from core.orchestrator import Orchestrator
from core.pdf_loader import extract_text_from_pdf
from core.observability import init_observability

# Initialisation de l'observabilité (Phoenix)
obs_active = init_observability()

# Agents
from agents.doc_analysis_agent import DocumentAnalysisAgent
from agents.extraction_agent import ExtractionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.validation_agent import ValidationAgent
from agents.report_agent import ReportAgent
from agents.web_search_agent import WebSearchAgent

# Configuration
st.set_page_config(
    page_title="Orchestrateur IA",
    page_icon="cog",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Chat Interface
st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    
    /* Style de l'en-tête */
    .header-container {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        border-radius: 8px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .header-container p {
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.85rem;
    }
    
    .badge-internal {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        background-color: rgba(255,255,255,0.2);
        color: white;
    }
    
    /* Messages de chat */
    .user-message {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .assistant-message {
        background: #f0f4f8;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .message-header {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }
    
    .badge-analysis { background: #3b82f6; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; display: inline-block; }
    .badge-reasoning { background: #8b5cf6; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; display: inline-block; }
    .badge-extraction { background: #10b981; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; display: inline-block; }
    .badge-validation { background: #f59e0b; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem; display: inline-block; }
    
    .status-online { color: #10b981; font-weight: 600; }
    .status-offline { color: #ef4444; font-weight: 600; }
    
    .module-item {
        padding: 0.5rem 0;
        border-left: 3px solid #e5e7eb;
        padding-left: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def init_orchestrator():
    if 'orchestrator' not in st.session_state:
        try:
            llm = GeminiClient(model="gemini-3.5-flash")
            if llm.is_available():
                orch = Orchestrator(llm)
                orch.register_agent(DocumentAnalysisAgent(llm))
                orch.register_agent(ExtractionAgent(llm))
                orch.register_agent(ReasoningAgent(llm))
                orch.register_agent(ValidationAgent(llm))
                orch.register_agent(ReportAgent(llm))
                orch.register_agent(WebSearchAgent(llm))
                st.session_state.orchestrator = orch
                st.session_state.llm_status = "En Ligne"
                st.session_state.active_model = llm.model
            else:
                st.session_state.orchestrator = None
                st.session_state.llm_status = "Hors Ligne"
        except Exception as e:
            st.session_state.orchestrator = None
            st.session_state.llm_status = "Hors Ligne"

def render_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style='padding: 1rem 0;'>
                <div style='background: linear-gradient(135deg, #3b82f6, #8b5cf6); 
                            width: 60px; height: 60px; border-radius: 12px; 
                            display: inline-flex; align-items: center; justify-content: center;
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                    <span style='color: white; font-size: 28px; font-weight: bold;'>AI</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Système")
        status_class = "status-online" if st.session_state.get('llm_status') == "En Ligne" else "status-offline"
        status_text = st.session_state.get('llm_status', 'Hors Ligne')
        st.markdown(f"**Moteur IA**: <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)
        
        # Afficher le modèle actif
        active_model = st.session_state.get('active_model', 'Modèle Inconnu')
        st.caption(f"Google Gemini: {active_model}")
        
        st.markdown("---")
        
        st.markdown("### Modules Actifs")
        modules = [
            ("Analyse Documentaire", "#3b82f6"),
            ("Moteur de Raisonnement", "#8b5cf6"),
            ("Extraction Structurée", "#10b981"),
            ("Validation & Qualité", "#f59e0b"),
            ("Recherche Web Avancée", "#00d2ff"),
            ("Télémétrie Technique", "#1e293b")
        ]
        for module, color in modules:
            st.markdown(f'<div class="module-item"><span style="color: {color}; margin-right: 0.5rem;">●</span>{module}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Section Observabilité
        st.markdown("### 🔍 Observabilité")
        if obs_active:
            cloud_mode = os.getenv("PHOENIX_API_KEY") is not None
            url = "https://app.phoenix.arize.com" if cloud_mode else "http://localhost:6006"
            label = "Phoenix Cloud" if cloud_mode else "Phoenix Local"
            st.success(f"Tracing Actif : {label}")
            st.markdown(f"[Ouvrir le Dashboard]({url})")
        else:
            st.warning("Observabilité désactivée")

        st.markdown("---")
        
        # PDF Upload in sidebar
        st.markdown("### Document")
        uploaded_file = st.file_uploader("Fichier PDF", type=['pdf'], label_visibility="collapsed")
        
        if uploaded_file:
            if 'current_pdf' not in st.session_state or st.session_state.current_pdf_name != uploaded_file.name:
                pdf_text = extract_text_from_pdf(uploaded_file.getvalue())
                if "error" not in pdf_text.lower():
                    st.session_state.current_pdf = pdf_text
                    st.session_state.current_pdf_name = uploaded_file.name
                    st.success(f"{uploaded_file.name}")
                else:
                    st.error("Erreur de lecture")
                    st.session_state.current_pdf = None
        else:
            st.session_state.current_pdf = None
            st.session_state.current_pdf_name = None
        
        st.markdown("---")
        
        if st.button("Nouvelle Conversation", use_container_width=True):
            # Nettoyage total de la session pour forcer le rechargement
            st.session_state.messages = []
            st.session_state.current_pdf = None
            if 'orchestrator' in st.session_state:
                del st.session_state.orchestrator
            st.rerun()

def get_agent_badge(agent_name: str) -> str:
    badges = {
        "DocumentAnalysisAgent": '<div class="badge-analysis">ANALYSE DOCUMENTAIRE</div>',
        "ReasoningAgent": '<div class="badge-reasoning">MOTEUR DE RAISONNEMENT</div>',
        "ExtractionAgent": '<div class="badge-extraction">EXTRACTION STRUCTURÉE</div>',
        "ValidationAgent": '<div class="badge-validation">VALIDATION & QUALITÉ</div>',
        "ReportAgent": '<div class="badge-reasoning">RAPPORT D\'ÉTUDE</div>',
        "WebSearchAgent": '<div class="badge-extraction" style="background: #00d2ff;">RECHERCHE WEB</div>'
    }
    return badges.get(agent_name, f'<div>{agent_name}</div>')

def generate_report(results: dict, query: str) -> str:
    """Générer un rapport Markdown formaté à partir des résultats des agents."""
    report_lines = [
        "# Rapport d'Analyse - Orchestrateur IA",
        f"\n**Date**: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"\n**Requête**: {query[:200]}...\n" if len(query) > 200 else f"\n**Requête**: {query}\n",
        "---\n"
    ]
    
    for key, value in sorted(results.items()):
        if key == 'original_query' or not key.startswith('step_'):
            continue
        
        if key.endswith('_result'):
            step_idx = int(key.split('_')[1])
            agent_key = f"step_{step_idx}_agent"
            agent_name = results.get(agent_key, "Agent")
            
            report_lines.append(f"\n## {agent_name}\n")
            
            if isinstance(value, dict):
                if 'analysis' in value:
                    report_lines.append(value['analysis'])
                elif 'extracted_data' in value:
                    report_lines.append("### Données Extraites\n")
                    for k, v in value.get('extracted_data', {}).items():
                        report_lines.append(f"- **{k}**: {v}")
                elif 'thought_process' in value:
                    report_lines.append(value['thought_process'])
                elif 'is_valid' in value:
                    status = "Validé" if value['is_valid'] else "Non valide"
                    report_lines.append(f"**Statut**: {status}")
                    if 'feedback' in value:
                        report_lines.append(f"\n**Feedback**: {value['feedback']}")
                else:
                    for k, v in value.items():
                        if k not in ['instruction', 'context']:
                            report_lines.append(f"- **{k}**: {v}")
            else:
                report_lines.append(str(value))
        
        elif key.endswith('_error'):
            report_lines.append(f"\n**Erreur**: {value}\n")
    
    report_lines.append("\n---\n*Généré par Orchestrateur IA*")
    return "\n".join(report_lines)

def render_message(role, content, timestamp=None):
    """Rendu d'un message de chat."""
    if role == "user":
        st.markdown('<div class="user-message">', unsafe_allow_html=True)
        if timestamp:
            st.markdown(f'<div class="message-header">Vous • {timestamp}</div>', unsafe_allow_html=True)
        st.markdown(f"**{content}**")  # Make user text bold for visibility
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="assistant-message">', unsafe_allow_html=True)
        if timestamp:
            st.markdown(f'<div class="message-header">Assistant • {timestamp}</div>', unsafe_allow_html=True)
        
        # Afficher les résultats des agents
        results = content
        
        # Affichage des erreurs globales (ex: échec de planification)
        if isinstance(results, dict) and "erreur" in results:
            st.error(results["erreur"])
            return
        
        # OPTIMISATION: Réponse directe (pas d'agents appelés)
        if isinstance(results, dict) and "direct_response" in results:
            st.write(results["direct_response"])
            return

        for key, value in sorted(results.items()):
            if key == 'original_query' or key == 'direct_response' or not key.startswith('step_'): 
                continue
            
            if key.endswith('_result'):
                step_idx = int(key.split('_')[1])
                agent_key = f"step_{step_idx}_agent"
                agent_name = results.get(agent_key, "")
                
                if agent_name:
                    st.markdown(get_agent_badge(agent_name), unsafe_allow_html=True)
                
                if isinstance(value, dict):
                    if 'analysis' in value:
                        st.write(value['analysis'])
                    elif 'extracted_data' in value:
                        extracted = value['extracted_data']
                        if isinstance(extracted, dict):
                            for field, val in extracted.items():
                                st.markdown(f"**{field}**: `{val}`")
                        else:
                            st.write(extracted)
                    elif 'thought_process' in value:
                        st.write(value['thought_process'])
                    elif 'is_valid' in value:
                        status = "Validé" if value['is_valid'] else "Non valide"
                        st.write(f"**Statut**: {status}")
                    elif 'report' in value:
                        # Full structured report from ReportAgent
                        st.markdown(value['report'])
                        # Dedicated download for the report
                        report_title = value.get('title', 'Rapport')
                        st.download_button(
                            label=f"Télécharger: {report_title}",
                            data=value['report'],
                            file_name=f"{report_title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown",
                            key=f"report_download_{timestamp}"
                        )
                    else:
                        for k, v in value.items():
                            if k not in ['instruction', 'context']:
                                st.write(f"**{k}**: {v}")
                else:
                    st.write(value)
            
            elif key.endswith('_error'):
                st.error(f"Erreur: {value}")
        
        # Download button for report
        original_query = results.get('original_query', '')
        report_content = generate_report(results, original_query)
        st.download_button(
            label="Télécharger le rapport",
            data=report_content,
            file_name=f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            key=f"download_{timestamp}"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_orchestrator()
    render_sidebar()
    
    # Initialize messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # En-tête Professionnel
    st.markdown("""
        <div class="header-container">
            <span class="badge-internal">Usage Interne</span>
            <h1>Orchestrateur IA</h1>
            <p>Système autonome d'analyse multi-agents</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display conversation history
    for msg in st.session_state.messages:
        render_message(msg['role'], msg['content'], msg.get('timestamp'))
    
    # Zone de saisie dynamique (st.chat_input)
    user_input = st.chat_input("Collez du texte ou posez une question...")
    
    if user_input:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Ajouter le message utilisateur
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # Préparer la requête avec le contexte PDF si disponible
        full_query = user_input
        if st.session_state.get('current_pdf'):
            full_query = f"CONTEXTE DU DOCUMENT:\n{st.session_state.current_pdf}\n\nINSTRUCTION:\n{user_input}"
        
        # Exécuter les agents avec affichage du statut
        if st.session_state.orchestrator:
            status_placeholder = st.empty()
            
            def update_status(step_num, total_steps, agent_name, status_text):
                """Callback pour mettre à jour l'interface avec la progression des agents."""
                if total_steps == 0:
                    progress_text = status_text
                else:
                    progress_text = f"**Étape {step_num}/{total_steps}** | `{agent_name}` | {status_text}"
                status_placeholder.info(progress_text)
            
            try:
                # Afficher le message utilisateur immédiatement avant l'exécution pour un feedback visuel
                st.rerun() # On force le rerun pour afficher le message utilisateur
                
            except Exception as e:
                st.error(f"Erreur d'exécution : {e}")

    # Logique d'exécution (déplacée pour gérer le rerun)
    if st.session_state.messages and st.session_state.messages[-1]['role'] == 'user':
        last_msg = st.session_state.messages[-1]
        
        full_query = last_msg['content']
        if st.session_state.get('current_pdf'):
             full_query = f"CONTEXTE DU DOCUMENT:\n{st.session_state.current_pdf}\n\nINSTRUCTION:\n{last_msg['content']}"

        if st.session_state.orchestrator:
            status_container = st.empty()
            def update_status_final(step_num, total_steps, agent_name, status_text):
                if total_steps == 0:
                    txt = status_text
                else:
                    txt = f"**Étape {step_num}/{total_steps}** | `{agent_name}` | {status_text}"
                status_container.info(txt)
            
            try:
                status_container.info("Initialisation du graphe LangGraph...")
                import time
                time.sleep(1)
                with st.spinner("L'orchestrateur travaille..."):
                    results = st.session_state.orchestrator.run(full_query, status_callback=update_status_final)
                    status_container.success("Traitement terminé !")
                    
                    # Ajouter la réponse de l'assistant
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': results,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    st.rerun()
            except Exception as e:
                status_container.error(f"Erreur d'exécution : {e}")
                try:
                    # Repli sur une réponse directe
                    direct_resp = st.session_state.orchestrator.llm_client.generate(
                        full_query,
                        system_prompt=(
                            "Tu es l'Agent IA Orchestrateur (secours). "
                            "Réponds directement à la question de l'utilisateur de manière complète en français."
                        )
                    )
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': {"direct_response": direct_resp},
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    st.rerun()
                except Exception as e_inner:
                    st.error(f"Erreur critique de secours : {e_inner}")

if __name__ == "__main__":
    main()