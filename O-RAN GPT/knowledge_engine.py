from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


KNOWLEDGE_DIR = Path("knowledge")


def load_json(name: str) -> Any:
    path = KNOWLEDGE_DIR / name
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


INTERFACES = load_json("interfaces.json") or []
COMPONENTS = load_json("components.json") or []
RELATIONSHIPS = load_json("relationships.json") or []
KNOWN_UNKNOWNS = load_json("known_unknowns.json") or {"known_unknowns": []}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9\-\+]+", normalize(text))


def get_known_unknown(question: str) -> dict | None:
    q = normalize(question)
    for item in KNOWN_UNKNOWNS.get("known_unknowns", []):
        term = normalize(item["term"])
        if re.search(rf"\b{re.escape(term)}\b", q):
            return item
    return None


def find_component_by_name(name: str) -> dict | None:
    n = normalize(name)
    for rec in COMPONENTS:
        names = [rec.get("name", "")] + rec.get("aliases", [])
        for item in names:
            if normalize(item) == n:
                return rec
    return None


def find_interface_by_name(name: str) -> dict | None:
    n = normalize(name)
    for rec in INTERFACES:
        names = [rec.get("name", "")] + rec.get("aliases", [])
        for item in names:
            if normalize(item) == n:
                return rec
    return None


def match_record(question: str, records: list[dict]) -> list[dict]:
    q = normalize(question)
    q_tokens = set(tokenize(q))

    scored = []
    for record in records:
        names = [record.get("name", "")]
        names.extend(record.get("aliases", []))

        text_parts = names + [
            record.get("definition", ""),
            record.get("purpose", ""),
            record.get("role", ""),
            " ".join(record.get("between", [])),
            " ".join(record.get("related_components", [])),
            " ".join(record.get("related_terms", [])),
            " ".join(record.get("uses_interfaces", [])),
        ]
        record_text = normalize(" ".join(text_parts))
        record_tokens = set(tokenize(record_text))

        score = len(q_tokens.intersection(record_tokens))

        exact_bonus = 0
        for n in names:
            n_norm = normalize(n)
            if n_norm and re.search(rf"\b{re.escape(n_norm)}\b", q):
                exact_bonus += 6

        score += exact_bonus

        if score > 0:
            scored.append((score, record))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:5]]


def detect_question_intent(question: str) -> str:
    q = normalize(question)

    if "difference between" in q or "compare" in q:
        return "comparison"
    if any(x in q for x in ["connects", "relationship", "interact", "used by", "runs on", "hosts"]):
        return "relationship"
    if any(x in q for x in ["what is", "define", "meaning of"]):
        return "definition"
    if any(x in q for x in ["how does", "explain", "flow", "end-to-end", "control loop"]):
        return "flow"
    return "general"


def find_relationships(question: str) -> list[dict]:
    q = normalize(question)
    q_tokens = set(tokenize(q))

    scored = []
    for rel in RELATIONSHIPS:
        rel_text = normalize(
            f"{rel.get('from', '')} {rel.get('relation', '')} {rel.get('to', '')} {rel.get('category', '')}"
        )
        rel_tokens = set(tokenize(rel_text))
        score = len(q_tokens.intersection(rel_tokens))
        if score > 0:
            scored.append((score, rel))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:6]]


def extract_entities_from_question(question: str) -> list[str]:
    q = normalize(question)
    candidates = []

    all_names = []
    for rec in COMPONENTS + INTERFACES:
        all_names.append(rec.get("name", ""))
        all_names.extend(rec.get("aliases", []))

    # longest first so "near-rt ric" matches before "ric"
    all_names = sorted(set(x for x in all_names if x), key=len, reverse=True)

    for name in all_names:
        n = normalize(name)
        if n and re.search(rf"\b{re.escape(n)}\b", q):
            candidates.append(name)

    return candidates


