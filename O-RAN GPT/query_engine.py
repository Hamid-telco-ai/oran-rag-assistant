from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import List, Tuple


REF_DIR = Path("references")
SKILL_FILE = Path("SKILL.md")


@dataclass
class Chunk:
    source: str
    heading: str
    text: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_markdown_into_chunks(file_path: Path) -> List[Chunk]:
    text = read_text(file_path)
    lines = text.splitlines()

    chunks: List[Chunk] = []
    current_heading = "Introduction"
    current_lines: List[str] = []

    def flush() -> None:
        nonlocal current_lines
        body = "\n".join(current_lines).strip()
        if body:
            chunks.append(
                Chunk(
                    source=file_path.name,
                    heading=current_heading,
                    text=body,
                )
            )
        current_lines = []

    for line in lines:
        if line.startswith("## "):
            flush()
            current_heading = line[3:].strip()
        else:
            current_lines.append(line)

    flush()
    return chunks


def load_knowledge_chunks() -> List[Chunk]:
    chunks: List[Chunk] = []
    for path in sorted(REF_DIR.glob("*.md")):
        chunks.extend(split_markdown_into_chunks(path))
    return chunks


def load_skill_text() -> str:
    if SKILL_FILE.exists():
        return read_text(SKILL_FILE)
    return ""


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9\-\+]+", text.lower())


SYNONYM_MAP = {
    "near real time ric": "near-rt ric",
    "near real-time ric": "near-rt ric",
    "non real time ric": "non-rt ric",
    "non real-time ric": "non-rt ric",
    "near rt ric": "near-rt ric",
    "non rt ric": "non-rt ric",
    "x app": "xapp",
    "r app": "rapp",
    "open fh": "open fronthaul",
    "fronthaul": "open fronthaul",
    "fh m-plane": "open fronthaul",
    "fh": "open fronthaul",
    "cloud": "o-cloud",
    "orchestration and management": "smo",
}


def normalize_text(text: str) -> str:
    normalized = text.lower()
    for old, new in SYNONYM_MAP.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


INTERFACE_TERMS = {
    "a1", "e2", "o1", "o2", "y1", "r1",
    "open", "fronthaul", "interface", "interfaces", "e2sm"
}

COMPONENT_TERMS = {
    "smo", "non-rt", "near-rt", "ric", "xapp", "rapp",
    "o-cu", "o-cu-cp", "o-cu-up", "o-du", "o-ru", "o-cloud",
    "component", "components", "node", "nodes"
}

ARCHITECTURE_TERMS = {
    "architecture", "layer", "layers", "system", "flow",
    "control", "loop", "loops", "end-to-end", "hierarchical"
}

DEFINITION_TERMS = {
    "what", "what is", "define", "definition", "meaning", "term"
}

FLOW_TERMS = {
    "how", "flow", "steps", "sequence", "procedure", "control loop",
    "end-to-end", "integrated", "interaction"
}

BOUNDARY_TERMS = {
    "does", "is", "replace", "used for", "run on", "allowed", "not"
}


def detect_question_type(question: str) -> str:
    q = normalize_text(question)
    tokens = set(tokenize(q))

    interface_score = len(tokens.intersection(INTERFACE_TERMS))
    component_score = len(tokens.intersection(COMPONENT_TERMS))
    architecture_score = len(tokens.intersection(ARCHITECTURE_TERMS))
    definition_score = len(tokens.intersection(DEFINITION_TERMS))
    flow_score = len(tokens.intersection(FLOW_TERMS))
    boundary_score = len(tokens.intersection(BOUNDARY_TERMS))

    if "difference between" in q or "compare" in q:
        if any(x in q for x in ["a1", "e2", "o1", "o2", "y1", "r1", "open fronthaul", "interface"]):
            return "interface_comparison"
        if any(x in q for x in ["xapp", "rapp", "smo", "ric", "o-du", "o-ru", "o-cloud"]):
            return "component_comparison"

    if q.startswith("what is ") or q.startswith("define "):
        if any(x in q for x in ["a1", "e2", "o1", "o2", "y1", "r1", "open fronthaul"]):
            return "interface_definition"
        if any(x in q for x in ["near-rt ric", "non-rt ric", "smo", "xapp", "rapp", "o-cloud", "e2 node"]):
            return "definition"

    if any(x in q for x in ["control loop", "end-to-end", "full oran control", "architecture"]):
        return "architecture"

    if "how" in q and any(x in q for x in ["xapp", "rapp", "interact", "integrated", "control"]):
        return "flow"

    if boundary_score > 0 and any(x in q for x in ["replace", "run on", "used for real-time", "used for control"]):
        return "boundary"

    if architecture_score >= max(interface_score, component_score, definition_score, flow_score) and architecture_score > 0:
        return "architecture"
    if flow_score >= max(interface_score, component_score, definition_score) and flow_score > 0:
        return "flow"
    if interface_score >= max(component_score, definition_score) and interface_score > 0:
        return "interface"
    if component_score >= definition_score and component_score > 0:
        return "component"
    if definition_score > 0:
        return "definition"

    return "general"


