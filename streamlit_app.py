import streamlit as st
import logging
import time
from datetime import datetime

# Core Imports
from core.llm_client import OllamaClient
from core.orchestrator import Orchestrator
from core.pdf_loader import extract_text_from_pdf

# Agents
from agents.doc_analysis_agent import DocumentAnalysisAgent
from agents.extraction_agent import ExtractionAgent
from agents.reasoning_agent import ReasoningAgent
from agents.validation_agent import ValidationAgent

# Configuration
st.set_page_config(
    page_title="AI Orchestrator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for Chat Interface
st.markdown("""
<style>
    .main { background-color: #f5f7fa; }
    
    /* Header styling */
    .header-container {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
        border-radius: 8px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.95rem;
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
    
    /* Chat message containers */
    .user-message {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .assistant-message {
        background: #f0f4f8;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
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
            llm = OllamaClient(model="llama3.2:1b")
            if llm.is_available():
                orch = Orchestrator(llm)
                orch.register_agent(DocumentAnalysisAgent(llm))
                orch.register_agent(ExtractionAgent(llm))
                orch.register_agent(ReasoningAgent(llm))
                orch.register_agent(ValidationAgent(llm))
                st.session_state.orchestrator = orch
                st.session_state.llm_status = "Online"
            else:
                st.session_state.orchestrator = None
                st.session_state.llm_status = "Offline"
        except Exception as e:
            st.session_state.orchestrator = None
            st.session_state.llm_status = "Offline"

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
        status_class = "status-online" if st.session_state.get('llm_status') == "Online" else "status-offline"
        status_text = "Opérationnel" if st.session_state.get('llm_status') == "Online" else "Hors ligne"
        st.markdown(f"**Moteur IA**: <span class='{status_class}'>{status_text}</span>", unsafe_allow_html=True)
        st.caption("Llama 3.2 (Local)")
        
        st.markdown("---")
        
        st.markdown("### Modules Actifs")
        modules = [
            ("Analyse Documentaire", "#3b82f6"),
            ("Moteur de Raisonnement", "#8b5cf6"),
            ("Extraction Structurée", "#10b981"),
            ("Validation & Qualité", "#f59e0b")
        ]
        for module, color in modules:
            st.markdown(f'<div class="module-item"><span style="color: {color}; margin-right: 0.5rem;">●</span>{module}</div>', unsafe_allow_html=True)
        
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
                    st.success(f"✓ {uploaded_file.name}")
                else:
                    st.error("Erreur de lecture")
                    st.session_state.current_pdf = None
        else:
            st.session_state.current_pdf = None
            st.session_state.current_pdf_name = None
        
        st.markdown("---")
        
        if st.button("Nouvelle Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_pdf = None
            st.rerun()

def get_agent_badge(agent_name: str) -> str:
    badges = {
        "DocumentAnalysisAgent": '<div class="badge-analysis">ANALYSE DOCUMENTAIRE</div>',
        "ReasoningAgent": '<div class="badge-reasoning">MOTEUR DE RAISONNEMENT</div>',
        "ExtractionAgent": '<div class="badge-extraction">EXTRACTION STRUCTURÉE</div>',
        "ValidationAgent": '<div class="badge-validation">VALIDATION & QUALITÉ</div>'
    }
    return badges.get(agent_name, f'<div>{agent_name}</div>')

def render_message(role, content, timestamp=None):
    """Render a chat message."""
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
        
        # Display agent results
        results = content
        for key, value in sorted(results.items()):
            if key == 'original_query' or not key.startswith('step_'): 
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
                    else:
                        for k, v in value.items():
                            if k not in ['instruction', 'context']:
                                st.write(f"**{k}**: {v}")
                else:
                    st.write(value)
            
            elif key.endswith('_error'):
                st.error(f"Erreur: {value}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    init_orchestrator()
    render_sidebar()
    
    # Initialize messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Professional Header
    st.markdown("""
        <div class="header-container">
            <span class="badge-internal">Usage Interne</span>
            <h1>Agentic AI Orchestrator</h1>
            <p>Système autonome d'analyse multi-agents</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display conversation history
    for msg in st.session_state.messages:
        render_message(msg['role'], msg['content'], msg.get('timestamp'))
    
    # Add vertical space to push input down
    st.markdown("<br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    
    # Input area at bottom
    st.markdown("###")
    
    with st.form("input_form", clear_on_submit=True):
        user_input = st.text_area(
            "Votre message", 
            placeholder="Collez du texte ou posez une question...",
            height=150,
            label_visibility="collapsed"
        )
        submit = st.form_submit_button("Envoyer", type="primary", use_container_width=True)
    
    if submit and user_input:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': timestamp
        })
        
        # Prepare query with PDF context if available
        full_query = user_input
        if st.session_state.get('current_pdf'):
            full_query = f"CONTEXTE DU DOCUMENT:\n{st.session_state.current_pdf}\n\nINSTRUCTION:\n{user_input}"
        
        # Execute
        if st.session_state.orchestrator:
            with st.spinner("Analyse en cours..."):
                try:
                    results = st.session_state.orchestrator.run(full_query)
                    
                    # Add assistant response
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': results,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                except Exception as e:
                    st.error(f"Erreur: {e}")
        else:
            st.error("Système non initialisé. Vérifiez qu'Ollama est en cours d'exécution.")
        
        st.rerun()

if __name__ == "__main__":
    main()