import os
import re
from collections import defaultdict
from docx import Document
import fitz  # PyMuPDF

FOLDER = "specs"

ENTITY_KEYWORDS = {
    "SMO": [r"\bsmo\b", r"service management and orchestration"],
    "Non-RT RIC": [r"\bnon-rt ric\b", r"non-real-time ran intelligent controller"],
    "Near-RT RIC": [r"\bnear-rt ric\b", r"near-real-time ran intelligent controller"],
    "O-CU": [r"\bo-cu\b", r"o-ran central unit", r"o-ran centralized unit"],
    "O-CU-CP": [r"\bo-cu-cp\b"],
    "O-CU-UP": [r"\bo-cu-up\b"],
    "O-DU": [r"\bo-du\b", r"o-ran distributed unit"],
    "O-RU": [r"\bo-ru\b", r"o-ran radio unit"],
    "O-Cloud": [r"\bo-cloud\b"],
    "xApp": [r"\bxapp\b", r"\bxapps\b", r"near-rt ric applications?"],
    "rApp": [r"\brapp\b", r"\brapps\b", r"non-rt ric applications?"],
    "A1": [r"\ba1\b", r"\ba1 interface\b"],
    "E2": [r"\be2\b", r"\be2 interface\b"],
    "O1": [r"\bo1\b", r"\bo1 interface\b"],
    "O2": [r"\bo2\b", r"\bo2 interface\b"],
    "Y1": [r"\by1\b", r"\by1 interface\b"],
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

def extract_docx(path):
    doc = Document(path)
    text = []
    for para in doc.paragraphs:
        line = para.text.strip()
        if line:
            text.append(line)
    return text

def extract_pdf(path):
    doc = fitz.open(path)
    text = []
    for page in doc:
        content = page.get_text()
        for line in content.split("\n"):
            line = line.strip()
            if line:
                text.append(line)
    return text

def is_noise(line):
    lower = line.lower().strip()
    if len(lower) < 3:
        return True
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False

def clean_lines(lines):
    cleaned = []
    for line in lines:
        line = re.sub(r"\s+", " ", line).strip()
        if not is_noise(line):
            cleaned.append(line)
    return cleaned

def extract_entities_with_context(lines):
    found = defaultdict(list)

    for line in lines:
        lower = line.lower()
        for entity, patterns in ENTITY_KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, lower):
                    if line not in found[entity]:
                        found[entity].append(line)
                    break

    return found

for file in os.listdir(FOLDER):
    path = os.path.join(FOLDER, file)

    if not (file.endswith(".docx") or file.endswith(".pdf")):
        continue

    print(f"\n========== {file} ==========\n")

    if file.endswith(".docx"):
        lines = extract_docx(path)
    else:
        lines = extract_pdf(path)

    lines = clean_lines(lines)
    entities = extract_entities_with_context(lines)

    if not entities:
        print("No key O-RAN entities found.")
        continue

    for entity, matches in entities.items():
        print(f"\n--- {entity} ---")
        for line in matches[:5]:
            print(f"- {line}")