def get_file_weight(question_type: str, source_file: str) -> float:
    weights = {
        "interface": {
            "interfaces.md": 3.2,
            "components.md": 1.3,
            "architecture.md": 1.2,
            "glossary.md": 1.1,
        },
        "interface_comparison": {
            "interfaces.md": 3.6,
            "architecture.md": 1.5,
            "components.md": 1.2,
            "glossary.md": 1.1,
        },
        "interface_definition": {
            "interfaces.md": 3.3,
            "glossary.md": 1.7,
            "components.md": 1.2,
            "architecture.md": 1.1,
        },
        "component": {
            "components.md": 3.2,
            "architecture.md": 1.6,
            "glossary.md": 1.4,
            "interfaces.md": 1.1,
        },
        "component_comparison": {
            "components.md": 3.5,
            "architecture.md": 1.7,
            "glossary.md": 1.3,
            "interfaces.md": 1.1,
        },
        "architecture": {
            "architecture.md": 3.5,
            "components.md": 1.6,
            "interfaces.md": 1.4,
            "glossary.md": 1.1,
        },
        "definition": {
            "glossary.md": 3.2,
            "components.md": 1.8,
            "interfaces.md": 1.7,
            "architecture.md": 1.2,
        },
        "flow": {
            "architecture.md": 3.0,
            "components.md": 1.8,
            "interfaces.md": 1.7,
            "glossary.md": 1.1,
        },
        "boundary": {
            "architecture.md": 2.1,
            "components.md": 2.0,
            "interfaces.md": 1.8,
            "glossary.md": 1.2,
        },
        "general": {
            "architecture.md": 1.5,
            "components.md": 1.5,
            "interfaces.md": 1.5,
            "glossary.md": 1.5,
        },
    }
    return weights.get(question_type, weights["general"]).get(source_file, 1.0)


def heading_bonus(question_type: str, heading: str) -> float:
    h = normalize_text(heading)

    if question_type in {"interface", "interface_comparison", "interface_definition"}:
        if any(x in h for x in ["a1", "e2", "o1", "o2", "y1", "r1", "open fronthaul"]):
            return 2.2
    elif question_type in {"component", "component_comparison"}:
        if any(x in h for x in ["smo", "near-rt ric", "non-rt ric", "xapp", "rapp", "o-cu", "o-du", "o-ru", "o-cloud"]):
            return 2.2
    elif question_type == "architecture":
        if any(x in h for x in ["overview", "layered architecture", "interface mapping", "control loop architecture", "end-to-end control flow"]):
            return 2.3
    elif question_type == "flow":
        if any(x in h for x in ["control flow", "end-to-end control flow", "control loop architecture", "interface mapping", "near-rt ric", "xapp"]):
            return 2.1
    elif question_type == "definition":
        return 1.4

    return 1.0


def phrase_bonus(question: str, chunk: Chunk) -> float:
    q = normalize_text(question)
    heading = normalize_text(chunk.heading)
    body = normalize_text(chunk.text)

    tracked_phrases = [
        "a1", "e2", "o1", "o2", "y1", "r1", "open fronthaul",
        "near-rt ric", "non-rt ric", "o-cloud", "xapp", "rapp",
        "smo", "e2 node", "control loop", "ai/ml", "architecture"
    ]

    bonus = 0.0
    for phrase in tracked_phrases:
        if phrase in q and phrase in heading:
            bonus += 2.2
        elif phrase in q and phrase in body:
            bonus += 0.9

    if "difference between" in q or "compare" in q:
        if "difference" in body or "compare" in body:
            bonus += 1.0

    if "what is" in q and len(chunk.text) < 1200:
        bonus += 0.3

    return bonus


def noise_penalty(chunk: Chunk) -> float:
    text = normalize_text(chunk.text)

    penalty = 0.0

    if text.count("evidence:") > 0:
        penalty += 0.3

    if len(text) < 40:
        penalty += 0.8

    noisy_markers = ["evidence:", "section:", "source:", "---"]
    noisy_hits = sum(1 for x in noisy_markers if x in text)
    penalty += 0.15 * noisy_hits

    return penalty


def score_chunk(question: str, chunk: Chunk) -> float:
    q_norm = normalize_text(question)
    q_tokens = set(tokenize(q_norm))
    text_tokens = set(tokenize(normalize_text(chunk.heading + " " + chunk.text)))

    overlap = q_tokens.intersection(text_tokens)
    base_score = len(overlap)

    if base_score == 0:
        return 0.0

    qtype = detect_question_type(question)
    file_weight = get_file_weight(qtype, chunk.source)
    title_weight = heading_bonus(qtype, chunk.heading)
    extra_phrase_bonus = phrase_bonus(question, chunk)
    penalty = noise_penalty(chunk)

    final_score = ((base_score + extra_phrase_bonus) * file_weight * title_weight) - penalty
    return max(final_score, 0.0)


