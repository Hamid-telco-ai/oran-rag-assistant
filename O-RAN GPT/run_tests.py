from pathlib import Path

QUESTIONS_FILE = Path("tests/test_questions.md")
RESULTS_FILE = Path("tests/test_results.md")

def load_questions(path: Path) -> list[str]:
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- "):
            questions.append(line[2:].strip())
    return questions

def main():
    questions = load_questions(QUESTIONS_FILE)

    lines = ["# O-RAN GPT Test Results", ""]
    for i, q in enumerate(questions, start=1):
        lines.append(f"## Test {i}")
        lines.append(f"**Question:** {q}")
        lines.append("")
        lines.append("**Status:** Not tested yet")
        lines.append("")
        lines.append("**Notes:**")
        lines.append("- ")
        lines.append("")
        lines.append("---")
        lines.append("")

    RESULTS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {RESULTS_FILE}")

if __name__ == "__main__":
    main()