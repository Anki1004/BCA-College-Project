"""
utils.py — AI Academic Platform
=================================
Pure-Python utilities that do NOT call any AI API.
All functions in this file work offline.

Sections
  1. Text helpers         (extract_code_block, detect_language, chunk_text)
  2. PDF helpers          (extract_pdf_text, find_relevant_pdf_content)
  3. Session analytics    (track_feature_usage, get_most_used_features, session_duration_text)
  4. Study tracking       (update_study_tracking, extract_topics, unique_topics)
  5. User profile         (detect_user_info, get_user_profile_summary)
  6. Code execution       (execute_python_code)
  7. Study planner        (build_study_plan)
  8. Study recommender    (get_basic_recommendations)
  9. Mode / system prompts (MODE_PROMPTS, build_system_prompt, build_user_prompt)
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import os
from datetime import datetime, date, timedelta
from io import BytesIO

import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
#  1. Text helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_code_block(text: str) -> tuple[str | None, str | None]:
    """Return (language, code) from the first fenced code block, or (None, None)."""
    match = re.search(r"```(\w+)?\n([\s\S]*?)```", text)
    if match:
        lang = match.group(1).strip() if match.group(1) else None
        return lang, match.group(2).strip()
    if "\n" in text and any(sym in text for sym in ["def ", "class ", "{", "}", ";", "import ", "#include"]):
        return None, text.strip()
    return None, None


def detect_language(code: str, hinted: str | None = None) -> str:
    """Guess the programming language of a code snippet."""
    if hinted:
        return hinted.lower()
    checks = {
        "python":     [r"\bdef\b", r"\bimport\b", r"print\("],
        "java":       [r"\bpublic class\b", r"System\.out\.println", r"\bstatic void main\b"],
        "cpp":        [r"#include\s*<", r"std::", r"int\s+main\s*\("],
        "c":          [r"#include\s*<stdio\.h>", r"printf\("],
        "javascript": [r"\bfunction\b", r"console\.log\(", r"=>"],
        "sql":        [r"\bSELECT\b", r"\bINSERT\b", r"\bFROM\b"],
    }
    for lang, patterns in checks.items():
        if any(re.search(p, code, flags=re.IGNORECASE) for p in patterns):
            return lang
    return "text"


def chunk_text(text: str, max_size: int = 8000) -> list[str]:
    """Split text into chunks of at most *max_size* characters on paragraph boundaries."""
    if len(text) <= max_size:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in text.split("\n\n"):
        if current_len + len(para) > max_size and current:
            chunks.append("\n\n".join(current))
            current, current_len = [para], len(para)
        else:
            current.append(para)
            current_len += len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


# ─────────────────────────────────────────────────────────────────────────────
#  2. PDF helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_pdf_text(uploaded_file) -> tuple[str | None, str | None]:
    """
    Extract all text from a Streamlit UploadedFile (PDF).
    Returns (text, None) on success or (None, error_message) on failure.
    """
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None, "pypdf not installed. Run: pip install pypdf"

    try:
        reader = PdfReader(BytesIO(uploaded_file.read()))
        pages  = []
        for num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"[Page {num}]\n{page_text}")
        full_text = "\n\n".join(pages)
        if not full_text.strip():
            return None, "No extractable text found in this PDF."
        return full_text, None
    except Exception as exc:
        return None, f"Error reading PDF: {exc}"


def find_relevant_pdf_content(pdf_text: str, query: str, max_length: int = 6000) -> str:
    """
    Score chunks of *pdf_text* against *query* and return the most relevant passage.
    Falls back to the beginning of the document.
    """
    query_words = {w for w in query.lower().split() if len(w) > 3}
    chunks = chunk_text(pdf_text, max_size=2000)
    if len(chunks) <= 1:
        return pdf_text[:max_length]

    scored = []
    for chunk in chunks:
        lower  = chunk.lower()
        score  = sum(1 for w in query_words if w in lower)
        scored.append((score, chunk))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = [c for s, c in scored[:3] if s > 0] or [chunks[0]]
    return "\n\n".join(top)[:max_length]


# ─────────────────────────────────────────────────────────────────────────────
#  3. Session analytics
# ─────────────────────────────────────────────────────────────────────────────

_FEATURE_MAP: dict[str, str] = {
    "ai_chat":      "AI Chat",
    "pdf":          "PDF Study Chat",
    "quiz":         "Quiz Generator",
    "code":         "Code Helper",
    "notes":        "Notes Summarizer",
    "assignment":   "Assignment Generator",
    "checker":      "Assignment Checker",
    "planner":      "Study Planner",
    "exam":         "Exam Paper Generator",
    "runner":       "Code Runner",
    "recommender":  "Study Recommender",
}


def track_feature_usage(key: str) -> None:
    """Increment the usage counter for *key* (e.g. 'pdf', 'quiz')."""
    mapped = _FEATURE_MAP.get(key.lower())
    if mapped and mapped in st.session_state.get("feature_usage", {}):
        st.session_state.feature_usage[mapped] += 1


def get_most_used_features() -> list[tuple[str, int]]:
    """Return feature usage sorted descending."""
    return sorted(
        st.session_state.get("feature_usage", {}).items(),
        key=lambda x: x[1],
        reverse=True,
    )


def session_duration_text() -> str:
    """Return a human-readable duration since session start."""
    start: datetime = st.session_state.get("session_start_dt", datetime.now())
    delta = datetime.now() - start
    total_minutes = int(delta.total_seconds() / 60)
    hours, mins   = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {mins}m"
    return f"{mins}m"


# ─────────────────────────────────────────────────────────────────────────────
#  4. Study tracking
# ─────────────────────────────────────────────────────────────────────────────

_CS_TOPICS = [
    "python", "java", "c++", "javascript", "sql", "html", "css",
    "dbms", "database", "os", "operating system", "networking", "networks",
    "data structures", "algorithms", "dsa", "oops", "object oriented",
    "ai", "machine learning", "cloud", "web development", "software engineering",
    "mathematics", "statistics", "calculus", "linear algebra",
]


def extract_topics(text: str) -> list[str]:
    """Return CS topics mentioned in *text*."""
    lower = text.lower()
    return [t.title() for t in _CS_TOPICS if t in lower]


def unique_topics(topics: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for t in topics:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result


def update_study_tracking(user_text: str) -> None:
    """Update session-level topic list and question counter from user input."""
    st.session_state["questions_asked"] = st.session_state.get("questions_asked", 0) + 1
    new_topics = extract_topics(user_text)
    existing   = st.session_state.get("topics_studied", [])
    st.session_state["topics_studied"] = unique_topics(existing + new_topics)[:50]


# ─────────────────────────────────────────────────────────────────────────────
#  5. User profile
# ─────────────────────────────────────────────────────────────────────────────

def detect_user_info(text: str) -> None:
    """Detect and persist the user's name from phrases like 'my name is …'."""
    match = re.search(r"my name is ([a-zA-Z]+)", text, re.IGNORECASE)
    if match:
        st.session_state["user_name"] = match.group(1).capitalize()


