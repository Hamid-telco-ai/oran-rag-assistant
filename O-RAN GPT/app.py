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
    .main {
        padding-top: 1.2rem;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: 2.3rem !important;
        margin-bottom: 0.2rem !important;
    }

    h2 {
        font-size: 1.8rem !important;
        margin-top: 1.2rem !important;
    }

    h3 {
        font-size: 1.35rem !important;
        margin-top: 1rem !important;
    }

    p, li, div, label {
        font-size: 1.05rem !important;
        line-height: 1.65 !important;
    }

    .stChatMessage {
        padding: 0.8rem 0.2rem 1.2rem 0.2rem;
    }

    .source-card {
        border: 1px solid rgba(120,120,120,0.25);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        background-color: rgba(250,250,250,0.02);
    }

    .source-title {
        font-weight: 700;
        font-size: 1.02rem;
        margin-bottom: 6px;
    }

    .source-meta {
        font-size: 0.95rem;
        opacity: 0.85;
        margin-bottom: 6px;
    }

    .app-caption {
        font-size: 1.08rem;
        opacity: 0.8;
        margin-bottom: 1rem;
    }

    .stTextInput input, .stChatInput input {
        font-size: 1.02rem !important;
    }

    code {
        font-size: 0.95rem !important;
    }

    .confidence-high {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.9rem;
        background: rgba(0, 180, 90, 0.14);
        border: 1px solid rgba(0, 180, 90, 0.35);
        margin-bottom: 12px;
    }

    .confidence-medium {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.9rem;
        background: rgba(220, 160, 0, 0.14);
        border: 1px solid rgba(220, 160, 0, 0.35);
        margin-bottom: 12px;
    }

    .confidence-low {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.9rem;
        background: rgba(220, 40, 40, 0.14);
        border: 1px solid rgba(220, 40, 40, 0.35);
        margin-bottom: 12px;
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
    for item in source_items:
        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-title">[{item['num']}] {item['file']}</div>
                <div class="source-meta">Section: {item['section']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


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
        if msg.get("confidence"):
            render_confidence_badge(msg["confidence"])

        if msg.get("unknown") and msg.get("question"):
            if msg.get("source_type"):
                st.caption(f"Answer source: {msg['source_type']}")
            render_unknown_case(msg["question"])
        else:
            if msg.get("source_type"):
                st.caption(f"Answer source: {msg['source_type']}")
            st.markdown(msg["content"])
            if msg.get("source_cards"):
                render_source_cards(msg["source_cards"])
            if msg.get("show_matches") and msg.get("question"):
                render_matched_sections(msg["question"])


question = st.chat_input("Ask an O-RAN question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        if st.session_state.mode == "Knowledge Retrieval Only":
            answer = answer_without_llm(question)
            st.markdown(answer)
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
                st.markdown(answer)

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