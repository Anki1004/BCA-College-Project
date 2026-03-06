"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     BCA AI STUDY ASSISTANT                                ║
║                  Advanced AI Learning Platform                            ║
║              Powered by Google Gemini API                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

Author: BCA AI Team
Version: 2.0 - Enhanced Edition
Features: AI Chat, PDF Study Chat, Quiz Generator, Code Helper, 
          Notes Summarizer, Assignment Generator, Study Planner,
          Exam Paper Generator, Dashboard with Analytics
"""

import json
import re
import time
from datetime import datetime, timedelta
from io import BytesIO

import google.generativeai as genai
import streamlit as st

# PDF processing
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
#                            PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BCA AI Assistant - Advanced Learning Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ═══════════════════════════════════════════════════════════════════════════
#                         RESPONSIVE CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary: #060b18;
    --bg-secondary: #0d1526;
    --bg-card: #111c33;
    --accent-blue: #38bdf8;
    --accent-purple: #818cf8;
    --accent-cyan: #22d3ee;
    --accent-green: #4ade80;
    --accent-pink: #f472b6;
    --text-primary: #e2e8f0;
    --text-muted: #64748b;
    --border: rgba(56,189,248,0.15);
}

* { 
    font-family: 'Space Grotesk', sans-serif !important; 
    box-sizing: border-box;
}
code, pre { font-family: 'JetBrains Mono', monospace !important; }

html, body, .stApp {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    overflow-x: hidden;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(56,189,248,0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(34,211,238,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.hero-header {
    text-align: center;
    padding: 30px 20px 20px;
    position: relative;
}

.hero-title {
    font-size: clamp(24px, 5vw, 52px);
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 40%, #22d3ee 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    line-height: 1.2;
    margin-bottom: 8px;
    word-wrap: break-word;
}

.hero-subtitle {
    font-size: clamp(10px, 2.5vw, 15px);
    color: #64748b;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    font-weight: 500;
    word-wrap: break-word;
}

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
    box-shadow: 0 0 8px rgba(74,222,128,0.6);
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.3); }
}

@keyframes typing {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}

.typing-indicator {
    animation: typing 1.4s infinite;
}

/* Chat Messages - Responsive */
[data-testid="stChatMessageContent"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    color: var(--text-primary) !important;
    line-height: 1.7 !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    max-width: 100% !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* Code Blocks - Horizontal Scroll */
pre {
    background: #0a1628 !important;
    border: 1px solid rgba(56,189,248,0.2) !important;
    border-radius: 10px !important;
    padding: 16px !important;
    overflow-x: auto !important;
    max-width: 100% !important;
    white-space: pre !important;
}

code {
    color: #38bdf8 !important;
    font-size: clamp(11px, 2vw, 13px) !important;
    word-break: break-all !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* Buttons - Responsive */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #38bdf8) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    width: 100% !important;
    padding: 10px 16px !important;
    font-size: clamp(12px, 2.5vw, 14px) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
    opacity: 0.95 !important;
}

/* Input Fields - Responsive */
.stSelectbox > div > div,
.stTextArea textarea,
.stTextInput input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: white !important;
    font-size: clamp(12px, 2.5vw, 14px) !important;
}

.stTextArea textarea {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: clamp(11px, 2vw, 13px) !important;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* Metrics - Responsive */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

[data-testid="stMetricLabel"] { 
    color: #64748b !important; 
    font-size: clamp(10px, 2vw, 12px) !important; 
}
[data-testid="stMetricValue"] { 
    color: #38bdf8 !important; 
    font-size: clamp(18px, 4vw, 22px) !important; 
    font-weight: 700 !important; 
}

/* Chat Input - Always Visible */
[data-testid="stChatInput"] {
    position: sticky !important;
    bottom: 0 !important;
    z-index: 999 !important;
    background: var(--bg-primary) !important;
    padding: 10px 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(56,189,248,0.6); }

/* Info/Warning/Success boxes */
.stAlert {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* ═══════════════════════════════════════════════════════════
   RESPONSIVE BREAKPOINTS - MEDIA QUERIES
   ═══════════════════════════════════════════════════════════ */

/* Desktop - 1200px and above */
@media (min-width: 1200px) {
    .hero-title { font-size: 52px; }
    .hero-subtitle { font-size: 15px; }
    [data-testid="stSidebar"] { min-width: 280px !important; }
}

/* Tablet - 768px to 1199px */
@media (max-width: 1199px) and (min-width: 768px) {
    .hero-title { font-size: 38px; }
    .hero-subtitle { font-size: 13px; letter-spacing: 1.5px; }
    .hero-header { padding: 20px 15px 15px; }
    [data-testid="stChatMessageContent"] { padding: 12px 16px !important; }
    [data-testid="stMetric"] { padding: 12px !important; }
    .stButton > button { padding: 8px 12px !important; }
}

/* Mobile - 480px to 767px */
@media (max-width: 767px) and (min-width: 480px) {
    .hero-title { font-size: 28px; }
    .hero-subtitle { font-size: 11px; letter-spacing: 1px; }
    .hero-header { padding: 15px 10px 10px; }
    [data-testid="stChatMessageContent"] { 
        padding: 10px 14px !important; 
        border-radius: 12px !important;
    }
    pre { padding: 12px !important; font-size: 11px !important; }
    [data-testid="stMetric"] { padding: 10px !important; }
    .stButton > button { padding: 8px 10px !important; font-size: 12px !important; }
    [data-testid="stSidebar"] { min-width: 200px !important; }
}

/* Small Mobile - Below 480px */
@media (max-width: 479px) {
    .hero-title { font-size: 24px; letter-spacing: -0.5px; }
    .hero-subtitle { 
        font-size: 9px; 
        letter-spacing: 0.5px;
        line-height: 1.4;
    }
    .hero-header { padding: 12px 8px 8px; }
    .status-dot { width: 6px; height: 6px; }
    [data-testid="stChatMessageContent"] { 
        padding: 8px 12px !important; 
        border-radius: 10px !important;
        font-size: 13px !important;
    }
    pre { 
        padding: 10px !important; 
        font-size: 10px !important;
        border-radius: 8px !important;
    }
    code { font-size: 10px !important; }
    [data-testid="stMetric"] { 
        padding: 8px !important;
        border-radius: 8px !important;
    }
    [data-testid="stMetricLabel"] { font-size: 9px !important; }
    [data-testid="stMetricValue"] { font-size: 16px !important; }
    .stButton > button { 
        padding: 6px 8px !important; 
        font-size: 11px !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea { font-size: 11px !important; }
    [data-testid="stSidebar"] { min-width: 180px !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
#                         APPLICATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

NAV_ITEMS = [
    "Home",
    "AI Chat",
    "📄 PDF Study Chat",
    "Quiz Generator",
    "Code Helper",
    "Notes Summarizer",
    "📝 Assignment Generator",
    "📅 Study Planner",
    "🧾 Exam Paper Generator",
    "Dashboard",
]

STUDY_MODES = [
    "Programming Helper",
    "Code Debugger",
    "Quiz Generator",
    "Notes Summarizer",
    "Assignment Writer",
    "Study Planner",
    "Exam Prep",
    "General Study Assistant",
]

# Enhanced Academic Prompts for Better Educational Content
MODE_PROMPTS = {
    "Programming Helper": """You are an expert programming tutor for BCA students.