def relationship_answer(question: str) -> dict | None:
    """
    Return a rule-based answer dict for deterministic relationship questions.
    """
    q = normalize(question)
    entities = extract_entities_from_question(question)

    # what runs on X?
    if "runs on" in q or (q.startswith("what runs on") and entities):
        if entities:
            target = entities[0]
            matches = [
                rel for rel in RELATIONSHIPS
                if rel.get("relation") == "runs_on" and normalize(rel.get("to", "")) == normalize(target)
            ]
            if matches:
                items = [rel["from"] for rel in matches]
                answer = f"{target} hosts {', '.join(items)}."
                return {
                    "answer": answer,
                    "confidence": "high",
                    "source_type": "structured knowledge",
                    "references": matches,
                }

    # what does X host?
    if "host" in q and entities:
        target = entities[0]
        matches = [
            rel for rel in RELATIONSHIPS
            if rel.get("relation") == "hosts" and normalize(rel.get("from", "")) == normalize(target)
        ]
        if matches:
            items = [rel["to"] for rel in matches]
            answer = f"{target} hosts {', '.join(items)}."
            return {
                "answer": answer,
                "confidence": "high",
                "source_type": "structured knowledge",
                "references": matches,
            }

    # what interfaces does X use?
    if ("interfaces" in q or "interface" in q) and ("use" in q or "does" in q) and entities:
        target = entities[0]
        matches = [
            rel for rel in RELATIONSHIPS
            if rel.get("relation") == "uses_interface" and normalize(rel.get("from", "")) == normalize(target)
        ]
        if matches:
            items = [rel["to"] for rel in matches]
            answer = f"{target} uses the following interfaces: {', '.join(items)}."
            return {
                "answer": answer,
                "confidence": "high",
                "source_type": "structured knowledge",
                "references": matches,
            }

    # what connects X and Y?
    if "connects" in q and len(entities) >= 2:
        a, b = entities[0], entities[1]
        matches = []
        for rel in RELATIONSHIPS:
            if rel.get("relation") != "connects":
                continue
            if normalize(rel.get("to", "")) in {normalize(a), normalize(b)}:
                matches.append(rel)

        grouped = {}
        for rel in matches:
            grouped.setdefault(rel["from"], set()).add(normalize(rel["to"]))

        for interface_name, endpoints in grouped.items():
            if normalize(a) in endpoints and normalize(b) in endpoints:
                supporting = [r for r in matches if r["from"] == interface_name]
                answer = f"{interface_name} connects {a} and {b}."
                return {
                    "answer": answer,
                    "confidence": "high",
                    "source_type": "structured knowledge",
                    "references": supporting,
                }

    # which components are in the real-time loop?
    if "real-time loop" in q and ("which components" in q or "what components" in q):
        matches = [
            rel for rel in RELATIONSHIPS
            if rel.get("relation") == "operates_in" and normalize(rel.get("to", "")) == "real-time loop"
        ]
        if matches:
            items = [rel["from"] for rel in matches]
            answer = f"The components operating in the real-time loop are: {', '.join(items)}."
            return {
                "answer": answer,
                "confidence": "high",
                "source_type": "structured knowledge",
                "references": matches,
            }

    return None


def build_knowledge_context(question: str) -> tuple[str, str]:
    unknown = get_known_unknown(question)
    if unknown:
        context = f"""## Known Unknown
Term: {unknown['term']}
Category: {unknown['category']}
Status: {unknown['status']}
Reason: {unknown['reason']}
Note: {unknown['note']}
"""
        return context, "low"

    intent = detect_question_intent(question)
    interfaces = match_record(question, INTERFACES)
    components = match_record(question, COMPONENTS)
    relationships = find_relationships(question)

    parts = [f"## Knowledge Intent\n{intent}"]

    if interfaces:
        parts.append("## Matched Interfaces")
        for i, rec in enumerate(interfaces, start=1):
            parts.append(
                f"""### Interface [{i}]
Name: {rec.get('name')}
Aliases: {", ".join(rec.get('aliases', []))}
Definition: {rec.get('definition')}
Between: {", ".join(rec.get('between', []))}
Purpose: {rec.get('purpose')}
Timing: {rec.get('timing_domain')}
Related Components: {", ".join(rec.get('related_components', []))}
Common Confusions: {", ".join(rec.get('common_confusions', []))}
"""
            )

    if components:
        parts.append("## Matched Components")
        for i, rec in enumerate(components, start=1):
            parts.append(
                f"""### Component [{i}]
Name: {rec.get('name')}
Aliases: {", ".join(rec.get('aliases', []))}
Definition: {rec.get('definition')}
Role: {rec.get('role')}
Hosts: {", ".join(rec.get('hosts', []))}
Interfaces: {", ".join(rec.get('uses_interfaces', []))}
Related Components: {", ".join(rec.get('related_components', []))}
Common Confusions: {", ".join(rec.get('common_confusions', []))}
"""
            )

    if relationships:
        parts.append("## Matched Relationships")
        for i, rel in enumerate(relationships, start=1):
            parts.append(
                f"""### Relationship [{i}]
From: {rel.get('from')}
Relation: {rel.get('relation')}
To: {rel.get('to')}
Category: {rel.get('category')}
"""
            )

    matched_count = len(interfaces) + len(components) + len(relationships)

    if matched_count >= 4:
        confidence = "high"
    elif matched_count >= 2:
        confidence = "medium"
    else:
        confidence = "low"

    if matched_count == 0:
        return "", "low"

    return "\n\n".join(parts), confidence