def get_user_profile_summary() -> str:
    """Return a Markdown snippet summarising the user profile."""
    parts: list[str] = []
    if st.session_state.get("user_name"):
        parts.append(f"👤 **{st.session_state['user_name']}**")
    q = st.session_state.get("questions_asked", 0)
    t = len(st.session_state.get("topics_studied", []))
    parts.append(f"❓ Questions asked: **{q}**")
    parts.append(f"📚 Topics explored: **{t}**")
    return "\n\n".join(parts) if parts else "No profile data yet."


# ─────────────────────────────────────────────────────────────────────────────
#  6. Safe Python code runner
# ─────────────────────────────────────────────────────────────────────────────

_BLOCKED_PATTERNS = [
    "import os", "import sys", "import subprocess", "import shutil",
    "import socket", "__import__", "open(", "eval(", "exec(", "compile(",
    "os.system", "os.popen", "os.remove", "os.rmdir",
]


def execute_python_code(code: str, timeout: int = 10) -> tuple[str, str]:
    """
    Execute *code* safely in a subprocess sandbox.
    Returns (stdout, stderr). Blocks dangerous imports/functions.
    """
    for blocked in _BLOCKED_PATTERNS:
        if blocked in code:
            return "", f"⛔ Blocked: '{blocked}' is not allowed for security reasons."

    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir="/tmp"
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout[:4000], result.stderr[:2000]
    except subprocess.TimeoutExpired:
        return "", f"⏱️ Code timed out after {timeout} seconds."
    except Exception as exc:
        return "", str(exc)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ─────────────────────────────────────────────────────────────────────────────
#  7. Study planner (pure Python, no AI)
# ─────────────────────────────────────────────────────────────────────────────

def build_study_plan(
    subjects:    list[str],
    exam_date:   date,
    hours_day:   float,
) -> list[dict]:
    """
    Build a day-by-day study plan from today to *exam_date*.
    Returns a list of {date, subject, hours, note} dicts.
    """
    today     = date.today()
    days_left = (exam_date - today).days
    if days_left <= 0 or not subjects:
        return []

    plan: list[dict] = []
    day = today
    idx = 0
    while day < exam_date:
        is_revision = (exam_date - day).days <= 3
        subject     = "All Subjects — Revision" if is_revision else subjects[idx % len(subjects)]
        note        = "Final revision: past papers + formula sheets" if is_revision else "Study + practice problems"
        plan.append({
            "date":    day.strftime("%a, %d %b %Y"),
            "subject": subject,
            "hours":   hours_day if not is_revision else min(hours_day + 1, 8),
            "note":    note,
        })
        if not is_revision:
            idx += 1
        day += timedelta(days=1)
    return plan