- Explain concepts with clarity and practical examples
- Include code snippets with explanations
- Mention real-world applications
- Provide step-by-step breakdowns
- End with practice suggestions""",
    
    "Code Debugger": """You are a professional code debugging assistant.
- Identify syntax and logic errors systematically
- Explain WHY the error occurs
- Provide corrected code with improvements
- Include best practices and optimization tips
- Use clear formatting with headings""",
    
    "Quiz Generator": """You are an academic quiz creator for BCA exams.
- Generate exactly 5 MCQs with 4 options each
- Mark correct answers clearly
- Keep questions exam-oriented and syllabus-based
- Include brief explanations for answers
- Balance difficulty levels""",
    
    "Notes Summarizer": """You are an exam preparation specialist.
- Convert lengthy notes into structured bullet points
- Highlight key definitions and formulas
- Use clear headings and subheadings
- Include quick revision checkpoints
- Format for easy scanning""",
    
    "Assignment Writer": """You are an academic assignment assistant.
- Structure content like college assignments
- Include: Title, Introduction, Body with headings, Conclusion
- Use formal academic language
- Provide reference suggestions
- Ensure proper formatting""",
    
    "Study Planner": """You are a study planning expert.
- Create realistic day-by-day study schedules
- Balance topics across available time
- Include revision slots
- Consider exam preparation strategies
- Provide motivational tips""",
    
    "Exam Prep": """You are an examination preparation specialist.
