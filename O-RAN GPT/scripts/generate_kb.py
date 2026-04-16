import os
import re
import json
from collections import defaultdict
from pathlib import Path
from docx import Document
import fitz  # PyMuPDF

SPEC_FOLDER = Path("specs")
REF_FOLDER = Path("references_auto")
OUT_JSON = Path("kb_evidence.json")

REF_FOLDER.mkdir(exist_ok=True)

INTERFACES = {
    "A1": {
        "patterns": [r"\ba1\b", r"\ba1 interface\b"],
        "between": "Non-RT RIC ↔ Near-RT RIC",
        "purpose": "Policy-based guidance, enrichment information, and model-related coordination",
        "type": "Non-real-time interface",
    },
    "E2": {
        "patterns": [r"\be2\b", r"\be2 interface\b"],
        "between": "Near-RT RIC ↔ E2 Nodes (e.g., O-CU-CP, O-CU-UP, O-DU)",
        "purpose": "Near-real-time monitoring and control",
        "type": "Near-real-time interface",
    },
    "O1": {
        "patterns": [r"\bo1\b", r"\bo1 interface\b"],
        "between": "SMO ↔ O-RAN Network Functions",
        "purpose": "Operations, administration, management, telemetry, and configuration",
        "type": "Management interface",
    },
    "O2": {
        "patterns": [r"\bo2\b", r"\bo2 interface\b"],
        "between": "SMO ↔ O-Cloud",
        "purpose": "Cloud resource, infrastructure, and workload management",
        "type": "Orchestration interface",
    },
    "Y1": {
        "patterns": [r"\by1\b", r"\by1 interface\b"],
        "between": "Near-RT RIC ↔ Y1 consumers",
        "purpose": "Exposure of RAN analytics services",
        "type": "Analytics exposure interface",
    },
    "R1": {
        "patterns": [r"\br1\b", r"\br1 interface\b"],
        "between": "rApps ↔ Non-RT RIC framework / SMO services",
        "purpose": "Service-based interaction for rApps",
        "type": "Service-based interface",
    },
    "Open Fronthaul": {
        "patterns": [r"open fronthaul", r"fh m-plane", r"m-plane"],
        "between": "O-DU ↔ O-RU",
        "purpose": "Transport of fronthaul management, synchronization, control, and user-plane related functions",
        "type": "Fronthaul interface family",
    },
}

COMPONENTS = {
    "SMO": {
        "patterns": [r"\bsmo\b", r"service management and orchestration"],
        "role": "Central management, orchestration, and automation layer",
        "interfaces": ["O1", "O2"],
    },
    "Non-RT RIC": {
        "patterns": [r"\bnon-rt ric\b", r"non-real-time ran intelligent controller"],
        "role": "Non-real-time optimization and policy layer",
        "interfaces": ["A1", "R1"],
    },
    "Near-RT RIC": {
        "patterns": [r"\bnear-rt ric\b", r"near-real-time ran intelligent controller"],
        "role": "Near-real-time control and optimization layer",
        "interfaces": ["E2", "A1", "O1", "Y1"],
    },
    "O-CU-CP": {
        "patterns": [r"\bo-cu-cp\b", r"central unit.?control plane"],
        "role": "Control-plane central unit",
        "interfaces": ["E2", "O1"],
    },
    "O-CU-UP": {
        "patterns": [r"\bo-cu-up\b", r"central unit.?user plane"],
        "role": "User-plane central unit",
        "interfaces": ["E2", "O1"],
    },
    "O-DU": {
        "patterns": [r"\bo-du\b", r"o-ran distributed unit"],
        "role": "Distributed unit hosting RLC, MAC, and High-PHY functions",
        "interfaces": ["E2", "O1", "Open Fronthaul"],
    },
    "O-RU": {
        "patterns": [r"\bo-ru\b", r"o-ran radio unit"],
        "role": "Radio unit hosting Low-PHY and RF functions",
        "interfaces": ["Open Fronthaul"],
    },
    "O-Cloud": {
        "patterns": [r"\bo-cloud\b", r"o-ran cloud"],
        "role": "Cloud platform hosting O-RAN functions and workloads",
        "interfaces": ["O2"],
    },
    "xApp": {
        "patterns": [r"\bxapp\b", r"\bxapps\b"],
        "role": "Application running on Near-RT RIC for near-real-time optimization and control",
        "interfaces": ["E2"],
    },
    "rApp": {
        "patterns": [r"\brapp\b", r"\brapps\b"],
        "role": "Application running on Non-RT RIC for non-real-time optimization and policy generation",
        "interfaces": ["R1", "A1"],
    },
}

GLOSSARY = {
    "E2 Node": [r"\be2 node\b"],
    "A1 Policy": [r"a1 policy", r"a1 policies"],
    "Enrichment Information": [r"enrichment information", r"\bei\b"],
    "Control Loop": [r"control loop", r"closed-loop", r"closed loop"],
    "Service Model": [r"e2sm", r"service model"],
    "Managed Function": [r"managed function"],
    "O-RAN NF": [r"o-ran network function", r"\bo-ran nf\b"],
    "Intent": [r"\bintent\b", r"intent owner", r"intent handler"],
}