# ─────────────────────────────────────────────────────────────────────────────
#  8. Study recommender (rule-based, no AI)
# ─────────────────────────────────────────────────────────────────────────────

_RESOURCES: dict[str, list[str]] = {
    "python":           ["docs.python.org", "realpython.com", "Python Crash Course (book)"],
    "java":             ["docs.oracle.com/javase", "Head First Java (book)"],
    "data structures":  ["visualgo.net", "Introduction to Algorithms — CLRS (book)"],
    "dbms":             ["sqlzoo.net", "Database System Concepts — Silberschatz (book)"],
    "operating system": ["studytonight.com/os", "Modern Operating Systems — Tanenbaum (book)"],
    "networking":       ["cisco.com/c/en/us/training", "Computer Networking — Kurose & Ross (book)"],
    "mathematics":      ["khanacademy.org", "brilliant.org"],
}


def get_basic_recommendations() -> str:
    """Return a Markdown-formatted recommendation block based on topics studied."""
    topics = [t.lower() for t in st.session_state.get("topics_studied", [])]
    lines  = ["### 📚 Recommended Resources\n"]
    matched = False
    for topic, resources in _RESOURCES.items():
        if any(topic in t or t in topic for t in topics):
            lines.append(f"**{topic.title()}**")
            for r in resources:
                lines.append(f"  • {r}")
            matched = True
    if not matched:
        lines.append(
            "Start learning a topic and I'll personalise recommendations!\n\n"
            "Popular starting points: Python · DBMS · Data Structures · OS · Networks"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
#  9. Mode prompts & prompt builders
# ─────────────────────────────────────────────────────────────────────────────

MODE_PROMPTS: dict[str, str] = {
    "General Study Assistant": (
        "You are a helpful AI Study Assistant for college students. "
        "Answer clearly and concisely with relevant examples. "
        "Use structured formatting when helpful."
    ),
    "Programming Helper": (
        "You are an expert programming tutor for CS students. "
        "Explain concepts with code examples and step-by-step breakdowns. "
        "Mention real-world applications. Always format code in fenced blocks."
    ),
    "Code Debugger": (
        "You are a professional code debugging assistant. "
        "Identify errors systematically, explain WHY the error occurs, "
        "provide corrected code with improvements, and mention best practices."
    ),
    "Quiz Generator": (
        "You are an academic quiz creator for university exams. "
        "Generate exactly 5 MCQs with 4 options each. "
        "Mark the correct answer clearly. Include brief explanations."
    ),
    "Notes Summarizer": (
        "You are an exam preparation specialist. "
        "Convert lengthy notes into structured bullet points. "
        "Highlight key definitions, formulas, and important concepts. "
        "Format for easy revision scanning."
    ),
    "Assignment Writer": (
        "You are an academic assignment assistant. "
        "Structure content with: Title, Introduction, Body (with headings), Conclusion, References. "
        "Use formal academic language. Target the requested word count."
    ),
    "Study Planner": (
        "You are a study planning expert. "
        "Create realistic day-by-day study schedules. "
        "Balance topics, include revision slots, and add motivational tips."
    ),
    "Exam Prep": (
        "You are an examination paper specialist. "
        "Generate realistic exam papers with MCQ, short answer, and long answer sections. "
        "Match university exam patterns with proper marks distribution."
    ),
}

BASE_CONTEXT = (
    "You are an AI Study Assistant for college students (BCA, BTech, BBA, BSc, BCom, MBA). "
    "Help with programming, CS theory, mathematics, business subjects, and exam preparation. "
    "Be educational, student-friendly, and precise."
)


def build_system_prompt(mode: str) -> str:
    """Combine BASE_CONTEXT with the mode-specific prompt."""
    mode_text = MODE_PROMPTS.get(mode, MODE_PROMPTS["General Study Assistant"])
    return f"{BASE_CONTEXT}\n\n{mode_text}"


def build_user_prompt(user_input: str, mode: str) -> str:
    """Optionally wrap the user input with mode-specific instructions."""
    wrappers = {
        "Quiz Generator":   f"Generate 5 MCQs on the following topic:\n\n{user_input}",
        "Notes Summarizer": f"Summarise the following notes:\n\n{user_input}",
        "Assignment Writer": f"Write a well-structured academic assignment on:\n\n{user_input}",
        "Code Debugger":    f"Debug and explain the following code:\n\n{user_input}",
    }
    return wrappers.get(mode, user_input)