- Generate realistic exam paper formats
- Include different sections (MCQ, Short, Long)
- Set appropriate marks distribution
- Match university exam patterns
- Provide time management tips""",
    
    "General Study Assistant": """You are a comprehensive AI Study Assistant for BCA students.
- Help with programming, CS theory, and exam prep
- Provide educational, student-friendly responses
- Include examples relevant to BCA syllabus
- Use structured formatting with headings
- Focus on learning outcomes""",
}

BASE_ACADEMIC_CONTEXT = """
You are an AI Study Assistant designed specifically for BCA (Bachelor of Computer Applications) students.
Your primary role is to facilitate learning, understanding, and exam preparation in:
- Programming Languages (Python, Java, C, C++)
- Database Management Systems
- Operating Systems
- Computer Networks
- Data Structures and Algorithms
- Software Engineering
- Web Development

Guidelines for responses:
1. Be educational and student-friendly
2. Include practical examples from BCA syllabus
3. Use proper formatting with headings and bullet points
4. Avoid generic chatbot-style responses
5. Focus on conceptual understanding
6. Provide actionable next steps
7. Keep language simple yet professional
"""

RESPONSE_FORMAT_GUIDELINES = """
Format all responses using this structure:
1. Start with a clear heading (##)
2. Brief introduction (1-2 sentences)
3. Main content with bullet points or numbered lists
4. Include at least one relevant example
5. Use code blocks with language tags when showing code
6. End with "Next Steps" or "Practice Tip" section
7. Keep tone encouraging and supportive
"""

QUICK_PROMPTS = {
    "Programming Helper": [
        "Explain recursion with Python example",
        "Difference between list and tuple",
        "What is time complexity? Explain with examples",
        "OOP pillars explained simply",
    ],
    "Code Debugger": [
        "Find bug in this loop",
        "Explain this Python traceback error",
        "Why IndexError occurs?",
        "Debug my SQL query",
    ],
    "Quiz Generator": [
        "Create quiz on DBMS normalization",
        "Generate MCQs on OS scheduling",
        "Quiz on C programming basics",
        "Python OOP MCQs",
    ],
    "Notes Summarizer": [
        "Summarize OS process scheduling",
        "DBMS normalization quick notes",
        "Computer Networks revision points",
        "Software lifecycle summary",
    ],
    "Assignment Writer": [
        "Write assignment on Cloud Computing",
        "DBMS assignment on normalization",
        "OS assignment on deadlock",
        "Software Engineering lifecycle assignment",
    ],
    "Study Planner": [
        "Plan for DBMS exam in 15 days",
        "Create study schedule for semester",
        "Revision plan for all subjects",
        "Daily study routine suggestion",
    ],
    "Exam Prep": [
        "Generate DBMS exam paper",
        "OS mid-semester question paper",
        "Python practical exam questions",
        "Data Structures exam paper",
    ],
    "General Study Assistant": [
        "Explain ACID properties with examples",
        "Compiler vs Interpreter difference",
        "How to prepare for BCA exams?",
        "TCP vs UDP comparison",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════
#                         SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_session() -> None:
    """Initialize all session state variables with defaults"""
    defaults = {
        # Chat & Navigation
        "messages": [],
        "mode": "General Study Assistant",
        "nav": "Home",
        
        # Model Configuration
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.5,
        "typing_speed": 0.01,
        "show_timestamps": True,
        
        # Session Tracking
        "session_start_dt": datetime.now(),
        "questions_asked": 0,
        "topics_studied": [],
        
        # Feature Usage Analytics
        "feature_usage": {
            "AI Chat": 0,
            "PDF Study Chat": 0,
            "Quiz Generator": 0,
            "Code Helper": 0,
            "Notes Summarizer": 0,
            "Assignment Generator": 0,
            "Study Planner": 0,
            "Exam Paper Generator": 0,
        },
        
        # PDF Study Chat
        "pdf_content": None,
        "pdf_filename": None,
        "pdf_chat_history": [],
        
        # User Content
        "user_notes": "",
        "code_scratch": "",
        
        # Theme
        "theme": "dark",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()


# ═══════════════════════════════════════════════════════════════════════════
#                              UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════
def unique_topics(topics: list[str]) -> list[str]:
    seen = set()
    ordered = []
    for topic in topics:
        t = topic.strip().lower()
        if t and t not in seen:
            seen.add(t)
            ordered.append(topic.strip())
    return ordered


def extract_topics(text: str) -> list[str]:
    topic_keywords = [
        "python",
        "java",
        "c",
        "c++",
        "dbms",
        "sql",
        "os",
        "operating system",
        "network",
        "computer networks",
        "dsa",
        "data structures",
        "algorithms",
        "software engineering",
        "ai",
        "machine learning",
        "cybersecurity",
        "oop",
        "compiler",
        "cloud computing",
    ]
    lower = text.lower()
    matched = [kw.title() for kw in topic_keywords if kw in lower]
    return unique_topics(matched)


def update_study_tracking(user_text: str) -> None:
    st.session_state.questions_asked += 1
    new_topics = extract_topics(user_text)
    st.session_state.topics_studied = unique_topics(st.session_state.topics_studied + new_topics)


def session_duration_text() -> str:
    delta = datetime.now() - st.session_state.session_start_dt
    total_seconds = int(delta.total_seconds())
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def extract_code_block(text: str) -> tuple[str | None, str | None]:
    fence_match = re.search(r"```(\w+)?\n([\s\S]*?)```", text)
    if fence_match:
        language = fence_match.group(1).strip() if fence_match.group(1) else None
        code = fence_match.group(2).strip()
        return language, code

    if "\n" in text and any(sym in text for sym in ["def ", "class ", "{", "}", ";", "import ", "#include"]):
        return None, text.strip()

    return None, None


def detect_language(code: str, hinted_language: str | None = None) -> str:
    if hinted_language:
        return hinted_language.lower()

    patterns = {
        "python": [r"\bdef\b", r"\bimport\b", r"print\("],
        "java": [r"\bpublic class\b", r"System\.out\.println", r"\bstatic void main\b"],
        "cpp": [r"#include\s*<", r"std::", r"int\s+main\s*\("],
        "c": [r"#include\s*<stdio\.h>", r"printf\(", r"int\s+main\s*\("],
        "javascript": [r"\bfunction\b", r"console\.log\(", r"=>"],
        "sql": [r"\bSELECT\b", r"\bINSERT\b", r"\bUPDATE\b", r"\bFROM\b"],
    }

    for lang, checks in patterns.items():
        if any(re.search(check, code, flags=re.IGNORECASE) for check in checks):
            return lang
    return "text"


def build_system_prompt(mode: str) -> str:
    mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["General Study Assistant"])
    return f"""
{BASE_ACADEMIC_CONTEXT}

Mode Instruction:
{mode_prompt}

{RESPONSE_FORMAT_GUIDELINES}
""".strip()


def build_mode_specific_user_prompt(user_prompt: str, mode: str) -> str:
    language_hint, code = extract_code_block(user_prompt)

    if mode == "Quiz Generator":
        return (
            "Generate exactly 5 multiple-choice questions for BCA students on the requested topic.\n"
            "Rules:\n"
            "- Each question must have 4 options labeled A, B, C, D\n"
            "- Clearly mention the correct answer below each question\n"
            "- Keep difficulty moderate for exam prep\n"
            "- Keep wording concise and syllabus oriented\n"
            f"\nStudent Topic/Request: {user_prompt}"
        )

    if mode == "Code Debugger":
        if code:
            detected = detect_language(code, language_hint)
            return (
                f"Student submitted {detected} code for debugging.\n"
                "Do the following in order:\n"
                "1. Detected Language\n"
                "2. Syntax/logic errors\n"
                "3. Why the error happens\n"
                "4. Corrected code\n"
                "5. Best practice tip\n\n"
                f"Code:\n```{detected}\n{code}\n```"
            )
        return (
            "The student is in Code Debugger mode. Ask for the code if missing, then provide step-by-step debugging support.\n"
            f"Student message: {user_prompt}"
        )

    if mode == "Notes Summarizer":
        return (
            "Summarize the provided notes into exam-ready bullets with clear headings.\n"
            "Also include: key definitions, important formulas/points, and quick revision checklist.\n"
            f"\nStudent notes/request:\n{user_prompt}"
        )

    return user_prompt


def get_gemini_response(user_prompt: str, mode: str, history: list[dict] | None = None) -> str:
    try:
        api_keys = st.secrets["GEMINI_KEYS"]
    except Exception:
        return "⚠️ API keys not found. Please configure `GEMINI_KEYS` in Streamlit secrets."

    if not isinstance(api_keys, list):
        api_keys = [api_keys]

    system_prompt = build_system_prompt(mode)
    mode_prompt = build_mode_specific_user_prompt(user_prompt, mode)

    context = ""
    if history:
        recent = history[-8:]
        if recent:
            lines = []
            for msg in recent:
                role = "Student" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['content'][:350]}")
            context = "\n".join(lines)

    full_prompt = (
        f"SYSTEM:\n{system_prompt}\n\n"
        f"RECENT CONTEXT:\n{context if context else 'No prior context.'}\n\n"
        f"STUDENT QUERY:\n{mode_prompt}"
    )

    for key in api_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel(st.session_state.model)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=st.session_state.temperature,
                    max_output_tokens=2048,
                ),
            )
            return response.text.strip() if response.text else "No response generated."
        except Exception as err:
            msg = str(err).lower()
            if "429" in msg or "quota" in msg or "invalid" in msg:
                continue
            return f"⚠️ Error: {err}"

    return "🚀 All API keys are busy or exhausted. Please try again shortly."


def export_chat_markdown() -> str:
    if not st.session_state.messages:
        return ""

    lines = [
        "# BCA AI Assistant - Chat Export",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Study Mode:** {st.session_state.mode}",
        "---",
        "",
    ]
    for msg in st.session_state.messages:
        role = "👤 Student" if msg["role"] == "user" else "🤖 Assistant"
        ts = msg.get("timestamp", "")
        lines.append(f"### {role} `{ts}`\n{msg['content']}\n")
    return "\n".join(lines)


def export_chat_json() -> str:
    return json.dumps(
        {
            "exported_at": datetime.now().isoformat(),
            "mode": st.session_state.mode,
            "messages": st.session_state.messages,
            "questions_asked": st.session_state.questions_asked,
            "topics_studied": st.session_state.topics_studied,
        },
        indent=2,
    )


def extract_pdf_text(uploaded_file) -> tuple[str, str]:
    """Extract text from uploaded PDF file"""
    if not PDF_AVAILABLE:
        return None, "PyPDF library not installed. Run: pip install pypdf"
    
    try:
        pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
        text_content = []
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"[Page {page_num}]\n{page_text}")
        
        full_text = "\n\n".join(text_content)
        
        if not full_text.strip():
            return None, "No text could be extracted from PDF"
        
        return full_text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"


def chunk_text(text: str, max_chunk_size: int = 8000) -> list[str]:
    """Simple text chunking for large PDF content"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        para_size = len(para)
        if current_size + para_size > max_chunk_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = para_size
        else:
            current_chunk.append(para)
            current_size += para_size
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks


def find_relevant_pdf_content(pdf_text: str, query: str, max_length: int = 6000) -> str:
    """Find most relevant section of PDF for the query"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    chunks = chunk_text(pdf_text, max_chunk_size=2000)
    
    if len(chunks) <= 1:
        return pdf_text[:max_length]
    
    # Score each chunk based on query word overlap
    chunk_scores = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower and len(word) > 3)
        chunk_scores.append((score, chunk))
    
    # Sort by relevance and take top chunks
    chunk_scores.sort(reverse=True, key=lambda x: x[0])
    relevant_chunks = [chunk for score, chunk in chunk_scores[:3]]
    
    combined = "\n\n".join(relevant_chunks)
    return combined[:max_length]


def track_feature_usage(feature_name: str) -> None:
    """Track which features are being used"""
    if feature_name in st.session_state.feature_usage:
        st.session_state.feature_usage[feature_name] += 1


def get_most_used_features() -> list[tuple[str, int]]:
    """Get features sorted by usage"""
    usage = st.session_state.feature_usage.items()
    return sorted(usage, key=lambda x: x[1], reverse=True)


# ═══════════════════════════════════════════════════════════════════════════
#                              SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 20px;">
            <div style="font-size:40px; margin-bottom:6px;">🤖</div>
            <div style="font-size:18px; font-weight:700; background: linear-gradient(135deg,#38bdf8,#818cf8);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;">BCA Assistant</div>
            <div style="font-size:11px; color:#475569; letter-spacing:2px; text-transform:uppercase;">AI Study Companion</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("#### 📍 Navigation")
    st.session_state.nav = st.radio(
        "Navigation",
        options=NAV_ITEMS,
        index=NAV_ITEMS.index(st.session_state.nav),
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("#### 🎯 Study Mode")
    st.session_state.mode = st.selectbox(
        "Mode",
        STUDY_MODES,
        index=STUDY_MODES.index(st.session_state.mode),
        label_visibility="collapsed",
    )

    st.caption("Academic context: AI Study Assistant for BCA students")

    with st.expander("⚙️ Model Settings", expanded=False):
        st.session_state.model = st.selectbox(
            "Gemini Model",
            ["gemini-2.0-flash-exp", "gemini-2.0-flash-lite", "gemini-1.5-pro", "gemini-1.5-flash"],
            index=0,
        )
        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
        )
        st.session_state.typing_speed = st.slider(
            "Typing Speed",
            min_value=0.0,
            max_value=0.08,
            value=st.session_state.typing_speed,
            step=0.01,
        )

    with st.expander("🖥️ Display Settings", expanded=False):
        st.session_state.show_timestamps = st.checkbox("Show timestamps", value=st.session_state.show_timestamps)

    st.divider()
    st.markdown("#### 📊 Session Snapshot")
    a, b = st.columns(2)
    with a:
        st.metric("Questions", st.session_state.questions_asked)
    with b:
        st.metric("Topics", len(st.session_state.topics_studied))
    st.caption(f"Duration: {session_duration_text()}")

    st.divider()

    st.markdown("#### 💾 Export Chat")
    if st.session_state.messages:
        x, y = st.columns(2)
        with x:
            st.download_button(
                "📄 MD",
                data=export_chat_markdown(),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with y:
            st.download_button(
                "📦 JSON",
                data=export_chat_json(),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.caption("No messages to export yet.")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.questions_asked = 0
        st.session_state.topics_studied = []
        st.rerun()


# ---------------- MAIN HEADER ----------------
st.markdown(
    f"""
<div class="hero-header">
    <div class="hero-title">🤖 BCA AI Study Assistant</div>
    <div class="hero-subtitle">
        <span class="status-dot"></span>
        Powered by Google Gemini · Active Mode: {st.session_state.mode}
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------- TOOLS ----------------
def add_chat_message(role: str, content: str) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M"),
            "mode": st.session_state.mode,
        }
    )