NOISE_PATTERNS = [
    r"^\s*\d+(\.\d+)*\s+",
    r"\.{5,}",
    r"^annex\b",
    r"^table\b",
    r"^figure\b",
    r"^contents\b",
    r"^\[\d+\]",
]

def extract_docx(path: Path) -> list[str]:
    doc = Document(path)
    lines = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            lines.append(text)
    return lines

def extract_pdf(path: Path) -> list[str]:
    doc = fitz.open(path)
    lines = []
    for page in doc:
        content = page.get_text()
        for line in content.split("\n"):
            text = line.strip()
            if text:
                lines.append(text)
    return lines

def is_noise(line: str) -> bool:
    lower = line.lower().strip()
    if len(lower) < 3:
        return True
    return any(re.search(pattern, lower) for pattern in NOISE_PATTERNS)

def clean_lines(lines: list[str]) -> list[str]:
    cleaned = []
    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if not is_noise(line):
            cleaned.append(line)
    return cleaned

def collect_lines() -> dict[str, list[str]]:
    docs = {}
    for path in SPEC_FOLDER.iterdir():
        if path.suffix.lower() == ".docx":
            docs[path.name] = clean_lines(extract_docx(path))
        elif path.suffix.lower() == ".pdf":
            docs[path.name] = clean_lines(extract_pdf(path))
    return docs

def gather_evidence(docs: dict[str, list[str]], catalog: dict) -> dict:
    result = {}
    for item, meta in catalog.items():
        patterns = meta["patterns"] if isinstance(meta, dict) else meta
        result[item] = {"matches": []}
        for filename, lines in docs.items():
            for line in lines:
                lower = line.lower()
                if any(re.search(p, lower) for p in patterns):
                    result[item]["matches"].append({"source": filename, "text": line})
        # deduplicate
        seen = set()
        deduped = []
        for match in result[item]["matches"]:
            key = (match["source"], match["text"])
            if key not in seen:
                seen.add(key)
                deduped.append(match)
        result[item]["matches"] = deduped[:12]
    return result

def write_interfaces_md(evidence: dict):
    lines = ["# O-RAN Interfaces", ""]
    for name, meta in INTERFACES.items():
        lines += [
            f"## {name}",
            f"- Between: {meta['between']}",
            f"- Purpose: {meta['purpose']}",
            f"- Type: {meta['type']}",
        ]
        if name == "E2":
            lines.append("- Notes: Uses E2 Service Models (E2SM) for structured monitoring and control.")
        if name == "O2":
            lines.append("- Notes: Can include infrastructure management and deployment/lifecycle management roles.")
        matches = evidence[name]["matches"]
        if matches:
            lines.append("- Evidence:")
            for m in matches[:3]:
                lines.append(f"  - {m['source']}: {m['text']}")
        lines += ["", "---", ""]
    (REF_FOLDER / "interfaces.md").write_text("\n".join(lines), encoding="utf-8")

def write_components_md(evidence: dict):
    lines = ["# O-RAN Components", ""]
    for name, meta in COMPONENTS.items():
        lines += [
            f"## {name}",
            f"- Role: {meta['role']}",
            f"- Key interfaces: {', '.join(meta['interfaces'])}",
        ]
        matches = evidence[name]["matches"]
        if matches:
            lines.append("- Evidence:")
            for m in matches[:3]:
                lines.append(f"  - {m['source']}: {m['text']}")
        lines += ["", "---", ""]
    (REF_FOLDER / "components.md").write_text("\n".join(lines), encoding="utf-8")

def write_glossary_md(evidence: dict):
    lines = ["# O-RAN Glossary", ""]
    for term, meta in evidence.items():
        lines.append(f"## {term}")
        matches = meta["matches"]
        if matches:
            lines.append(f"- Evidence term found in source documents.")
            lines.append("- Evidence:")
            for m in matches[:3]:
                lines.append(f"  - {m['source']}: {m['text']}")
        else:
            lines.append("- Evidence not found in current seed documents.")
        lines += ["", "---", ""]
    (REF_FOLDER / "glossary.md").write_text("\n".join(lines), encoding="utf-8")

def main():
    docs = collect_lines()
    if not docs:
        raise FileNotFoundError("No .pdf or .docx files found in specs/")

    interface_evidence = gather_evidence(docs, INTERFACES)
    component_evidence = gather_evidence(docs, COMPONENTS)
    glossary_evidence = gather_evidence(docs, GLOSSARY)

    write_interfaces_md(interface_evidence)
    write_components_md(component_evidence)
    write_glossary_md(glossary_evidence)

    payload = {
        "interfaces": interface_evidence,
        "components": component_evidence,
        "glossary": glossary_evidence,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Generated:")
    print("- references/interfaces.md")
    print("- references/components.md")
    print("- references/glossary.md")
    print("- kb_evidence.json")

if __name__ == "__main__":
    main()