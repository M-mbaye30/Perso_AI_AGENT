import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="Traçabilité - Orchestrateur IA",
    page_icon="terminal",
    layout="wide"
)

# Custom CSS for Traceability
st.markdown("""
<style>
    .trace-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #1e293b;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .trace-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.5rem;
    }
    .status-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .status-success { background: #dcfce7; color: #166534; }
    .status-retry { background: #fef9c3; color: #854d0e; }
    .status-failed { background: #fee2e2; color: #991b1b; }
    
    .payload-container {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 4px;
        font-family: monospace;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Tableau de Bord de Traçabilité")
st.caption("Observabilité technique et audit des cycles agentiques")

if 'messages' not in st.session_state or not st.session_state.messages:
    st.info("Aucune trace d'exécution disponible. Lancez une requête pour voir les détails techniques ici.")
else:
    # Get last assistant result (which contains the context)
    last_assistant_msg = next((m for m in reversed(st.session_state.messages) if m['role'] == 'assistant'), None)
    
    if not last_assistant_msg or 'trace' not in last_assistant_msg['content']:
        st.warning("Les données de traçabilité ne sont pas disponibles pour cette session.")
    else:
        trace = last_assistant_msg['content']['trace']
        original_query = last_assistant_msg['content'].get('original_query', 'N/A')
        
        st.write(f"**Dernière Requête Auditée** : `{original_query[:100]}...`")
        
        st.divider()
        
        # Summary Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Étapes Totales", len(set([t.get('step_index') for t in trace if 'step_index' in t])))
        col2.metric("Itérations LLM", len(trace))
        retries = len([t for t in trace if t.get('attempt', 1) > 1])
        col3.metric("Auto-Corrections", retries)

        st.markdown("### Chronologie d'Exécution")
        
        for entry in trace:
            step_idx = entry.get('step_index', 'V')
            attempt = entry.get('attempt', 1)
            agent = entry.get('agent', 'Inconnu')
            status = entry.get('statut', 'succès')
            
            status_class = "status-success"
            if status == "échec_validation": status_class = "status-failed"
            elif attempt > 1: status_class = "status-retry"
            
            with st.container():
                st.markdown(f"""
                <div class="trace-card">
                    <div class="trace-header">
                        <div>
                            <span style="font-weight: bold; color: #1e293b;">ÉTAPE {step_idx}</span> 
                            <span style="margin: 0 10px; color: #94a3b8;">|</span>
                            <span style="font-weight: 500;">{agent}</span>
                        </div>
                        <span class="status-badge {status_class}">{status}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Expandable Details
                with st.expander(f"Détails de l'itération (Tentative {attempt})"):
                    if 'instruction' in entry:
                        st.markdown(f"**Instruction** : `{entry['instruction']}`")
                    
                    if 'payload' in entry:
                        st.markdown("**Données d'Entrée (Payload)**")
                        st.json(entry['payload'])
                    
                    if 'raw_result' in entry:
                        st.markdown("**Sortie Brute de l'Agent**")
                        if isinstance(entry['raw_result'], dict):
                            st.json(entry['raw_result'])
                        else:
                            st.code(entry['raw_result'], language="text")
                            
                    if 'feedback' in entry:
                        st.error(f"**Feedback de Correction** : {entry['feedback']}")
                        
                st.markdown("</div>", unsafe_allow_html=True)

st.divider()
st.caption("Généré par le Moteur de Télémétrie de l'Orchestrateur IA")
