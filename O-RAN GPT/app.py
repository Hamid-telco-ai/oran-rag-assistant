from __future__ import annotations

import os
import re
import streamlit as st
from openai import OpenAI

from knowledge_engine import build_knowledge_context, get_known_unknown, relationship_answer
from query_engine import (
    build_context,
    build_source_list,
    answer_without_llm,
    retrieve_relevant_chunks,
)

st.set_page_config(page_title="O-RAN GPT", layout="wide")

st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(120,160,255,0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(100,200,255,0.10), transparent 30%),
            radial-gradient(circle at bottom left, rgba(180,220,255,0.14), transparent 30%),
            linear-gradient(180deg, #f8fbff 0%, #edf3fb 100%);
    }

    .main {
        padding-top: 1.0rem;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    /* Typography */
    h1 {
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        color: #16255c !important;
        margin-bottom: 0.15rem !important;
        letter-spacing: -0.02em;
    }

    h2 {
        font-size: 1.9rem !important;
        font-weight: 700 !important;
        color: #18285f !important;
        margin-top: 1.1rem !important;
    }

    h3 {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #24366f !important;
    }

    p, li, div, label {
        font-size: 1.03rem !important;
        line-height: 1.75 !important;
        color: #2f3b58 !important;
    }

    .app-caption {
        font-size: 1.08rem;
        color: #61708f !important;
        margin-bottom: 1.2rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(244,248,255,0.86));
        border-right: 1px solid rgba(130, 150, 190, 0.20);
        backdrop-filter: blur(12px);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Chat messages */
    .stChatMessage {
        padding: 0.65rem 0 1rem 0;
        background: transparent !important;
    }

    /* Assistant answer card */
    .answer-card {
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(180,190,220,0.32);
        border-radius: 24px;
        padding: 24px 28px;
        box-shadow: 0 10px 30px rgba(31, 55, 110, 0.08);
        backdrop-filter: blur(10px);
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }

    /* User bubble */
    .user-question {
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(180,190,220,0.28);
        border-radius: 16px;
        padding: 12px 16px;
        box-shadow: 0 8px 20px rgba(31,55,110,0.05);
        margin-bottom: 0.75rem;
    }

    /* Source cards */
    .source-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 12px;
        margin-top: 0.6rem;
    }

    .source-card {
        border: 1px solid rgba(180,190,220,0.30);
        border-radius: 18px;
        padding: 14px 16px;
        background: rgba(255,255,255,0.74);
        box-shadow: 0 8px 20px rgba(31,55,110,0.05);
        backdrop-filter: blur(8px);
    }

    .source-title {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 4px;
        color: #1d2d62 !important;
    }

    .source-meta {
        font-size: 0.94rem;
        color: #6b7896 !important;
    }

    /* Confidence badge */
    .confidence-high,
    .confidence-medium,
    .confidence-low {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.92rem;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    .confidence-high {
        background: rgba(57, 181, 74, 0.12);
        border: 1px solid rgba(57, 181, 74, 0.35);
        color: #1f6d2a !important;
    }

    .confidence-medium {
        background: rgba(230, 170, 45, 0.14);
        border: 1px solid rgba(230, 170, 45, 0.35);
        color: #875b00 !important;
    }

    .confidence-low {
        background: rgba(220, 70, 70, 0.12);
        border: 1px solid rgba(220, 70, 70, 0.35);
        color: #9e1f1f !important;
    }

    /* Inputs */
    .stChatInput {
        background: rgba(255,255,255,0.75);
        border-radius: 20px;
    }

    .stChatInput input, .stTextInput input {
        font-size: 1rem !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(150,170,210,0.35);
        background: rgba(255,255,255,0.72);
        color: #23356d;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(31,55,110,0.05);
    }

    .stButton > button:hover {
        border-color: rgba(90,120,200,0.45);
        color: #16255c;
    }

    /* Caption */
    .stCaption {
        color: #71809f !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("O-RAN GPT")
st.markdown(
    '<div class="app-caption">Ask Your Question with O-RAN Assistance.</div>',
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "OpenAI Bot"


with st.sidebar:
    st.header("Settings")
    mode = st.radio(
        "Mode",
        ["OpenAI Bot", "Knowledge Retrieval Only", "LLM Ready Context View"],
        index=["OpenAI Bot", "Knowledge Retrieval Only", "LLM Ready Context View"].index(
            st.session_state.mode
        ),
    )
    st.session_state.mode = mode

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


def extract_used_source_numbers(answer: str) -> list[int]:
    found = re.findall(r"\[(\d+)\]", answer)
    return sorted({int(x) for x in found})


def extract_retrieval_confidence(context: str) -> str:
    m = re.search(r"## Retrieval Confidence\s+([a-zA-Z]+)", context)
    if m:
        return m.group(1).strip().lower()
    return "unknown"


def map_sources_for_display(question: str, answer: str, top_k: int = 5) -> list[dict]:
    raw_sources = build_source_list(question, top_k=top_k)
    used_numbers = extract_used_source_numbers(answer)

    parsed = []
    for item in raw_sources:
        m = re.match(r"\[(\d+)\]\s+(.*?)\s+→\s+(.*)", item)
        if m:
            parsed.append(
                {
                    "num": int(m.group(1)),
                    "file": m.group(2),
                    "section": m.group(3),
                }
            )

    if used_numbers:
        parsed = [p for p in parsed if p["num"] in used_numbers]

    return parsed


def build_system_prompt(confidence: str) -> str:
    base = """
You are an O-RAN expert assistant.

Core rules:
- Answer only from the provided local knowledge base and skill rules.
- Do not use outside knowledge.
- If the answer is not supported by the provided context, say exactly:
  "Not defined in current knowledge base."
- Be precise, structured, and technical.
- Use markdown.
- Use inline citations like [1], [2], [3] only when directly supported by the provided context.
- Do not include a separate heading called "Sources".
- Do not cite a source unless it directly supports the sentence or claim.
- Prefer fewer, more precise citations over many loose citations.
- Keep the answer readable and professional.
"""

    if confidence == "high":
        extra = """
Retrieval confidence is high.
- Answer normally from the provided context.
- Cite only directly supporting sources.
"""
    elif confidence == "medium":
        extra = """
Retrieval confidence is medium.
- Answer conservatively.
- Avoid overgeneralizing.
- If a detail is not clearly supported, omit it or say it is not defined in current knowledge base.
- Cite only directly supporting sources.
"""
    else:
        extra = """
Retrieval confidence is low.
- Be very strict.
- If the context does not clearly support the answer, say exactly:
  "Not defined in current knowledge base."
- Do not infer missing details.
- Do not expand beyond explicit context.
- Cite only directly supporting sources.
"""

    citation_examples = """
Citation examples:
- Good: "A1 connects Non-RT RIC and Near-RT RIC [1]."
- Bad: "A1 connects Non-RT RIC and Near-RT RIC [1][2][3]" unless each source directly supports that exact claim.
"""

    return base + "\n" + extra + "\n" + citation_examples


def answer_with_openai(question: str) -> tuple[str, str, str, list[dict]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY is not set.", "unknown", "none", []

    # 1) Rule-based deterministic relationship answers first
    rel_answer = relationship_answer(question)
    if rel_answer:
        answer = rel_answer["answer"]
        confidence = rel_answer["confidence"]
        source_type = rel_answer["source_type"]
        references = rel_answer["references"]
        return answer, confidence, source_type, references

    # 2) Structured knowledge layer
    client = OpenAI(api_key=api_key)

    knowledge_context, knowledge_confidence = build_knowledge_context(question)

    # 3) Markdown fallback
    markdown_context = build_context(question, top_k=5)
    markdown_confidence = extract_retrieval_confidence(markdown_context)

    if knowledge_context:
        context = (
            f"## Structured Knowledge Layer\n{knowledge_context}\n\n"
            f"## Markdown Knowledge Layer\n{markdown_context}"
        )
        confidence = knowledge_confidence
        source_type = "structured knowledge + markdown"
    else:
        context = markdown_context
        confidence = markdown_confidence
        source_type = "markdown"

    system_prompt = build_system_prompt(confidence)

    response = client.responses.create(
        model="gpt-5.4",
        instructions=system_prompt,
        input=f"Question:\n{question}\n\nContext:\n{context}",
    )

    return response.output_text, confidence, source_type, []


def render_source_cards(source_items: list[dict]):
    if not source_items:
        return

    st.markdown("### References")

    cards_html = '<div class="source-grid">'
    for item in source_items:
        cards_html += f"""
        <div class="source-card">
            <div class="source-title">[{item['num']}] {item['file']}</div>
            <div class="source-meta">Section: {item['section']}</div>
        </div>
        """
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)


def render_matched_sections(question: str, top_k: int = 5):
    chunks = retrieve_relevant_chunks(question, top_k=top_k)
    if not chunks:
        return

    with st.expander("Matched Sections"):
        for i, chunk in enumerate(chunks, start=1):
            st.markdown(f"**[{i}] {chunk.source} → {chunk.heading}**")
            st.markdown(chunk.text)
            st.markdown("---")


def render_confidence_badge(confidence: str):
    cls = {
        "high": "confidence-high",
        "medium": "confidence-medium",
        "low": "confidence-low",
    }.get(confidence, "confidence-medium")

    st.markdown(
        f'<div class="{cls}">Retrieval confidence: {confidence.upper()}</div>',
        unsafe_allow_html=True,
    )


def extract_unknown_term(question: str) -> str | None:
    known_unknown = get_known_unknown(question)
    if known_unknown:
        return known_unknown["term"]

    q = question.lower()
    for t in ["f1", "e1", "x2", "xn", "ng"]:
        if re.search(rf"\b{re.escape(t)}\b", q):
            return t.upper()
    return None


def render_unknown_case(question: str):
    st.markdown("### Not found in knowledge base")

    term = extract_unknown_term(question)
    if term:
        st.markdown(f"**{term} interface** is not defined in the current knowledge base.")
    else:
        st.markdown("This concept is not defined in the current knowledge base.")

    st.markdown("### Related O-RAN concepts")

    related_chunks = retrieve_relevant_chunks(question, top_k=3)
    if not related_chunks:
        st.markdown("- No related concepts found.")
        return

    for chunk in related_chunks:
        st.markdown(f"**{chunk.heading}**")
        first_meaningful_line = ""
        for line in chunk.text.splitlines():
            line = line.strip()
            if line and not line.lower().startswith("- evidence"):
                first_meaningful_line = line
                break
        if first_meaningful_line:
            st.markdown(f"- {first_meaningful_line}")

    with st.expander("Matched Sections"):
        for i, chunk in enumerate(related_chunks, start=1):
            st.markdown(f"**[{i}] {chunk.source} → {chunk.heading}**")
            st.markdown(chunk.text)
            st.markdown("---")


def structured_refs_to_source_cards(structured_refs: list[dict]) -> list[dict]:
    source_cards = []
    for i, rel in enumerate(structured_refs, start=1):
        ev = rel.get("evidence", [{}])[0]
        source_cards.append(
            {
                "num": i,
                "file": ev.get("file", "relationships.json"),
                "section": ev.get("section", rel.get("relation", "relationship")),
            }
        )
    return source_cards


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-question">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
            continue

        if msg.get("confidence"):
            render_confidence_badge(msg["confidence"])

        if msg.get("unknown") and msg.get("question"):
            if msg.get("source_type"):
                st.caption(f"Answer source: {msg['source_type']}")
            render_unknown_case(msg["question"])
        else:
            if msg.get("source_type"):
                st.caption(f"Answer source: {msg['source_type']}")
            st.markdown('<div class="answer-card">', unsafe_allow_html=True)
            st.markdown(msg["content"])
            st.markdown('</div>', unsafe_allow_html=True)
            if msg.get("source_cards"):
                render_source_cards(msg["source_cards"])
            if msg.get("show_matches") and msg.get("question"):
                render_matched_sections(msg["question"])


question = st.chat_input("Ask an O-RAN question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(f'<div class="user-question">{question}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        if st.session_state.mode == "Knowledge Retrieval Only":
            answer = answer_without_llm(question)
            st.markdown('<div class="answer-card">', unsafe_allow_html=True)
            st.markdown(answer)
            st.markdown('</div>', unsafe_allow_html=True)
            render_matched_sections(question)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "question": question,
                    "show_matches": True,
                }
            )

        elif st.session_state.mode == "LLM Ready Context View":
            context = build_context(question, top_k=5)
            st.code(context)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Displayed prompt context.",
                    "question": question,
                    "show_matches": True,
                }
            )

        else:
            with st.spinner("Thinking..."):
                answer, confidence, source_type, structured_refs = answer_with_openai(question)

            is_unknown = (
                confidence == "low"
                and "not defined in current knowledge base" in answer.lower()
            )

            render_confidence_badge(confidence)
            st.caption(f"Answer source: {source_type}")

            if is_unknown:
                render_unknown_case(question)

                term = extract_unknown_term(question)
                unknown_text = (
                    f"{term} interface is not defined in the current knowledge base."
                    if term
                    else "This concept is not defined in the current knowledge base."
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": unknown_text,
                        "question": question,
                        "show_matches": False,
                        "confidence": confidence,
                        "unknown": True,
                        "source_type": source_type,
                    }
                )

            else:
                st.markdown('<div class="answer-card">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown('</div>', unsafe_allow_html=True)

                if structured_refs:
                    source_cards = structured_refs_to_source_cards(structured_refs)
                else:
                    source_cards = map_sources_for_display(question, answer, top_k=5)

                render_source_cards(source_cards)
                render_matched_sections(question)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "source_cards": source_cards,
                        "question": question,
                        "show_matches": True,
                        "confidence": confidence,
                        "source_type": source_type,
                    }
                )
