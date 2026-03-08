"""
app.py — AI Academic Platform
================================
Main Streamlit application.

Architecture
  app.py          → UI pages, routing, session state
  ai_engine.py    → Gemini (key rotation) → Claude fallback
  utils.py        → All offline Python utilities

Sidebar order (fixed, 13 tools)
  1  Home                 8  Code Runner
  2  PDF Study Chat       9  Study Recommender
  3  Notes Summarizer    10  Dashboard
  4  Assignment Generator 11  AI Chat
  5  Assignment Checker  12  Quiz Generator
  6  Study Planner       13  Code Helper
  7  Exam Paper Generator
"""

from __future__ import annotations

import re
from datetime import datetime, date

import streamlit as st

from ai_engine import get_response, ai_available
from utils import (
    MODE_PROMPTS,
    build_system_prompt,
    build_user_prompt,
    extract_pdf_text,
    find_relevant_pdf_content,
    execute_python_code,
    track_feature_usage,
    get_most_used_features,
    session_duration_text,
    update_study_tracking,
    detect_user_info,
    get_user_profile_summary,
    get_basic_recommendations,
    build_study_plan,
)


# ─────────────────────────────────────────────────────────────────────────────
#  Page config (must be FIRST Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Academic Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
[data-testid="stAppViewContainer"] {
    background: #060b18;
    color: #e2e8f0;
    font-family: 'Space Grotesk', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0d1526;
    border-right: 1px solid #1e2d4a;
}

