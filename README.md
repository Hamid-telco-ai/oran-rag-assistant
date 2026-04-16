# O-RAN GPT – Telecom Knowledge Assistant with RAG

## Overview

O-RAN GPT is a telecom-focused knowledge assistant designed to support engineers working with O-RAN architectures, RIC components, and modern wireless systems. It combines Retrieval-Augmented Generation (RAG), structured domain knowledge, and citation-aware answering to provide reliable, engineering-grade responses.

Unlike generic AI chatbots, this system integrates telecom-specific relationships and controlled reasoning to improve accuracy, reduce hallucinations, and reflect real-world system behavior.

---

## Key Features

* **Telecom-focused knowledge assistant**
  Built specifically for O-RAN, RIC, and wireless network concepts.

* **Retrieval-Augmented Generation (RAG)**
  Combines LLM reasoning with document retrieval to provide grounded answers.

* **Hybrid reasoning (LLM + rule-based layer)**
  Uses structured knowledge (`relationships.json`) to answer certain queries deterministically.

* **Confidence-aware responses**
  Outputs include a confidence signal based on retrieval quality.

* **Strict citation mode**
  Ensures answers are supported by references, reducing hallucinations.

* **Known-unknown handling**
  Uses `known_unknowns.json` to avoid overconfident responses in uncertain areas.

* **Domain-specific knowledge layer**
  Encodes telecom relationships (e.g., O-RAN components, RIC interactions, xApps).

* **Extensible architecture**
  Easily integrates new telecom documents and structured knowledge.

---

## System Architecture

The system follows a hybrid AI architecture combining retrieval, structured reasoning, and LLM-based generation.

### Pipeline

1. **User Query**
2. **Retriever**

   * Searches telecom references and knowledge base
3. **Rule-Based Layer**

   * Checks structured relationships (`relationships.json`)
   * Bypasses LLM for deterministic answers where applicable
4. **LLM Generator**

   * Produces contextual answers using retrieved data
5. **Confidence & Validation Layer**

   * Applies strict citation rules
   * Evaluates confidence level
6. **Final Response**

### Design Philosophy

* Reduce hallucination through retrieval + rules
* Prioritize telecom domain accuracy over generic fluency
* Explicitly model uncertainty (known unknowns)
* Enable explainable AI behavior for engineering use cases

---

## Project Structure

```text
O-RAN-GPT/
├── app.py                     # Main application entry point
├── query_engine.py            # Query handling and orchestration
├── knowledge_engine.py        # Structured knowledge and rule-based logic
├── requirements.txt
├── README.md
├── .gitignore
│
├── knowledge/                 # Structured domain knowledge
│   ├── relationships.json     # Telecom/O-RAN relationships
│   ├── known_unknowns.json    # Controlled uncertainty handling
│   └── kb_evidence.json       # Supporting evidence / extracted knowledge
│
├── references/                # Curated telecom references
├── references_auto/           # Auto-processed knowledge sources
├── tests/                     # Test cases
│
├── scripts/                   # Data processing / pipeline scripts
│   ├── parse_specs.py
│   └── generate_kb.py

```
## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/o-ran-gpt.git
cd o-ran-gpt
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set environment variables

```bash
export OPENAI_API_KEY="your_api_key"
```

### 4. Run the application

```bash
python app.py
```

---

## Example Usage

### Query

```
What is the role of the Near-RT RIC in O-RAN?
```

### Output (example)

```
The Near-RT RIC is responsible for near real-time control of RAN elements (10 ms – 1 s timescale). It hosts xApps that perform functions such as traffic steering, QoS optimization, and interference management.

Confidence: High  
Sources: [RIC architecture reference, O-RAN WG specs]
```

---

## Knowledge Layer

This project uses a hybrid knowledge approach:

* **Unstructured data**

  * Telecom references and documentation

* **Structured data**

  * `relationships.json` → explicit O-RAN relationships
  * `known_unknowns.json` → controlled uncertainty handling

> Note:
> The knowledge layer was built using curated telecom references and selected O-RAN source materials. Raw standards and source documents are not included in this public repository.

---



