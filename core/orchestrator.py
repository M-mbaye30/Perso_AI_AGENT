from typing import List, Dict, Any
import logging
import json
import difflib
from .agent_base import BaseAgent
from .llm_client import OllamaClient

logger = logging.getLogger("core.orchestrator")

class Orchestrator:
    """
    L'Orchestrateur agit comme le cerveau central du système.
    """
    
    def __init__(self, llm_client: OllamaClient):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_client = llm_client
        logger.info("Orchestrator initialized.")

    def register_agent(self, agent: BaseAgent):
        """Enregistrer une nouvelle capacité d'agent."""
        self.agents[agent.name] = agent
        logger.info(f"Agent enregistré : {agent.name} - {agent.description}")

    def _get_agent_fuzzy(self, name: str) -> BaseAgent:
        """Trouve un agent avec une correspondance floue pour gérer les hallucinations du LLM."""
        if name in self.agents:
            return self.agents[name]
        
        # Correspondance floue
        available_names = list(self.agents.keys())
        matches = difflib.get_close_matches(name, available_names, n=1, cutoff=0.6)
        
        if matches:
            best_match = matches[0]
            logger.warning(f"Agent '{name}' non trouvé. Utilisation de la correspondance floue : '{best_match}'")
            return self.agents[best_match]
        
        return None

    def plan_task(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Utilise le LLM pour créer un plan d'exécution.
        """
        agents_info = "\n".join([f"- {name}: {agent.description}" for name, agent in self.agents.items()])
        
        system_prompt = (
            "Vous êtes l'Orchestrateur. Planifiez les étapes pour résoudre la requête de l'utilisateur.\n"
            "Directives d'Utilisation :\n"
            "1. Utilisez 'DocumentAnalysisAgent' pour résumer ou comprendre un texte. POUR LE CHAT GÉNÉRAL/QUESTIONS, UTILISEZ L'INSTRUCTION : 'chat_response'.\n"
            "2. Utilisez 'ReasoningAgent' pour créer un plan ou prendre une décision.\n"
            "3. Utilisez 'ExtractionAgent' pour obtenir des champs JSON spécifiques.\n"
            "4. Utilisez 'ValidationAgent' pour vérifier la qualité.\n"
            "5. Utilisez 'ReportAgent' pour générer des rapports d'étude structurés.\n"
            "6. Utilisez 'WebSearchAgent' pour TOUTE question nécessitant des données externes, faits, actualités ou recherche complexe.\n\n"
            f"Agents Disponibles :\n{agents_info}\n\n"
            "FORMAT DE RÉPONSE : Liste JSON d'étapes.\n"
            "Exemple :\n"
            '{"steps": [\n'
            '  {"agent": "DocumentAnalysisAgent", "instruction": "chat_response", "input_data": "USER_QUERY"},\n'
            '  {"agent": "ExtractionAgent", "instruction": "Extraire les dates", "input_data": "PREVIOUS_RESULT"}\n'
            ']}'
        )
        
        prompt = f"Requête Utilisateur : {user_query}\n\nCréez un plan simple."
        
        try:
            response = self.llm_client.generate(prompt, system_prompt=system_prompt, json_mode=True)
            print(f"DEBUG: Raw Planner Response: {response}") # DEBUG
            
            # Clean response if it contains markdown code blocks
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            plan = json.loads(clean_response)
            print(f"DEBUG: Parsed Plan: {plan}") # DEBUG
            return plan.get("steps", [])
        except Exception as e:
            logger.error(f"Échec de la planification de la tâche : {e}")
            raise

    def run(self, user_query: str, status_callback=None) -> Dict[str, Any]:
        """
        Exécute le flux complet avec les rôles d'Observateur et de Contrôleur.
        status_callback : Fonction optionnelle(step_num, total_steps, agent_name, status) pour les mises à jour UI.
        """
        logger.info(f"Démarrage de l'exécution pour la requête : {user_query}")
        
        if status_callback:
            status_callback(0, 0, "Orchestrator", "Creation du plan d'execution...")
        
        try:
            steps = self.plan_task(user_query)
            logger.info(f"Plan created with {len(steps)} steps.")
        except Exception as e:
            return {"erreur": f"La planification a échoué : {str(e)}"}

        if status_callback:
            status_callback(0, len(steps), "Orchestrator", f"Plan cree avec {len(steps)} etape(s)")

        context = {
            "original_query": user_query,
            "trace": [] # Télémétrie technique détaillée
        }
        last_result = user_query 
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3
        
        i = 0
        while i < len(steps):
            step = steps[i]
            agent_name = step.get("agent")
            instruction = step.get("instruction")
            input_source = step.get("input_data", "")
            
            # Contrôleur : Disjoncteur (Circuit Breaker)
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                logger.error("Trop d'erreurs consécutives. Arrêt.")
                context["erreur"] = "Exécution interrompue : trop d'erreurs consécutives."
                break

            if status_callback:
                status_callback(i + 1, len(steps), agent_name, f"Execution: {instruction[:50]}...")
            
            logger.info(f"Step {i+1}: {agent_name} -> {instruction}")
            
            agent = self._get_agent_fuzzy(agent_name)
            if not agent:
                logger.error(f"Agent {agent_name} not found!")
                context[f"step_{i}_error"] = f"Agent {agent_name} not found"
                consecutive_errors += 1
                i += 1
                continue
                
            # Boucle d'Auto-Correction (Contrôleur & Observateur)
            attempts = 0
            MAX_ATTEMPTS = 3
            step_success = False
            feedback = ""

            while attempts < MAX_ATTEMPTS and not step_success:
                attempts += 1
                try:
                    # Determine "content" to process
                    if input_source == "USER_QUERY" or (i == 0 and not feedback):
                        content_to_process = user_query
                    elif isinstance(last_result, dict):
                        if "analysis" in last_result: content_to_process = last_result["analysis"]
                        elif "extracted_data" in last_result: content_to_process = json.dumps(last_result["extracted_data"])
                        elif "thought_process" in last_result: content_to_process = last_result["thought_process"]
                        else: content_to_process = str(last_result)
                    else:
                        content_to_process = str(last_result) if last_result else user_query

                    # Construction du Payload avec feedback potentiel pour correction
                    payload = {
                        "instruction": f"{instruction} (Correction: {feedback})" if feedback else instruction,
                        "context": context,
                        "text": content_to_process,
                        "content": content_to_process,
                        "goal": instruction,
                        "fields": ["summary", "key_info"] if "Extraction" in agent.name else [],
                        "criteria": instruction
                    }

                    result = agent.process(payload)
                    
                    # Enregistrer l'étape dans la trace de télémétrie
                    context["trace"].append({
                        "id": f"{i}_{attempts}",
                        "step_index": i,
                        "attempt": attempts,
                        "agent": agent.name,
                        "instruction": instruction,
                        "payload": {k: (str(v)[:200] + "...") if isinstance(v, str) and len(str(v)) > 200 else v for k, v in payload.items() if k != "context"},
                        "raw_result": result,
                        "statut": "succès"
                    })
                    
                    # --- Observateur : Vérifications de cohérence (Sanity Checks) ---
                    is_sane = True
                    result_str = str(result).lower()
                    
                    if not result:
                        is_sane = False
                        feedback = "La réponse est vide."
                    elif isinstance(result, dict):
                        # Vérifier si tous les champs pertinents sont vides
                        text_fields = [v for k, v in result.items() if isinstance(v, str) and k not in ['instruction', 'context']]
                        if text_fields and all(not v.strip() for v in text_fields):
                            is_sane = False
                            feedback = "Les champs de réponse sont vides."
                    
                    # Détecter les refus de l'IA
                    if is_sane and any(phrase in result_str for phrase in ["désolé", "je ne peux pas", "i'm sorry", "not able to", "as an ai"]):
                        is_sane = False
                        feedback = f"L'agent a refusé ou n'a pas pu répondre correctement : {result if isinstance(result, str) else 'Refus détecté'}"
                    
                    if not is_sane:
                        logger.warning(f"Échec de la vérification de cohérence pour {agent_name} : {feedback}. Tentative {attempts}/{MAX_ATTEMPTS}")
                        continue

                    # --- Contrôleur : Vérifier s'il y a une étape de validation ---
                    # Si ce n'est PAS un ValidationAgent, mais que l'étape SUIVANTE EST un ValidationAgent
                    if "ValidationAgent" not in agent.name and (i + 1 < len(steps)) and "ValidationAgent" in steps[i+1].get("agent", ""):
                        val_step = steps[i+1]
                        val_agent = self._get_agent_fuzzy("ValidationAgent")
                        if val_agent:
                            val_payload = {
                                "content": str(result),
                                "criteria": val_step.get("instruction", "Vérifier la qualité")
                            }
                            val_result = val_agent.process(val_payload)
                            
                            if not val_result.get("is_valid", True):
                                feedback = val_result.get("feedback", "Validation échouée")
                                logger.warning(f"Validation échouée pour {agent_name} : {feedback}. Re-tentative...")
                                context[f"step_{i}_validation_error"] = feedback
                                # Enregistrer l'échec de validation dans la trace
                                context["trace"].append({
                                    "step": i,
                                    "agent": "ValidationAgent",
                                    "statut": "échec_validation",
                                    "feedback": feedback,
                                    "content": str(result)[:500]
                                })
                                continue # Déclenche la boucle de re-tentative
                    
                    # Si on arrive ici, l'étape est réussie
                    step_success = True
                    context[f"step_{i}_result"] = result
                    context[f"step_{i}_agent"] = agent.name
                    context[agent.name] = result
                    last_result = result
                    consecutive_errors = 0 # Réinitialiser le compteur d'erreurs
                    
                except Exception as e:
                    logger.error(f"Erreur à l'étape {i} (tentative {attempts}) : {e}")
                    feedback = str(e)
                    consecutive_errors += 1

            if not step_success:
                context[f"step_{i}_error"] = f"Échec après {MAX_ATTEMPTS} tentatives. Dernier feedback : {feedback}"
            
            # Si nous avons exécuté manuellement la validation dans le cadre de la boucle de re-tentative, 
            # sauter l'étape suivante si c'était cette validation
            if (i + 1 < len(steps)) and "ValidationAgent" in steps[i+1].get("agent", ""):
                i += 2 # Sauter l'étape de validation car nous l'avons déjà gérée
            else:
                i += 1
                
        return context