/* ── Cards ── */
.card {
    background: #111c33;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.card-green  { border-left: 4px solid #10b981; }
.card-blue   { border-left: 4px solid #38bdf8; }
.card-purple { border-left: 4px solid #818cf8; }
.card-amber  { border-left: 4px solid #f59e0b; }
.card-red    { border-left: 4px solid #f87171; }



/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0d1526 0%, #111c33 100%);
    border: 1px solid #1e2d4a;
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
}
.hero h1 {
    font-size: 2.2rem;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.hero p { color: #64748b; font-size: 1rem; }

/* ── Tool grid card ── */
.tool-card {
    background: #111c33;
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.7rem;
    transition: border-color 0.2s;
}
.tool-card:hover { border-color: #38bdf8; }
.tool-card .icon { font-size: 1.5rem; margin-bottom: 4px; }
.tool-card .name { font-weight: 600; color: #e2e8f0; font-size: 0.95rem; }
.tool-card .desc { color: #64748b; font-size: 0.8rem; }

/* ── Metric ── */
.kpi {
    background: #111c33;
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    text-align: center;
}
.kpi h3 { font-size: 1.8rem; color: #38bdf8; margin: 0; }
.kpi p  { font-size: 0.75rem; color: #64748b; margin: 0; }

/* ── Inputs ── */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #111c33 !important;
    border: 1px solid #1e2d4a !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #6366f1) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
code, pre {
    font-family: 'JetBrains Mono', monospace !important;
    background: #060b18 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Navigation constants (FIXED ORDER — do not change)
# ─────────────────────────────────────────────────────────────────────────────

NAV_ITEMS: list[str] = [
    "🏠 Home",
    "📄 PDF Study Chat",
    "📝 Notes Summarizer",
    "✍️ Assignment Generator",
    "✓ Assignment Checker",
    "📅 Study Planner",
    "🧾 Exam Paper Generator",
    "💻 Code Runner",
    "🎓 Study Recommender",
    "📊 Dashboard",
    "💬 AI Chat",
    "🧩 Quiz Generator",
    "🐛 Code Helper",
]

# Map nav → study mode (for auto-switching the mode selector)
NAV_TO_MODE: dict[str, str] = {
    "🏠 Home":                "General Study Assistant",
    "📄 PDF Study Chat":      "General Study Assistant",
    "📝 Notes Summarizer":    "Notes Summarizer",
    "✍️ Assignment Generator": "Assignment Writer",
    "✓ Assignment Checker":   "General Study Assistant",
    "📅 Study Planner":       "Study Planner",
    "🧾 Exam Paper Generator": "Exam Prep",
    "💻 Code Runner":          "Programming Helper",
    "🎓 Study Recommender":   "General Study Assistant",
    "📊 Dashboard":           "General Study Assistant",
    "💬 AI Chat":             "General Study Assistant",
    "🧩 Quiz Generator":      "Quiz Generator",
    "🐛 Code Helper":         "Code Debugger",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Session state initialisation
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULTS: dict = {
    # Navigation
    "nav":                "🏠 Home",
    "mode":               "General Study Assistant",
    # Chat
    "messages":           [],
    # Session stats
    "session_start_dt":   datetime.now(),
    "questions_asked":    0,
    "topics_studied":     [],
    # User profile
    "user_name":          None,
    # Feature analytics
    "feature_usage": {
        "AI Chat": 0, "PDF Study Chat": 0, "Quiz Generator": 0,
        "Code Helper": 0, "Notes Summarizer": 0, "Assignment Generator": 0,
        "Assignment Checker": 0, "Study Planner": 0, "Exam Paper Generator": 0,
        "Code Runner": 0, "Study Recommender": 0,
    },
    # PDF
    "pdf_content":        None,
    "pdf_filename":       None,
    "pdf_chat_history":   [],
    # Code runner
    "code_output":        "",
    "code_error":         "",
    # AI key rotation
    "_gemini_key_index":  0,
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────────────────────────────────────
#  Shared helpers
# ─────────────────────────────────────────────────────────────────────────────

def _source_badge(source: str) -> str:
    return ""


def _ai(
    prompt:     str,
    mode:       str,
    fallback:   str | None = None,
    history:    list[dict] | None = None,
    pdf_ctx:    str | None = None,
) -> tuple[str, str]:
    """
    Build the full prompt and call ai_engine.get_response().
    Returns (answer_text, source).
    """
    system = build_system_prompt(mode)
    user   = build_user_prompt(prompt, mode)

    # Append conversation context
    if history:
        ctx_lines = [
            f"{'Student' if m['role'] == 'user' else 'AI'}: {m['content'][:200]}"
            for m in history[-6:]
        ]
        user = "Previous context:\n" + "\n".join(ctx_lines) + "\n\n" + user

    # Prepend PDF context
    if pdf_ctx:
        user = f"REFERENCE DOCUMENT:\n{pdf_ctx}\n\n{user}"

    return get_response(user, system, fallback)


def _render_response(prompt: str, mode: str, pdf_ctx: str | None = None) -> str:
    """Call AI and stream the result into a Streamlit chat message bubble."""
    resp, src = _ai(prompt, mode, history=st.session_state.messages, pdf_ctx=pdf_ctx)
    st.markdown(resp + _source_badge(src), unsafe_allow_html=True)
    return resp


def _add_message(role: str, content: str) -> None:
    st.session_state.messages.append({
        "role":      role,
        "content":   content,
        "timestamp": datetime.now().strftime("%H:%M"),
    })


def _hr() -> None:
    st.markdown("<hr style='border-color:#1e2d4a;margin:1rem 0'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:12px 0 18px">
      <div style="font-size:36px">🎓</div>
      <div style="font-size:1.05rem;font-weight:700;
           background:linear-gradient(135deg,#38bdf8,#818cf8);
           -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        AI Academic Platform
      </div>
      <div style="font-size:0.7rem;color:#475569;letter-spacing:2px;
           text-transform:uppercase;margin-top:2px">
        OpenRouter · Gemini · Claude · Always On
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation radio
    st.markdown("#### 📍 Navigation")
    nav_idx = NAV_ITEMS.index(st.session_state.nav) if st.session_state.nav in NAV_ITEMS else 0
    new_nav = st.radio(
        "nav_radio",
        options=NAV_ITEMS,
        index=nav_idx,
        label_visibility="collapsed",
    )
    if new_nav != st.session_state.nav:
        st.session_state.nav  = new_nav
        st.session_state.mode = NAV_TO_MODE.get(new_nav, "General Study Assistant")
        st.rerun()

    st.divider()

    # Study mode selector
    st.markdown("#### 🎯 Study Mode")
    mode_list = list(MODE_PROMPTS.keys())
    mode_idx  = mode_list.index(st.session_state.mode) if st.session_state.mode in mode_list else 0
    new_mode  = st.selectbox("mode_sel", mode_list, index=mode_idx, label_visibility="collapsed")
    st.session_state.mode = new_mode

    st.divider()

    # User profile
    with st.expander("👤 Profile"):
        name_val = st.text_input("Your name", value=st.session_state.user_name or "", key="sb_name")
        if name_val != (st.session_state.user_name or ""):
            st.session_state.user_name = name_val or None
        st.markdown(get_user_profile_summary())

    st.divider()

    # Session stats
    st.markdown("#### 📊 Session")
    c1, c2 = st.columns(2)
    c1.metric("Questions", st.session_state.questions_asked)
    c2.metric("Topics",    len(st.session_state.topics_studied))

    # AI status dot
    status_dot = "🟢" if ai_available() else "🔴"
    st.caption(f"{status_dot} AI: {'Online' if ai_available() else 'Keys missing'}")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  Pages
# ─────────────────────────────────────────────────────────────────────────────

page = st.session_state.nav

# ── 1. Home ──────────────────────────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div class="hero">
      <h1>🎓 AI Academic Platform</h1>
      <p>Your intelligent study companion — OpenRouter first, Gemini & Claude backed, always responsive.</p>
    </div>
    """, unsafe_allow_html=True)

    tools = [
        ("📄", "PDF Study Chat",       "Upload any PDF, ask questions about it",  "📄 PDF Study Chat"),
        ("📝", "Notes Summarizer",     "Paste notes → get a concise summary",     "📝 Notes Summarizer"),
        ("✍️", "Assignment Generator", "Topic → full structured assignment",      "✍️ Assignment Generator"),
        ("✓",  "Assignment Checker",   "Paste assignment → grammar + AI feedback","✓ Assignment Checker"),
        ("📅", "Study Planner",        "Subjects + exam date → day-by-day schedule","📅 Study Planner"),
        ("🧾", "Exam Paper Generator", "Subject → realistic exam paper",          "🧾 Exam Paper Generator"),
        ("💻", "Code Runner",          "Write & run Python in a safe sandbox",    "💻 Code Runner"),
        ("🎓", "Study Recommender",    "Personalised resources based on topics",  "🎓 Study Recommender"),
        ("📊", "Dashboard",            "Session analytics and usage stats",       "📊 Dashboard"),
        ("💬", "AI Chat",              "Ask anything — general AI assistant",     "💬 AI Chat"),
        ("🧩", "Quiz Generator",       "Topic → 5 MCQs with answers",            "🧩 Quiz Generator"),
        ("🐛", "Code Helper",          "Paste code → debug, explain, optimise",   "🐛 Code Helper"),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc, nav_key) in enumerate(tools):
        with cols[i % 3]:
            if st.button(f"{icon} {name}", key=f"home_{nav_key}", use_container_width=True, help=desc):
                st.session_state.nav  = nav_key
                st.session_state.mode = NAV_TO_MODE.get(nav_key, "General Study Assistant")
                st.rerun()


# ── 2. PDF Study Chat ─────────────────────────────────────────────────────────
elif page == "📄 PDF Study Chat":
    track_feature_usage("pdf")
    st.markdown("### 📄 PDF Study Chat")

    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded:
        if uploaded.name != st.session_state.pdf_filename:
            with st.spinner("📖 Reading PDF…"):
                text, err = extract_pdf_text(uploaded)
            if err:
                st.error(f"❌ {err}")
            else:
                st.session_state.pdf_content  = text
                st.session_state.pdf_filename = uploaded.name
                st.session_state.pdf_chat_history = []
                st.success(f"✅ Loaded: **{uploaded.name}**")

    if st.session_state.pdf_content:
        st.caption(f"📎 Active PDF: {st.session_state.pdf_filename}")

        for msg in st.session_state.pdf_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)

        question = st.chat_input("Ask a question about the PDF…")
        if question:
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.pdf_chat_history.append({"role": "user", "content": question})

            ctx = find_relevant_pdf_content(st.session_state.pdf_content, question)
            with st.chat_message("assistant"):
                answer = _render_response(question, "General Study Assistant", pdf_ctx=ctx)
            st.session_state.pdf_chat_history.append({"role": "assistant", "content": answer})
            update_study_tracking(question)

        if st.button("🗑️ Clear PDF"):
            st.session_state.pdf_content      = None
            st.session_state.pdf_filename     = None
            st.session_state.pdf_chat_history = []
            st.rerun()
    elif not uploaded:
        st.info("👆 Upload a PDF to get started.")


# ── 3. Notes Summarizer ──────────────────────────────────────────────────────
elif page == "📝 Notes Summarizer":
    track_feature_usage("notes")
    st.markdown("### 📝 Notes Summarizer")

    notes = st.text_area("Paste your notes here", height=260,
                         placeholder="Paste lecture notes, textbook passages, or any text…")
    length = st.select_slider("Summary length", ["Very Short", "Short", "Medium", "Detailed"], value="Medium")
    length_map = {"Very Short": "3 sentences", "Short": "5 sentences",
                  "Medium": "8–10 sentences", "Detailed": "15+ sentences"}

    if st.button("✨ Summarize", type="primary") and notes.strip():
        prompt = (
            f"Summarise the following academic notes in {length_map[length]}. "
            f"Preserve all key definitions, formulas, and important facts. "
            f"Use bullet points where helpful.\n\nNOTES:\n{notes}"
        )
        update_study_tracking(notes)
        with st.spinner("Summarising…"):
            resp, src = _ai(prompt, "Notes Summarizer",
                            fallback="Summary unavailable. Please check AI keys.")
        st.markdown(f'<div class="card card-green">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)
        _add_message("user", notes[:200] + "…")
        _add_message("assistant", resp)


# ── 4. Assignment Generator ───────────────────────────────────────────────────
elif page == "✍️ Assignment Generator":
    track_feature_usage("assignment")
    st.markdown("### ✍️ Assignment Generator")

    topic      = st.text_input("Assignment topic", placeholder="e.g. Cloud Computing and its Applications")
    c1, c2     = st.columns(2)
    word_count = c1.number_input("Target word count", 500, 5000, 1000, step=250)
    style      = c2.selectbox("Style", ["Academic Essay", "Technical Report", "Case Study", "Lab Report"])

    if st.button("📄 Generate Assignment", type="primary") and topic.strip():
        prompt = (
            f"Write a {style} on '{topic}'. "
            f"Target length: approximately {word_count} words. "
            f"Structure: Introduction → Main Body (with subheadings) → Conclusion → References. "
            f"Use formal academic English."
        )
        update_study_tracking(topic)
        with st.spinner("Writing assignment…"):
            resp, src = _ai(prompt, "Assignment Writer",
                            fallback=f"Assignment generation unavailable. Topic: {topic}")
        st.markdown(f'<div class="card">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download as .txt",
            data=resp,
            file_name=f"assignment_{topic[:25].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        _add_message("user", prompt[:200])
        _add_message("assistant", resp)


# ── 5. Assignment Checker ─────────────────────────────────────────────────────
elif page == "✓ Assignment Checker":
    track_feature_usage("checker")
    st.markdown("### ✓ Assignment Checker")
    st.info("Paste your assignment below to get AI feedback on grammar, structure, and content quality.")

    text = st.text_area("Paste your assignment", height=300,
                        placeholder="Paste the full text of your assignment here…")

    if st.button("🔍 Check Assignment", type="primary") and text.strip():
        # Word / sentence count (offline)
        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        c1, c2, c3 = st.columns(3)
        c1.metric("Words",     len(words))
        c2.metric("Sentences", len(sentences))
        c3.metric("Avg Sent",  f"{round(len(words)/max(1,len(sentences)),1)} words")

        _hr()
        prompt = (
            f"Review the following student assignment and provide constructive feedback. "
            f"Evaluate: (1) Grammar and spelling, (2) Sentence clarity, "
            f"(3) Structure and flow, (4) Argument quality, (5) Academic tone. "
            f"List specific improvements. Be encouraging but honest.\n\nASSIGNMENT:\n{text[:3000]}"
        )
        with st.spinner("Analysing…"):
            resp, src = _ai(prompt, "General Study Assistant",
                            fallback="AI feedback unavailable. Try checking: grammar, paragraph structure, and citation format.")
        st.markdown(f'<div class="card card-blue">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Feedback",
            data=resp,
            file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ── 6. Study Planner ──────────────────────────────────────────────────────────
elif page == "📅 Study Planner":
    track_feature_usage("planner")
    st.markdown("### 📅 Study Planner")

    c1, c2     = st.columns(2)
    exam_date  = c1.date_input("Exam date", value=date.today().replace(month=min(date.today().month + 1, 12)))
    hours_day  = c1.slider("Hours per day", 1.0, 10.0, 4.0, 0.5)
    subjects_r = c2.text_area("Subjects (one per line)", height=160,
                               placeholder="Python Programming\nDBMS\nOperating Systems\nComputer Networks")
    ai_tips    = c2.checkbox("✨ Add AI study tips for each subject")

    if st.button("📅 Generate Plan", type="primary"):
        subjects = [s.strip() for s in subjects_r.splitlines() if s.strip()]
        if not subjects:
            st.warning("Enter at least one subject.")
        elif exam_date <= date.today():
            st.warning("Exam date must be in the future.")
        else:
            plan = build_study_plan(subjects, exam_date, hours_day)
            days = (exam_date - date.today()).days
            st.success(f"📅 {days}-day plan · {len(subjects)} subjects · {hours_day}h/day · {round(days*hours_day)}h total")

            for entry in plan[:60]:
                is_rev = "Revision" in entry["subject"]
                colour = "card-red" if is_rev else "card-green"
                st.markdown(
                    f'<div class="card {colour}" style="padding:0.6rem 1.2rem">'
                    f'<b>{entry["date"]}</b>  —  {entry["subject"]}  '
                    f'<span style="color:#64748b">({entry["hours"]}h)</span><br>'
                    f'<span style="font-size:0.82rem;color:#94a3b8">{entry["note"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            if ai_tips and subjects:
                _hr()
                st.markdown("### ✨ AI Study Tips")
                prompt = (
                    f"I have {days} days to prepare for an exam covering: {', '.join(subjects)}. "
                    f"I study {hours_day} hours per day. "
                    f"Give me: 1) priority order for topics, 2) one key tip per subject, "
                    f"3) a revision strategy for the last 3 days."
                )
                with st.spinner("Getting AI tips…"):
                    resp, src = _ai(prompt, "Study Planner",
                                    fallback="Focus on weak areas first, practice past papers in the final 3 days.")
                st.markdown(f'<div class="card card-purple">{resp}{_source_badge(src)}</div>',
                            unsafe_allow_html=True)


# ── 7. Exam Paper Generator ───────────────────────────────────────────────────
elif page == "🧾 Exam Paper Generator":
    track_feature_usage("exam")
    st.markdown("### 🧾 Exam Paper Generator")

    c1, c2 = st.columns(2)
    subject    = c1.text_input("Subject",   placeholder="DBMS, Python, Computer Networks…")
    difficulty = c1.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
    duration   = c2.selectbox("Duration",   ["1 Hour", "2 Hours", "3 Hours"])
    marks      = c2.selectbox("Total Marks",["40", "50", "75", "100"])

    if st.button("📋 Generate Exam Paper", type="primary") and subject.strip():
        prompt = (
            f"Generate a university-style exam paper for: **{subject}**\n"
            f"Total Marks: {marks} | Duration: {duration} | Difficulty: {difficulty}\n\n"
            f"Format:\n"
            f"Section A: MCQs (20% of marks)\n"
            f"Section B: Short Answer (30% of marks, 3–4 questions)\n"
            f"Section C: Long Answer (50% of marks, 2–3 questions)\n\n"
            f"Include marks per question. Write clearly numbered questions."
        )
        update_study_tracking(subject)
        with st.spinner("Generating exam paper…"):
            resp, src = _ai(prompt, "Exam Prep",
                            fallback=f"Exam paper generation unavailable. Subject: {subject}")
        st.markdown(f'<div class="card">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)
        st.download_button(
            "⬇️ Download Exam Paper",
            data=resp,
            file_name=f"exam_{subject[:20].replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ── 8. Code Runner ────────────────────────────────────────────────────────────
elif page == "💻 Code Runner":
    track_feature_usage("runner")
    st.markdown("### 💻 Code Runner")
    st.warning("⚠️ Runs Python only. Dangerous imports (os, sys, subprocess…) are blocked.")

    snippets = {
        "— blank —":         "# Write your Python code here\nprint('Hello, World!')",
        "Hello World":       "print('Hello, World!')\nprint(2 ** 10)",
        "Fibonacci":         "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a, end=' ')\n        a, b = b, a+b\nfib(12)",
        "List Comprehension":"squares = [x**2 for x in range(1, 11)]\nprint('Squares:', squares)\nevens = [x for x in range(20) if x % 2 == 0]\nprint('Evens:', evens)",
        "Class Example":     "class Student:\n    def __init__(self, name, grade):\n        self.name = name\n        self.grade = grade\n    def __repr__(self):\n        return f'Student({self.name}, grade={self.grade})'\n\ns = Student('Alice', 'A')\nprint(s)",
    }
    starter  = st.selectbox("Load starter snippet", list(snippets.keys()))
    code_val = snippets[starter]
    code     = st.text_area("Python code", value=code_val, height=280)
    timeout  = st.slider("Timeout (seconds)", 3, 15, 8)

    if st.button("▶️ Run Code", type="primary"):
        with st.spinner("Executing…"):
            stdout, stderr = execute_python_code(code, timeout)

        if stdout:
            st.success("✅ Output")
            st.code(stdout, language="text")
        if stderr:
            if "Blocked" in stderr or "timed out" in stderr:
                st.warning(stderr)
            else:
                st.error("❌ Error")
                st.code(stderr, language="text")
        if not stdout and not stderr:
            st.info("Code ran successfully with no output.")


# ── 9. Study Recommender ──────────────────────────────────────────────────────
elif page == "🎓 Study Recommender":
    track_feature_usage("recommender")
    st.markdown("### 🎓 Study Recommender")

    # Offline rule-based recommendations always shown
    st.markdown(get_basic_recommendations())

    _hr()
    st.markdown("#### ✨ Personalised AI Learning Path")
    extra_topic = st.text_input("Topic or subject to focus on", placeholder="e.g. Data Structures")

    if st.button("Get AI Recommendations", type="primary"):
        studied = st.session_state.topics_studied
        prompt  = (
            f"Create a personalised learning path for a college CS student.\n"
            f"Topics already studied: {', '.join(studied) if studied else 'None yet'}\n"
            f"Focus area: {extra_topic or 'General CS'}\n\n"
            f"Provide:\n"
            f"1. Next 5 topics to learn (with priority order)\n"
            f"2. Why each topic matters\n"
            f"3. Recommended resources (free + paid)\n"
            f"4. Practice projects\n"
            f"5. Estimated time per topic"
        )
        with st.spinner("Building learning path…"):
            resp, src = _ai(prompt, "General Study Assistant",
                            fallback=get_basic_recommendations())
        st.markdown(f'<div class="card card-purple">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)


# ── 10. Dashboard ─────────────────────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.markdown("### 📊 Study Dashboard")

    total_actions = sum(st.session_state.feature_usage.values())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi"><h3>{st.session_state.questions_asked}</h3><p>Questions Asked</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi"><h3>{len(st.session_state.topics_studied)}</h3><p>Topics Explored</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi"><h3>{session_duration_text()}</h3><p>Session Duration</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi"><h3>{total_actions}</h3><p>Total Actions</p></div>', unsafe_allow_html=True)

    _hr()
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 📈 Feature Usage")
        feat_data = [(f, v) for f, v in get_most_used_features() if v > 0]
        if feat_data:
            for feat, count in feat_data:
                st.metric(feat, count)
        else:
            st.caption("No tool usage recorded yet.")

    with c2:
        st.markdown("#### 📚 Topics Studied")
        topics = st.session_state.topics_studied
        if topics:
            for t in topics:
                st.markdown(f"• {t}")
        else:
            st.caption("No topics tracked yet — start chatting!")

    _hr()
    st.markdown("#### 🕐 Recent Chat Activity")
    recent = st.session_state.messages[-5:]
    if recent:
        for msg in recent:
            icon    = "👤" if msg["role"] == "user" else "🤖"
            preview = msg["content"][:120] + ("…" if len(msg["content"]) > 120 else "")
            st.markdown(f"**{icon}** {preview}")
    else:
        st.caption("No chat activity yet.")

    if st.button("🔄 Reset Stats"):
        for k in ["questions_asked", "topics_studied", "messages"]:
            st.session_state[k] = 0 if k == "questions_asked" else []
        st.session_state.feature_usage = {k: 0 for k in st.session_state.feature_usage}
        st.rerun()


# ── 11. AI Chat ───────────────────────────────────────────────────────────────
elif page == "💬 AI Chat":
    track_feature_usage("ai_chat")
    st.markdown("### 💬 AI Chat")
    st.caption("Ask anything about your studies — OpenRouter → Gemini → Claude → Rules Engine.")

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Chat input
    prompt = st.chat_input("Ask anything…")
    if prompt:
        detect_user_info(prompt)
        update_study_tracking(prompt)

        with st.chat_message("user"):
            st.markdown(prompt)
        _add_message("user", prompt)

        with st.chat_message("assistant"):
            answer = _render_response(prompt, st.session_state.mode)
        _add_message("assistant", answer)


# ── 12. Quiz Generator ────────────────────────────────────────────────────────
elif page == "🧩 Quiz Generator":
    track_feature_usage("quiz")
    st.markdown("### 🧩 Quiz Generator")

    topic  = st.text_input("Quiz topic", placeholder="DBMS, Python OOP, OSI Model…")
    num_q  = st.slider("Number of questions", 3, 10, 5)
    level  = st.select_slider("Difficulty", ["Easy", "Mixed", "Hard"], value="Mixed")

    if st.button("🧩 Generate Quiz", type="primary") and topic.strip():
        prompt = (
            f"Create a {level.lower()}-difficulty quiz on **{topic}** with exactly {num_q} questions.\n"
            f"For each question provide:\n"
            f"  • The question\n"
            f"  • 4 labelled options (A, B, C, D)\n"
            f"  • The correct answer\n"
            f"  • A brief explanation (1–2 sentences)\n\n"
            f"Number questions clearly (Q1, Q2, …)."
        )
        update_study_tracking(topic)
        with st.spinner("Generating quiz…"):
            resp, src = _ai(prompt, "Quiz Generator",
                            fallback=f"Quiz generation unavailable. Topic: {topic}")
        st.markdown(f'<div class="card">{resp}{_source_badge(src)}</div>',
                    unsafe_allow_html=True)
        _add_message("user",      f"Generate quiz on {topic}")
        _add_message("assistant", resp)


# ── 13. Code Helper ───────────────────────────────────────────────────────────
elif page == "🐛 Code Helper":
    track_feature_usage("code")
    st.markdown("### 🐛 Code Helper")

    action = st.radio(
        "What do you need?",
        ["🔍 Debug & Fix", "📖 Explain Code", "⚡ Optimise", "✍️ Write Code"],
        horizontal=True,
    )

    if "✍️ Write" in action:
        desc     = st.text_area("Describe what the code should do", height=120,
                                placeholder="Write a Python function to merge two sorted lists…")
        lang_sel = st.selectbox("Language", ["Python", "Java", "C++", "JavaScript", "SQL"])
        if st.button("✍️ Generate Code", type="primary") and desc.strip():
            prompt = (
                f"Write clean, well-commented {lang_sel} code for:\n{desc}\n\n"
                f"Include: function/class definition, example usage, and a short explanation."
            )
            with st.spinner("Writing code…"):
                resp, src = _ai(prompt, "Programming Helper",
                                fallback=f"# {lang_sel} code for: {desc}\n# AI unavailable.")
            st.markdown(f'<div class="card">{resp}{_source_badge(src)}</div>',
                        unsafe_allow_html=True)
    else:
        code = st.text_area("Paste your code", height=250,
                            placeholder="# Paste your code here…")
        err  = ""
        if "🔍 Debug" in action:
            err = st.text_input("Error message (optional)",
                                placeholder="e.g. TypeError: unsupported operand type(s)…")

        if st.button("🔍 Analyse", type="primary") and code.strip():
            if "🔍 Debug" in action:
                prompt = (
                    f"Debug this code:\n```\n{code}\n```\n"
                    + (f"\nError: {err}\n" if err else "")
                    + "\nProvide: (1) Root cause, (2) Fixed code, (3) Explanation."
                )
                mode = "Code Debugger"
            elif "📖 Explain" in action:
                prompt = (
                    f"Explain this code line by line for a student:\n```\n{code}\n```\n"
                    f"Cover: purpose, logic flow, data structures, time/space complexity."
                )
                mode = "Programming Helper"
            else:  # Optimise
                prompt = (
                    f"Analyse and optimise this code:\n```\n{code}\n```\n"
                    f"Provide: (1) Issues, (2) Optimised version, (3) Explanation."
                )
                mode = "Code Debugger"

            update_study_tracking("code debugging")
            with st.spinner("Analysing…"):
                resp, src = _ai(prompt, mode,
                                fallback="AI unavailable. Check: syntax errors, off-by-one issues, and variable names.")
            st.markdown(f'<div class="card">{resp}{_source_badge(src)}</div>',
                        unsafe_allow_html=True)
            _add_message("user",      f"[Code analysis: {action}]")
            _add_message("assistant", resp)


# ─────────────────────────────────────────────────────────────────────────────
#  Footer
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<hr style='border-color:#1e2d4a;margin-top:2rem'>
<div style='text-align:center;color:#475569;font-size:0.78rem;padding-bottom:1rem'>
  🎓 AI Academic Platform &nbsp;·&nbsp; Gemini 1.5 Flash + Claude 3 Haiku
  &nbsp;·&nbsp; Built for college students
</div>
""", unsafe_allow_html=True)
