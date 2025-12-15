# Enterprise AI Orchestrator

## Overview

The **Enterprise AI Orchestrator** is a self-hosted, autonomous multi-agent system designed for secure document analysis and strategic reasoning. It leverages local Large Language Models (LLMs) to ensure data sovereignty and compliance with strict privacy regulations.

Unlike traditional RAG pipelines, this system employs an **Agentic Architecture** where specialized agents (Analysis, Extraction, Reasoning, Validation) collaborate to solve complex tasks dynamically.

## Key Features

- **Data Sovereignty**: Runs entirely On-Premise (Local GPU/CPU). No data leaves your infrastructure.
- **Agentic Orchestration**: Autonomous planning and delegation of tasks.
- **Document Intelligence**: Native PDF support with semantic analysis.
- **Modular Design**: extensible `core` and `agents` architecture.

## Architecture

The system is built on a modular Python framework:

- **Core**:
  - `Orchestrator`: Central intelligence managing workflow and state.
  - `OllamaClient`: Secure wrapper for local LLM inference (e.g., Llama 3).
- **Agents**:
  - `DocumentAnalysisAgent`: Summarization and key topic identification.
  - `ExtractionAgent`: Structured data extraction (JSON) from unstructured text.
  - `ReasoningAgent`: Complex problem decomposition and planning.
  - `ValidationAgent`: Quality control and hallucination checking.

## Usage

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) (running locally)
- Model: `llama3.2:1b` (optimized for standard workstations)

### Installation

```bash
pip install -r requirements.txt
# Ensure pypdf is installed for document support
pip install pypdf
```

### Running the System

1. **Start the Local LLM**:

    ```bash
    ollama serve
    ```

2. **Launch the Dashboard**:

    ```bash
    streamlit run streamlit_app.py
    ```

## Security Note

This application is designed for **local deployment**. API keys or external cloud credentials are **not required**. Ensure your local Ollama instance is secured if exposed on a network.
