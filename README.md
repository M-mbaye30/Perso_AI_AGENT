# Orchestrateur IA Agentique

L'**Orchestrateur IA** est un système autonome piloté par une intelligence agentique et un état global évolutif. Conçu pour l'analyse documentaire et le raisonnement stratégique, il déploie des agents spécialisés coordonnés de manière itérative pour garantir la précision et la robustesse des résultats.

Contrairement aux pipelines RAG classiques, cette architecture s'appuie sur une boucle de contrôle dynamique où la planification, l'exécution et la validation permettent une auto-correction autonome face aux tâches complexes.

## Fonctionnalités Clés

- **Souveraineté des Données** : Fonctionne entièrement sur site (GPU/CPU local). Aucune donnée ne quitte votre infrastructure.
- **Orchestration Agentique** : Planification et délégation autonome des tâches.
- **Intelligence Documentaire** : Support natif des PDF avec analyse sémantique.
- **Recherche Web Avancée** : Investigation en ligne avec vérification croisée des sources.
- **Design Modulaire** : Architecture extensible pour les composants `core` et les `agents`.

## Architecture

Le système est construit sur un framework Python modulaire :

- **Cœur (Core)** :
  - `Orchestrator` : Intelligence centrale gérant le flux de travail et l'état.
  - `OllamaClient` : Interface sécurisée pour l'inférence LLM locale (ex: Llama 3) ou l'API Gemini.
- **Agents** :
  - `DocumentAnalysisAgent` : Résumé et identification des sujets clés.
  - `ExtractionAgent` : Extraction de données structurées (JSON) à partir de textes bruts.
  - `ReasoningAgent` : Décomposition de problèmes complexes et planification.
  - `ValidationAgent` : Contrôle qualité et vérification des hallucinations.
  - `WebSearchAgent` : Recherche web approfondie et synthèse d'informations.
  - `ReportAgent` : Génération de rapports structurés et professionnels.

## Ressources & Présentation

Vous trouverez une présentation détaillée des principes de l'agent et de son architecture dans le dossier dédié :

- [**Présentation : Architecture et Principes**](presentation/L'Agent%20IA%20-%20Architecture%20et%20Principes.pdf)

## Démonstration Vidéo

> [!TIP]
> **[Regarder la vidéo de démonstration complète ici](demo/demo_video.webm)** (Lien à mettre à jour après l'upload)

![Démo de l'Interface](demo/interface_preview.png)

## Utilisation

### Prérequis

- Python 3.10+
- [Ollama](https://ollama.com/) (pour une exécution locale)
- Modèle recommandé : `llama3.2:1b` ou `llama3.2:3b`

### Installation

```bash
pip install -r requirements.txt
# Support PDF inclus via pypdf
```

### Lancement du Système

1. **Démarrer l'instance locale Ollama** (si utilisé) :

    ```bash
    ollama serve
    ```

2. **Lancer le Tableau de Bord** :

    ```bash
    streamlit run streamlit_app.py
    ```