def select_diverse_chunks(scored_chunks: List[Tuple[float, Chunk]], top_k: int) -> List[Chunk]:
    """
    Prefer diversity across files first, then fill remaining slots by score.
    """
    selected: List[Chunk] = []
    used_files = set()

    # first pass: best chunk per file
    for score, chunk in scored_chunks:
        if score <= 0:
            continue
        if chunk.source not in used_files:
            selected.append(chunk)
            used_files.add(chunk.source)
        if len(selected) >= top_k:
            return selected

    # second pass: fill remaining by best overall
    for score, chunk in scored_chunks:
        if score <= 0:
            continue
        if chunk not in selected:
            selected.append(chunk)
        if len(selected) >= top_k:
            return selected

    return selected

def extract_query_entities(question: str) -> set[str]:
    q = normalize_text(question)

    tracked_entities = {
        "a1", "e2", "o1", "o2", "y1", "r1", "open fronthaul",
        "f1", "e1", "xn", "x2", "near-rt ric", "non-rt ric",
        "smo", "xapp", "rapp", "o-cloud", "o-cu", "o-cu-cp",
        "o-cu-up", "o-du", "o-ru", "e2 node"
    }

    found = set()
    for entity in tracked_entities:
        if entity in q:
            found.add(entity)

    return found

def retrieved_chunks_cover_entities(question: str, chunks: List[Chunk]) -> bool:
    entities = extract_query_entities(question)

    if not entities:
        return True

    combined_text = " ".join(
        normalize_text(chunk.heading + " " + chunk.text) for chunk in chunks
    )

    for entity in entities:
        if entity not in combined_text:
            return False

    return True

def compute_confidence(question: str, scored_chunks: List[Tuple[float, Chunk]]) -> str:
    positive = [(score, chunk) for score, chunk in scored_chunks if score > 0]
    if not positive:
        return "low"

    best = positive[0][0]
    total = sum(score for score, _ in positive[:3])
    top_chunks = [chunk for _, chunk in positive[:5]]

    # Entity coverage check: if asked entity is not actually covered, confidence must be low
    if not retrieved_chunks_cover_entities(question, top_chunks):
        return "low"

    if best >= 18 and total >= 30:
        return "high"
    if best >= 8:
        return "medium"
    return "low"

def retrieve_relevant_chunks(question: str, top_k: int = 5) -> List[Chunk]:
    chunks = load_knowledge_chunks()
    scored = [(score_chunk(question, chunk), chunk) for chunk in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)
    return select_diverse_chunks(scored, top_k=top_k)


def build_context(question: str, top_k: int = 5) -> str:
    skill = load_skill_text()
    chunks = load_knowledge_chunks()
    scored = [(score_chunk(question, chunk), chunk) for chunk in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)

    top_chunks = select_diverse_chunks(scored, top_k=top_k)
    question_type = detect_question_type(question)
    confidence = compute_confidence(question, scored)

    parts = []
    if skill:
        parts.append("## Skill Rules\n" + skill)

    parts.append(f"## Question Type\n{question_type}")
    parts.append(f"## Retrieval Confidence\n{confidence}")

    if top_chunks:
        parts.append("## Local Knowledge Base")
        for i, chunk in enumerate(top_chunks, start=1):
            parts.append(
                f"""### Source [{i}]
File: {chunk.source}
Section: {chunk.heading}

{chunk.text}
"""
            )

    return "\n\n".join(parts)


def build_source_list(question: str, top_k: int = 5) -> List[str]:
    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    labels = []
    for i, c in enumerate(chunks, start=1):
        labels.append(f"[{i}] {c.source} → {c.heading}")
    return labels


def answer_without_llm(question: str) -> str:
    chunks = load_knowledge_chunks()
    scored = [(score_chunk(question, chunk), chunk) for chunk in chunks]
    scored.sort(key=lambda x: x[0], reverse=True)

    top_chunks = select_diverse_chunks(scored, top_k=5)
    if not top_chunks:
        return "Not defined in current knowledge base."

    qtype = detect_question_type(question)
    confidence = compute_confidence(question, scored)

    lines = [
        f"Detected question type: **{qtype}**",
        f"Retrieval confidence: **{confidence}**",
        "",
        "Relevant O-RAN knowledge found:",
        "",
    ]
    for i, chunk in enumerate(top_chunks, start=1):
        lines.append(f"- **[{i}] {chunk.source} / {chunk.heading}**")
        snippet = chunk.text[:350].strip()
        lines.append(f"  {snippet}...")
    return "\n".join(lines)