def render_assistant_response(prompt: str, mode: str) -> str:
    response = get_gemini_response(prompt, mode, st.session_state.messages)

    placeholder = st.empty()
    speed = st.session_state.typing_speed
    final_text = ""

    if speed > 0:
        words = response.split()
        for idx, word in enumerate(words):
            final_text += word + " "
            if idx % 3 == 0:
                placeholder.markdown(final_text + "▌")
                time.sleep(speed)
        placeholder.markdown(final_text.strip())
    else:
        placeholder.markdown(response)
        final_text = response

    return final_text.strip()


# ---------------- UI PAGES ----------------
def page_home() -> None:
    st.markdown("### Home")
    st.markdown(
        """
        <div style="background: rgba(56,189,248,0.05); border: 1px solid rgba(56,189,248,0.15);
             border-radius: 16px; padding: 18px; margin-bottom: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">Academic AI Assistant for BCA Students</div>
            <div style="font-size: 13px; color: #94a3b8; line-height: 1.8;">
                Use Study Modes to switch behavior between tutoring, debugging, quizzes, summarization, and general prep.
                This assistant is designed for programming, computer science subjects, assignments, and exam revision.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Questions Asked", st.session_state.questions_asked)
    with c2:
        st.metric("Topics Studied", len(st.session_state.topics_studied))
    with c3:
        st.metric("Session Duration", session_duration_text())

    st.markdown("### Recommended Workflow")
    st.markdown("1. Choose a study mode in the sidebar based on your task.")
    st.markdown("2. Use AI Chat for explanations, Code Helper for debugging, and Notes Summarizer for revision.")
    st.markdown("3. Open Dashboard to monitor your study activity.")


def page_ai_chat() -> None:
    st.markdown("### AI Chat")

    if not st.session_state.messages:
        st.markdown("#### Quick Prompts")
        quick = QUICK_PROMPTS.get(st.session_state.mode, [])
        col_left, col_right = st.columns(2)
        for idx, qp in enumerate(quick):
            with col_left if idx % 2 == 0 else col_right:
                if st.button(qp, key=f"quick_{idx}", use_container_width=True):
                    st.session_state._quick_prompt = qp
                    st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if st.session_state.show_timestamps and msg.get("timestamp"):
                st.caption(f"🕐 {msg['timestamp']} · {msg.get('mode', st.session_state.mode)}")

    prompt_input = st.chat_input(f"Ask in {st.session_state.mode} mode...")
    if hasattr(st.session_state, "_quick_prompt"):
        prompt_input = st.session_state._quick_prompt
        del st.session_state._quick_prompt

    if prompt_input:
        update_study_tracking(prompt_input)
        with st.chat_message("user"):
            st.markdown(prompt_input)
            if st.session_state.show_timestamps:
                st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
        add_chat_message("user", prompt_input)

        with st.chat_message("assistant"):
            final_response = render_assistant_response(prompt_input, st.session_state.mode)
            if st.session_state.show_timestamps:
                st.caption(
                    f"🕐 {datetime.now().strftime('%H:%M')} · {len(final_response.split())} words"
                )
        add_chat_message("assistant", final_response)


def page_quiz_generator() -> None:
    st.markdown("### Quiz Generator")
    st.info("Generate 5 MCQ questions with 4 options each and the correct answer for exam practice.")

    topic = st.text_input("Enter topic", placeholder="Example: DBMS normalization, Python OOP, Operating System scheduling")
    if st.button("Generate 5 MCQs", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic first.")
            return

        st.session_state.mode = "Quiz Generator"
        prompt = f"Create quiz for topic: {topic.strip()}"
        update_study_tracking(prompt)

        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Quiz Generator")
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)


def page_code_helper() -> None:
    st.markdown("### Code Helper")
    st.info("Paste your code to detect language, identify syntax issues, and get corrected code.")

    code_input = st.text_area(
        "Paste code",
        height=280,
        placeholder="Paste code here. You can use plain code or fenced blocks.",
        key="code_helper_input",
    )
    extra_context = st.text_input("Error message (optional)", placeholder="Example: IndexError: list index out of range")

    if st.button("Debug Code", use_container_width=True):
        if not code_input.strip():
            st.warning("Please paste code first.")
            return

        st.session_state.mode = "Code Debugger"
        wrapped = f"```\n{code_input}\n```"
        debug_prompt = wrapped
        if extra_context.strip():
            debug_prompt += f"\n\nObserved error:\n{extra_context.strip()}"

        update_study_tracking("code debugging " + extra_context)
        with st.chat_message("assistant"):
            result = render_assistant_response(debug_prompt, "Code Debugger")
        add_chat_message("user", debug_prompt)
        add_chat_message("assistant", result)


def page_notes_summarizer() -> None:
    st.markdown("### Notes Summarizer")
    st.info("Paste long academic notes and convert them into revision-focused bullet points.")

    notes = st.text_area(
        "Paste notes",
        height=300,
        placeholder="Paste lecture notes, textbook paragraphs, or your own notes...",
        key="notes_summarizer_input",
    )

    if st.button("Summarize Notes", use_container_width=True):
        if not notes.strip():
            st.warning("Please paste notes first.")
            return

        st.session_state.mode = "Notes Summarizer"
        update_study_tracking("notes summarization")
        with st.chat_message("assistant"):
            result = render_assistant_response(notes, "Notes Summarizer")
        add_chat_message("user", notes)
        add_chat_message("assistant", result)


def page_dashboard() -> None:
    st.markdown("### Study Dashboard")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Questions Asked", st.session_state.questions_asked)
    with m2:
        st.metric("Topics Studied", len(st.session_state.topics_studied))
    with m3:
        st.metric("Session Duration", session_duration_text())

    st.markdown("#### Topics Studied")
    if st.session_state.topics_studied:
        st.write(" • " + "\n • ".join(st.session_state.topics_studied))
    else:
        st.caption("No topics tracked yet. Ask questions to build your dashboard.")

    st.markdown("#### Recent Conversation")
    recent = st.session_state.messages[-6:]
    if recent:
        for item in recent:
            role = "Student" if item["role"] == "user" else "Assistant"
            st.markdown(f"**{role} ({item.get('timestamp', '')})**: {item['content'][:180]}")
    else:
        st.caption("No chat activity yet.")


# ---------------- ROUTING ----------------
if st.session_state.nav == "Home":
    page_home()
elif st.session_state.nav == "AI Chat":
    page_ai_chat()
elif st.session_state.nav == "Quiz Generator":
    page_quiz_generator()
elif st.session_state.nav == "Code Helper":
    page_code_helper()
elif st.session_state.nav == "Notes Summarizer":
    page_notes_summarizer()
elif st.session_state.nav == "Dashboard":
    page_dashboard()
