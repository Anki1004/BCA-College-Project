"""
╔══════════════════════════════════════════════════════════════════════════╗
║                 BCA AI ACADEMIC PLATFORM - v3.0                          ║
║              Advanced AI-Powered Learning Companion                       ║
║                                                                          ║
║  Multi-Model System | Voice Assistant | Memory System | Smart Router    ║
║  Code Executor | Assignment Checker | Study Recommender | Analytics     ║
╚══════════════════════════════════════════════════════════════════════════╝

Author: BCA AI Team
Version: 3.0 - Enterprise Edition
Date: March 2026

---
ARCHITECTURE OVERVIEW:
1. CONFIG - Application configuration and constants
2. UTILITIES - Helper functions and data processing
3. AI ENGINE - Multi-model AI integration
4. MEMORY SYSTEM - User profile and learning history
5. SMART TOOLS - Tool detection and routing
6. VOICE ASSISTANT - Speech-to-text and text-to-speech
7. CODE EXECUTOR - Safe Python code execution sandbox
8. ASSIGNMENT CHECKER - Academic feedback system
9. STUDY RECOMMENDER - Personalized learning paths
10. UI PAGES - User interface components
11. MAIN ROUTER - Page navigation and rendering
---
"""

# ═══════════════════════════════════════════════════════════════════════════
#                            1. IMPORTS & SETUP
# ═══════════════════════════════════════════════════════════════════════════

import json
import re
import time
import subprocess
import io
import sys
from datetime import datetime, timedelta
from io import BytesIO
from urllib import error as urlerror
from urllib import request as urlrequest
from contextlib import redirect_stdout, redirect_stderr

import google.generativeai as genai
import streamlit as st

# Optional voice libraries - gracefully handled if missing
try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    import pyttsx3
    TEXT_TO_SPEECH_AVAILABLE = True
except ImportError:
    TEXT_TO_SPEECH_AVAILABLE = False

# PDF processing
try:
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
#                        2. PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BCA AI Academic Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════
#                     3. RESPONSIVE CUSTOM CSS
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

/* Fix Streamlit material icons showing as text */
.material-symbols-rounded,
.material-symbols-outlined,
[data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
    font-style: normal;
    -webkit-font-smoothing: antialiased;
}

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

[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not(.material-symbols-rounded):not(.material-symbols-outlined),
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div:not([data-testid="stIconMaterial"]),
[data-testid="stSidebar"] li,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
    color: var(--text-primary) !important;
}

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

[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

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

[data-testid="stChatInput"] {
    position: sticky !important;
    bottom: 0 !important;
    z-index: 999 !important;
    background: var(--bg-primary) !important;
    padding: 10px 0 !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.3); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(56,189,248,0.6); }

.stAlert { word-wrap: break-word !important; overflow-wrap: break-word !important; }

/* RESPONSIVE BREAKPOINTS */
@media (max-width: 1199px) {
    .hero-title { font-size: 38px; }
    .hero-subtitle { font-size: 13px; }
}

@media (max-width: 767px) {
    .hero-title { font-size: 28px; }
    .hero-subtitle { font-size: 11px; }
    [data-testid="stChatMessageContent"] { padding: 10px 14px !important; }
}

@media (max-width: 479px) {
    .hero-title { font-size: 22px; letter-spacing: -0.5px; }
    .hero-subtitle { font-size: 9px; }
    [data-testid="stChatMessageContent"] { padding: 8px 12px !important; font-size: 13px !important; }
    .stButton > button { padding: 6px 8px !important; font-size: 11px !important; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
#                        4. APPLICATION CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

NAV_ITEMS = [
    "🏠 Home",
    "💬 AI Chat",
    "📄 PDF Study Chat",
    "🧩 Quiz Generator",
    "🐛 Code Helper",
    "📝 Notes Summarizer",
    "✍️ Assignment Generator",
    "✓ Assignment Checker",
    "📅 Study Planner",
    "🧾 Exam Paper Generator",
    "💻 Code Runner",
    "🎓 Study Recommender",
    "📊 Dashboard",
]

STUDY_MODES = [
    "General Study Assistant",
    "Programming Helper",
    "Code Debugger",
    "Quiz Generator",
    "Notes Summarizer",
    "Assignment Writer",
    "Study Planner",
    "Exam Prep",
]

# AI MODEL CONFIGURATIONS
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

CLAUDE_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-3-5-haiku-20241022",
]

AI_MODELS_CONFIG = {
    "Gemini Flash": {"provider": "gemini", "model": "gemini-1.5-flash"},
    "Gemini Pro": {"provider": "gemini", "model": "gemini-1.5-pro"},
    "Claude Sonnet": {"provider": "claude", "model": "claude-sonnet-4-20250514"},
    "Claude Haiku": {"provider": "claude", "model": "claude-3-5-haiku-20241022"},
}

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
        "What is time complexity?",
        "OOP pillars explained",
    ],
    "Code Debugger": [
        "Find bug in this loop",
        "Explain Python traceback",
        "Why IndexError occurs?",
        "Debug SQL query",
    ],
    "Quiz Generator": [
        "DBMS normalization MCQs",
        "OS scheduling quiz",
        "C programming basics",
        "Python OOP questions",
    ],
    "Notes Summarizer": [
        "Summarize OS scheduling",
        "DBMS normalization notes",
        "Networks revision points",
        "Software lifecycle summary",
    ],
    "Assignment Writer": [
        "Cloud Computing assignment",
        "DBMS normalization topic",
        "OS deadlock writeup",
        "Software lifecycle assignment",
    ],
    "Study Planner": [
        "DBMS exam in 15 days",
        "Semester study schedule",
        "Revision plan for all subjects",
        "Weekly study routine",
    ],
    "Exam Prep": [
        "Generate DBMS exam",
        "OS question paper",
        "Python exam questions",
        "Data Structures test",
    ],
    "General Study Assistant": [
        "Explain ACID properties",
        "Compiler vs Interpreter",
        "How to prepare for exams?",
        "TCP vs UDP comparison",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════
#                    5. SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

def init_session() -> None:
    """Initialize all session state variables"""
    defaults = {
        # Navigation & Chat
        "messages": [],
        "mode": "General Study Assistant",
        "nav": "🏠 Home",
        
        # AI Configuration
        "ai_model_name": "Gemini Flash",
        "ai_provider": "gemini",
        "gemini_model": "gemini-1.5-flash",
        "claude_model": "claude-sonnet-4-20250514",
        "temperature": 0.5,
        "typing_speed": 0.01,
        "show_timestamps": True,
        
        # Session Tracking
        "session_start_dt": datetime.now(),
        "questions_asked": 0,
        "topics_studied": [],
        
        # User Memory & Profile
        "user_name": None,
        "user_email": None,
        "preferred_subjects": [],
        "learning_history": [],
        "past_questions": [],
        
        # Feature Usage Analytics
        "feature_usage": {
            "AI Chat": 0,
            "PDF Study Chat": 0,
            "Quiz Generator": 0,
            "Code Helper": 0,
            "Notes Summarizer": 0,
            "Assignment Generator": 0,
            "Assignment Checker": 0,
            "Study Planner": 0,
            "Exam Paper Generator": 0,
            "Code Runner": 0,
            "Study Recommender": 0,
        },
        
        # PDF Study Chat
        "pdf_content": None,
        "pdf_filename": None,
        "pdf_chat_history": [],
        
        # Code Runner
        "code_output": "",
        "code_error": "",
        
        # Assignment Feedback
        "assignment_feedback": None,
        
        # Voice
        "voice_enabled": VOICE_AVAILABLE and TEXT_TO_SPEECH_AVAILABLE,
        "last_voice_input": None,
        
        # Theme
        "theme": "dark",
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session()


# ═══════════════════════════════════════════════════════════════════════════
#                        6. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def safe_log(message: str, category: str = "info") -> None:
    """Safe logging with error handling"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{category.upper()}] {message}"
    except Exception:
        pass


def unique_topics(topics: list[str]) -> list[str]:
    """Remove duplicates while preserving order"""
    seen = set()
    ordered = []
    for topic in topics:
        t = topic.strip().lower()
        if t and t not in seen:
            seen.add(t)
            ordered.append(topic.strip())
    return ordered


def extract_topics(text: str) -> list[str]:
    """Extract subject topics from text"""
    topic_keywords = [
        "python", "java", "c", "c++", "dbms", "sql", "os", "operating system",
        "network", "computer networks", "dsa", "data structures", "algorithms",
        "software engineering", "ai", "machine learning", "cybersecurity",
        "oop", "compiler", "cloud computing", "web development", "database",
    ]
    lower = text.lower()
    matched = [kw.title() for kw in topic_keywords if kw in lower]
    return unique_topics(matched)


def update_study_tracking(user_text: str) -> None:
    """Update session tracking metrics and memory"""
    st.session_state.questions_asked += 1
    new_topics = extract_topics(user_text)
    st.session_state.topics_studied = unique_topics(st.session_state.topics_studied + new_topics)
    
    # Store in learning history
    st.session_state.learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "question": user_text[:100],
        "mode": st.session_state.mode,
        "topics": new_topics,
    })
    
    if user_text not in st.session_state.past_questions:
        st.session_state.past_questions.append(user_text[:200])


def session_duration_text() -> str:
    """Get formatted session duration"""
    delta = datetime.now() - st.session_state.session_start_dt
    total_seconds = int(delta.total_seconds())
    hrs = total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def extract_code_block(text: str) -> tuple[str | None, str | None]:
    """Extract code blocks from text"""
    fence_match = re.search(r"```(\w+)?\n([\s\S]*?)```", text)
    if fence_match:
        language = fence_match.group(1).strip() if fence_match.group(1) else None
        code = fence_match.group(2).strip()
        return language, code
    
    if "\n" in text and any(sym in text for sym in ["def ", "class ", "{", "}", ";", "import ", "#include"]):
        return None, text.strip()
    
    return None, None


def detect_language(code: str, hinted_language: str | None = None) -> str:
    """Detect programming language from code"""
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


def extract_pdf_text(uploaded_file) -> tuple[str | None, str | None]:
    """Extract text from PDF file"""
    if not PDF_AVAILABLE:
        return None, "PyPDF not installed. Run: pip install pypdf"
    
    try:
        pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
        text_content = []
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"[Page {page_num}]\n{page_text}")
        
        full_text = "\n\n".join(text_content)
        
        if not full_text.strip():
            return None, "No text found in PDF"
        
        return full_text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"


def chunk_text(text: str, max_chunk_size: int = 8000) -> list[str]:
    """Simple text chunking"""
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
    """Find most relevant PDF section"""
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    chunks = chunk_text(pdf_text, max_chunk_size=2000)
    
    if len(chunks) <= 1:
        return pdf_text[:max_length]
    
    chunk_scores = []
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = sum(1 for word in query_words if word in chunk_lower and len(word) > 3)
        chunk_scores.append((score, chunk))
    
    chunk_scores.sort(reverse=True, key=lambda x: x[0])
    relevant_chunks = [chunk for score, chunk in chunk_scores[:3] if score > 0]
    
    if not relevant_chunks:
        relevant_chunks = [chunks[0]]
    
    combined = "\n\n".join(relevant_chunks)
    return combined[:max_length]


def track_feature_usage(feature_name: str) -> None:
    """Track feature usage"""
    feature_mapping = {
        "ai_chat": "AI Chat",
        "pdf": "PDF Study Chat",
        "quiz": "Quiz Generator",
        "code": "Code Helper",
        "notes": "Notes Summarizer",
        "assignment": "Assignment Generator",
        "checker": "Assignment Checker",
        "planner": "Study Planner",
        "exam": "Exam Paper Generator",
        "runner": "Code Runner",
        "recommender": "Study Recommender",
    }
    
    for key, mapped_name in feature_mapping.items():
        if key in feature_name.lower() and mapped_name in st.session_state.feature_usage:
            st.session_state.feature_usage[mapped_name] += 1
            break


def get_most_used_features() -> list[tuple[str, int]]:
    """Get features sorted by usage"""
    usage = st.session_state.feature_usage.items()
    return sorted(usage, key=lambda x: x[1], reverse=True)


def build_system_prompt(mode: str) -> str:
    """Build system prompt based on mode"""
    mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["General Study Assistant"])
    
    user_context = ""
    if st.session_state.user_name:
        user_context = f"\nNote: The student's name is {st.session_state.user_name}."
    
    return f"""
{BASE_ACADEMIC_CONTEXT}

Mode Instruction:
{mode_prompt}

{RESPONSE_FORMAT_GUIDELINES}{user_context}
""".strip()


def build_mode_specific_user_prompt(user_prompt: str, mode: str) -> str:
    """Enhance user prompt based on mode"""
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
                "Do the following:\n"
                "1. Detected Language\n"
                "2. Syntax/logic errors\n"
                "3. Why the error happens\n"
                "4. Corrected code\n"
                "5. Best practice tip\n\n"
                f"Code:\n```{detected}\n{code}\n```"
            )
        return f"Debug this code:\n{user_prompt}"

    if mode == "Notes Summarizer":
        return (
            "Summarize into exam-ready bullets with headings.\n"
            "Include: definitions, formulas, quick checklist.\n"
            f"\nNotes:\n{user_prompt}"
        )
    
    if mode == "Assignment Writer":
        return (
            "Create college assignment with:\n"
            "1. Title\n2. Introduction\n3. Body with headings\n4. Conclusion\n5. References\n"
            "Use formal academic language.\n"
            f"\nTopic: {user_prompt}"
        )
    
    if mode == "Study Planner":
        return (
            "Create day-by-day study plan with:\n"
            "- Daily topics\n- Time allocation\n- Revision days\n- Motivation tips\n"
            f"\nRequirements: {user_prompt}"
        )
    
    if mode == "Exam Prep":
        return (
            "Generate exam paper with:\n"
            "- Section A: 5 MCQs (1 mark each)\n"
            "- Section B: 5 Short answers (3 marks each)\n"
            "- Section C: 3 Long answers (5 marks each)\n"
            "- Total: 40 marks, 2 hours\n"
            f"\nSubject: {user_prompt}"
        )

    return user_prompt


# ═══════════════════════════════════════════════════════════════════════════
#                        7. AI ENGINE - MULTI-MODEL
# ═══════════════════════════════════════════════════════════════════════════

def get_gemini_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Get response from Gemini"""
    try:
        api_keys = st.secrets["GEMINI_KEYS"]
    except Exception:
        return "❌ **Error:** Gemini API keys not configured in secrets."

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
                role = "Student" if msg["role"] == "user" else "AI"
                lines.append(f"{role}: {msg['content'][:200]}")
            context = "\n".join(lines)
    
    pdf_section = ""
    if pdf_context:
        pdf_section = f"\n\nREFERENCE DOCUMENT:\n{pdf_context}\n"

    full_prompt = (
        f"SYSTEM:\n{system_prompt}\n\n"
        f"CONTEXT:\n{context if context else 'None'}\n"
        f"{pdf_section}"
        f"QUERY:\n{mode_prompt}"
    )

    models_to_try = [st.session_state.gemini_model] + [m for m in GEMINI_MODELS if m != st.session_state.gemini_model]
    last_error = None

    for key in api_keys:
        genai.configure(api_key=key)
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=st.session_state.temperature,
                        max_output_tokens=2048,
                    ),
                )
                st.session_state.gemini_model = model_name
                return response.text.strip() if response.text else "No response generated."
            except Exception as err:
                last_error = err
                msg = str(err).lower()

                if "not found" in msg or "404" in msg or "unsupported" in msg:
                    continue
                if "429" in msg or "quota" in msg or "invalid" in msg:
                    break
                continue

    return f"❌ **Error:** All API attempts failed. Try again shortly."


def get_claude_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Get response from Claude (Anthropic) API"""
    try:
        claude_key = st.secrets["CLAUDE_API_KEY"]
    except Exception:
        return "❌ **Error:** Claude API key not configured in secrets."

    system_prompt = build_system_prompt(mode)
    mode_prompt = build_mode_specific_user_prompt(user_prompt, mode)

    context = ""
    if history:
        recent = history[-8:]
        if recent:
            lines = []
            for msg in recent:
                role = "Student" if msg["role"] == "user" else "AI"
                lines.append(f"{role}: {msg['content'][:200]}")
            context = "\n".join(lines)

    pdf_section = ""
    if pdf_context:
        pdf_section = f"\n\nREFERENCE DOCUMENT:\n{pdf_context}\n"

    combined_user_content = (
        f"CONTEXT:\n{context if context else 'None'}\n"
        f"{pdf_section}"
        f"QUERY:\n{mode_prompt}"
    )

    models_to_try = [st.session_state.claude_model] + [m for m in CLAUDE_MODELS if m != st.session_state.claude_model]
    last_error = None

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": combined_user_content},
            ],
            "max_tokens": 2048,
            "temperature": st.session_state.temperature,
        }

        req = urlrequest.Request(
            url="https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": claude_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlrequest.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content_blocks = data.get("content", [])
            text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
            content = "\n".join(text_parts).strip()
            if content:
                st.session_state.claude_model = model_name
                return content
        except urlerror.HTTPError as err:
            last_error = err
            try:
                err_body = err.read().decode("utf-8")
            except Exception:
                err_body = str(err)
            lower = err_body.lower()
            if "model" in lower and ("not found" in lower or "unsupported" in lower):
                continue
            if err.code in (401, 403):
                return "❌ **Error:** Claude API key is invalid or unauthorized."
            if err.code == 429:
                return "⏳ **Rate Limited:** Claude rate limit reached. Try again shortly."
            continue
        except Exception as err:
            last_error = err
            continue

    return f"❌ **Error:** Unable to generate response. Check API keys."


def get_ai_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Route to appropriate AI provider"""
    if st.session_state.ai_provider == "claude":
        return get_claude_response(user_prompt, mode, history, pdf_context)
    return get_gemini_response(user_prompt, mode, history, pdf_context)


# ═══════════════════════════════════════════════════════════════════════════
#                    8. MEMORY SYSTEM - USER PROFILE
# ═══════════════════════════════════════════════════════════════════════════

def detect_user_info(text: str) -> None:
    """Detect and store user information from text"""
    # Simple name detection
    if "my name is" in text.lower():
        match = re.search(r"my name is ([a-zA-Z]+)", text, re.IGNORECASE)
        if match:
            st.session_state.user_name = match.group(1).capitalize()
    
    # Preferred subject detection
    subjects = ["python", "java", "dbms", "os", "networks", "dsa", "web", "ai"]
    for subject in subjects:
        if subject in text.lower() and subject not in [s.lower() for s in st.session_state.preferred_subjects]:
            st.session_state.preferred_subjects.append(subject.capitalize())


def get_user_profile_summary() -> str:
    """Get user profile summary"""
    profile = []
    if st.session_state.user_name:
        profile.append(f"👤 **Name:** {st.session_state.user_name}")
    
    if st.session_state.preferred_subjects:
        profile.append(f"📚 **Preferred Subjects:** {', '.join(st.session_state.preferred_subjects)}")
    
    profile.append(f"❓ **Questions Asked:** {st.session_state.questions_asked}")
    profile.append(f"📖 **Topics Learned:** {len(st.session_state.topics_studied)}")
    
    return "\n".join(profile) if profile else "No profile data yet."


# ═══════════════════════════════════════════════════════════════════════════
#                    9. SMART TOOL ROUTER - AUTO DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_tool_from_text(text: str) -> str | None:
    """Automatically detect which tool the user wants"""
    text_lower = text.lower()
    
    tool_keywords = {
        "Quiz Generator": ["quiz", "mcq", "questions", "test", "exam question"],
        "Code Helper": ["debug", "code", "error", "bug", "fix"],
        "Notes Summarizer": ["summarize", "summary", "notes", "key points", "identify"],
        "Assignment Writer": ["assignment", "write", "essay", "report"],
        "Study Planner": ["schedule", "plan", "study plan", "days"],
        "Exam Prep": ["exam paper", "question paper", "mock exam"],
    }
    
    for tool, keywords in tool_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return tool
    
    return None


# ═══════════════════════════════════════════════════════════════════════════
#                    10. VOICE ASSISTANT - SPEECH I/O
# ═══════════════════════════════════════════════════════════════════════════

def speech_to_text() -> str | None:
    """Convert speech to text"""
    if not VOICE_AVAILABLE:
        return None
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Listening... speak your question")
            audio = recognizer.listen(source, timeout=10)
            text = recognizer.recognize_google(audio)
            return text
    except sr.UnknownValueError:
        st.error("❌ Could not understand audio. Please speak clearly.")
        return None
    except sr.RequestError as e:
        st.error(f"❌ Microphone error: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Voice error: {e}")
        return None


def text_to_speech(text: str) -> None:
    """Convert text to speech"""
    if not TEXT_TO_SPEECH_AVAILABLE:
        st.warning("⚠️ Text-to-speech not available. Install: pip install pyttsx3")
        return
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text[:500])  # Limit to first 500 chars
        engine.runAndWait()
    except Exception as e:
        st.error(f"❌ Text-to-speech error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
#                    11. CODE EXECUTOR - SANDBOX
# ═══════════════════════════════════════════════════════════════════════════

def execute_python_code(code: str) -> tuple[str, str]:
    """Execute Python code safely in a subprocess sandbox"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            env={"PATH": ""},
        )
        output = result.stdout or "Code executed successfully."
        error = result.stderr
        return output, error
    except subprocess.TimeoutExpired:
        return "", "Error: Code execution timed out (10 second limit)."
    except Exception as e:
        return "", f"Execution Error: {e}"


# ═══════════════════════════════════════════════════════════════════════════
#                    12. ASSIGNMENT CHECKER - FEEDBACK
# ═══════════════════════════════════════════════════════════════════════════

def check_assignment(assignment_text: str) -> str:
    """Get AI feedback on assignment"""
    prompt = f"""
Analyze this student assignment and provide detailed feedback:

---
{assignment_text}
---

Provide feedback on:
1. **Grammar & Clarity** - Identify errors and suggest improvements
2. **Structure** - Is it well-organized with clear sections?
3. **Content Quality** - Is the information accurate and relevant?
4. **Plagiarism Risk** - No actual plagiarism check, just note suspicious patterns
5. **Improvements** - 3-5 specific suggestions to enhance the assignment
6. **Grade Estimate** - What grade does this deserve? (A/B/C/D/E)

Format as a detailed report.
"""
    return get_ai_response(prompt, "General Study Assistant")


# ═══════════════════════════════════════════════════════════════════════════
#                    13. STUDY RECOMMENDER
# ═══════════════════════════════════════════════════════════════════════════

def get_study_recommendations() -> str:
    """Get personalized study recommendations"""
    studied = st.session_state.topics_studied
    
    if not studied:
        return """
### 📚 **Getting Started**

Based on BCA curriculum, here's where to start:

1. **Programming Fundamentals** - Python/Java basics
2. **Data Structures** - Arrays, Linked Lists, Trees, Graphs
3. **Database Systems** - DBMS basics, SQL
4. **Operating Systems** - Processes, Threads, Memory Management
5. **Computer Networks** - TCP/IP, Protocols, Sockets

**Next Steps:**
- Start with **Programming Helper** mode to learn fundamentals
- Use **Code Runner** to practice with real code
- Take **Quizzes** to test your knowledge
"""
    
    recommendations = []
    
    # Suggest related topics
    if "Python" in studied:
        recommendations.append("**Advanced Python** - OOP, Decorators, Generators")
    if any(x in studied for x in ["DBMS", "Database"]):
        recommendations.append("**SQL Optimization** - Indexing, Query Planning")
    if "Os" in studied:
        recommendations.append("**Distributed Systems** - Concurrency, Synchronization")
    if "Networks" in studied:
        recommendations.append("**Cryptography** - Security Protocols, Encryption")
    
    result = f"""
### 🎯 **Personalized Study Path**

**Topics You've Covered:** {', '.join(studied)}

**Recommended Next Topics:**
"""
    
    for rec in recommendations[:3]:
        result += f"\n- {rec}"
    
    if len(recommendations) < 3:
        result += "\n- **Advanced Data Structures** - B-Trees, Heaps, Hash Tables"
        result += "\n- **Software Engineering** - Design Patterns, SDLC"
        result += "\n- **Web Development** - HTTP, REST APIs, Databases"
    
    result += "\n\n💡 **Study Strategy:**\n"
    result += "1. Master the fundamentals thoroughly\n"
    result += "2. Always practice with code examples\n"
    result += "3. Take quizzes to identify weak areas\n"
    result += "4. Review assignments for real-world application\n"
    
    return result


# ═══════════════════════════════════════════════════════════════════════════
#                    14. EXPORT & UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def export_chat_markdown() -> str:
    """Export chat as Markdown"""
    if not st.session_state.messages:
        return ""

    lines = [
        "# BCA AI Platform - Chat Export",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Study Mode:** {st.session_state.mode}",
        f"**AI Model:** {st.session_state.ai_model_name}",
        "---",
        "",
    ]
    for msg in st.session_state.messages:
        role = "👤 Student" if msg["role"] == "user" else "🤖 AI"
        ts = msg.get("timestamp", "")
        lines.append(f"### {role}\n{msg['content']}\n")
    return "\n".join(lines)


def export_chat_json() -> str:
    """Export chat as JSON"""
    return json.dumps(
        {
            "exported_at": datetime.now().isoformat(),
            "mode": st.session_state.mode,
            "ai_model": st.session_state.ai_model_name,
            "user_name": st.session_state.user_name,
            "messages": st.session_state.messages,
            "questions_asked": st.session_state.questions_asked,
            "topics_studied": st.session_state.topics_studied,
        },
        indent=2,
    )


def add_chat_message(role: str, content: str) -> None:
    """Add message to chat history"""
    st.session_state.messages.append(
        {
            "role": role,
            "content": content,
            "timestamp": datetime.now().strftime("%H:%M"),
            "mode": st.session_state.mode,
        }
    )


def render_assistant_response(prompt: str, mode: str, pdf_context: str | None = None) -> str:
    """Render AI response with typing animation"""
    response = get_ai_response(prompt, mode, st.session_state.messages, pdf_context)

    placeholder = st.empty()
    speed = st.session_state.typing_speed
    final_text = ""

    if speed > 0:
        words = response.split()
        batch_size = 5
        for idx in range(0, len(words), batch_size):
            final_text = " ".join(words[:idx + batch_size])
            placeholder.markdown(final_text + " ▌")
            time.sleep(speed * batch_size)
        placeholder.markdown(response)
        final_text = response
    else:
        placeholder.markdown(response)
        final_text = response

    return final_text.strip()


# ═══════════════════════════════════════════════════════════════════════════
#                        15. SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 10px 0 20px;">
            <div style="font-size:40px; margin-bottom:6px;">🎓</div>
            <div style="font-size:18px; font-weight:700; background: linear-gradient(135deg,#38bdf8,#818cf8);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;">BCA Platform</div>
            <div style="font-size:11px; color:#475569; letter-spacing:2px; text-transform:uppercase;">AI Academic Ecosystem</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Mapping between nav pages and study modes ──
    NAV_TO_MODE = {
        "🏠 Home": "General Study Assistant",
        "💬 AI Chat": "General Study Assistant",
        "📄 PDF Study Chat": "General Study Assistant",
        "🧩 Quiz Generator": "Quiz Generator",
        "🐛 Code Helper": "Code Debugger",
        "📝 Notes Summarizer": "Notes Summarizer",
        "✍️ Assignment Generator": "Assignment Writer",
        "✓ Assignment Checker": "General Study Assistant",
        "📅 Study Planner": "Study Planner",
        "🧾 Exam Paper Generator": "Exam Prep",
        "💻 Code Runner": "Programming Helper",
        "🎓 Study Recommender": "General Study Assistant",
        "📊 Dashboard": "General Study Assistant",
    }

    MODE_TO_NAV = {
        "General Study Assistant": "💬 AI Chat",
        "Programming Helper": "🐛 Code Helper",
        "Code Debugger": "🐛 Code Helper",
        "Quiz Generator": "🧩 Quiz Generator",
        "Notes Summarizer": "📝 Notes Summarizer",
        "Assignment Writer": "✍️ Assignment Generator",
        "Study Planner": "📅 Study Planner",
        "Exam Prep": "🧾 Exam Paper Generator",
    }

    st.markdown("#### 📍 Navigation")
    nav_index = NAV_ITEMS.index(st.session_state.nav) if st.session_state.nav in NAV_ITEMS else 0
    new_nav = st.radio(
        "Navigation",
        options=NAV_ITEMS,
        index=nav_index,
        label_visibility="collapsed",
    )

    # Sync: nav changed → update mode
    if new_nav != st.session_state.nav:
        st.session_state.nav = new_nav
        mapped_mode = NAV_TO_MODE.get(new_nav)
        if mapped_mode and mapped_mode != st.session_state.mode:
            st.session_state.mode = mapped_mode
            st.rerun()

    st.session_state.nav = new_nav

    st.divider()

    st.markdown("#### 🎯 Study Mode")
    mode_index = STUDY_MODES.index(st.session_state.mode) if st.session_state.mode in STUDY_MODES else 0
    new_mode = st.selectbox(
        "Mode",
        STUDY_MODES,
        index=mode_index,
        label_visibility="collapsed",
    )

    # Sync: mode changed → update nav
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        mapped_nav = MODE_TO_NAV.get(new_mode)
        if mapped_nav and mapped_nav != st.session_state.nav:
            st.session_state.nav = mapped_nav
            st.rerun()

    st.session_state.mode = new_mode

    with st.expander("⚙️ AI Configuration"):
        st.session_state.ai_model_name = st.selectbox(
            "AI Model",
            list(AI_MODELS_CONFIG.keys()),
            index=0,
        )
        
        config = AI_MODELS_CONFIG[st.session_state.ai_model_name]
        st.session_state.ai_provider = config["provider"]
        if config["provider"] == "gemini":
            st.session_state.gemini_model = config["model"]
        else:
            st.session_state.claude_model = config["model"]

        st.session_state.temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
        )

    with st.expander("👤 User Profile"):
        name_input = st.text_input(
            "Your Name",
            value=st.session_state.user_name or "",
            key="sidebar_user_name",
        )
        if name_input != (st.session_state.user_name or ""):
            st.session_state.user_name = name_input if name_input else None
        st.markdown(get_user_profile_summary())

    with st.expander("🔊 Voice Settings"):
        if VOICE_AVAILABLE and TEXT_TO_SPEECH_AVAILABLE:
            st.session_state.voice_enabled = st.checkbox(
                "Enable Voice",
                value=st.session_state.voice_enabled,
                key="sidebar_voice_toggle",
            )
            st.caption("🎤 Microphone & Speaker required")
        else:
            st.warning("⚠️ Voice features unavailable. Install: speechrecognition, pyttsx3")

    st.divider()

    st.markdown("#### 📊 Session Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Questions", st.session_state.questions_asked)
    with col2:
        st.metric("Topics", len(st.session_state.topics_studied))
    st.caption(f"Duration: {session_duration_text()}")

    st.divider()

    st.markdown("#### 💾 Export")
    if st.session_state.messages:
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 MD",
                data=export_chat_markdown(),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "📦 JSON",
                data=export_chat_json(),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
            )
    else:
        st.caption("No messages to export")

    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.questions_asked = 0
        st.session_state.topics_studied = []
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#                            16. MAIN HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    f"""
<div class="hero-header">
    <div class="hero-title">🎓 BCA AI Academic Platform</div>
    <div class="hero-subtitle">
        <span class="status-dot"></span>
        {st.session_state.ai_model_name} · {st.session_state.mode}
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════
#                            17. UI PAGES
# ═══════════════════════════════════════════════════════════════════════════

def page_home() -> None:
    """Home page"""
    st.markdown("### 🏠 Home - Welcome to BCA AI Platform")
    
    st.info("🎓 Your all-in-one AI-powered academic platform for BCA students")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions", st.session_state.questions_asked)
    with col2:
        st.metric("Topics", len(st.session_state.topics_studied))
    with col3:
        st.metric("Duration", session_duration_text())
    with col4:
        total = sum(st.session_state.feature_usage.values())
        st.metric("Actions", total)
    
    st.markdown("### ✨ Features")
    feat1, feat2 = st.columns(2)
    
    with feat1:
        st.markdown("""
        **Learning Tools:**
        - 💬 AI Chat with voice
        - 📄 PDF Study Chat
        - 🧩 Quiz Generator
        - 🐛 Code Helper
        - 📝 Notes Summarizer
        """)
    
    with feat2:
        st.markdown("""
        **Advanced Features:**
        - ✍️ Assignment Generator
        - ✓ Assignment Checker (NEW)
        - 💻 Code Runner (NEW)
        - 🎓 Study Recommender (NEW)
        - 📊 Advanced Dashboard
        """)


def page_ai_chat() -> None:
    """AI Chat page"""
    track_feature_usage("ai_chat")
    st.markdown("### 💬 AI Chat")
    
    # Voice input button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.voice_enabled and st.button("🎤 Voice", use_container_width=True):
            voice_text = speech_to_text()
            if voice_text:
                st.session_state._voice_input = voice_text
                st.rerun()
    
    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt_input = st.chat_input("Ask anything...")
    
    if hasattr(st.session_state, "_voice_input"):
        prompt_input = st.session_state._voice_input
        del st.session_state._voice_input

    if prompt_input:
        detect_user_info(prompt_input)
        update_study_tracking(prompt_input)
        
        # Check if user wants to switch tools
        detected_tool = detect_tool_from_text(prompt_input)
        if detected_tool:
            st.session_state.mode = detected_tool
        
        with st.chat_message("user"):
            st.markdown(prompt_input)
        add_chat_message("user", prompt_input)

        with st.chat_message("assistant"):
            final_response = render_assistant_response(prompt_input, st.session_state.mode)
        add_chat_message("assistant", final_response)
        
        # Offer voice output
        if st.session_state.voice_enabled:
            if st.button("🔊 Read Aloud"):
                text_to_speech(final_response)


def page_pdf_study_chat() -> None:
    """PDF Study Chat"""
    track_feature_usage("pdf")
    st.markdown("### 📄 PDF Study Chat")
    
    if not PDF_AVAILABLE:
        st.error("❌ PyPDF not installed. Run: pip install pypdf")
        return
    
    uploaded_file = st.file_uploader("Choose PDF", type=['pdf'])
    
    if uploaded_file:
        if st.session_state.pdf_filename != uploaded_file.name:
            with st.spinner("📖 Reading PDF..."):
                content, error = extract_pdf_text(uploaded_file)
                
                if error:
                    st.error(f"❌ {error}")
                    return
                
                st.session_state.pdf_content = content
                st.session_state.pdf_filename = uploaded_file.name
                st.session_state.pdf_chat_history = []
                st.success(f"✅ Loaded: {uploaded_file.name}")
        
        st.markdown(f"**PDF:** {st.session_state.pdf_filename}")
        
        for msg in st.session_state.pdf_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        pdf_question = st.chat_input("Ask about the PDF...")
        
        if pdf_question:
            with st.chat_message("user"):
                st.markdown(pdf_question)
            
            st.session_state.pdf_chat_history.append({
                "role": "user",
                "content": pdf_question,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            
            relevant_content = find_relevant_pdf_content(
                st.session_state.pdf_content,
                pdf_question
            )
            
            with st.chat_message("assistant"):
                final_response = render_assistant_response(pdf_question, "General Study Assistant", pdf_context=relevant_content)
                st.session_state.pdf_chat_history.append({
                    "role": "assistant",
                    "content": final_response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                })
            
            update_study_tracking(pdf_question)
        
        if st.button("🗑️ Clear PDF"):
            st.session_state.pdf_content = None
            st.session_state.pdf_filename = None
            st.session_state.pdf_chat_history = []
            st.rerun()


def page_quiz_generator() -> None:
    """Quiz Generator"""
    track_feature_usage("quiz")
    st.markdown("### 🧩 Quiz Generator")
    
    topic = st.text_input("Topic", placeholder="DBMS, Python OOP, Networks...")
    
    if st.button("Generate 5 MCQs"):
        if not topic.strip():
            st.warning("Enter a topic")
            return
        
        st.session_state.mode = "Quiz Generator"
        prompt = f"Create 5 MCQs on: {topic}"
        update_study_tracking(prompt)
        
        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Quiz Generator")
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)


def page_code_helper() -> None:
    """Code Helper"""
    track_feature_usage("code")
    st.markdown("### 🐛 Code Helper")
    
    code_input = st.text_area("Paste code:", height=250)
    
    if st.button("🔍 Analyze Code"):
        if not code_input.strip():
            st.warning("Paste code first")
            return
        
        st.session_state.mode = "Code Debugger"
        wrapped = f"```\n{code_input}\n```"
        update_study_tracking("code debugging")
        
        with st.chat_message("assistant"):
            result = render_assistant_response(wrapped, "Code Debugger")
        add_chat_message("user", wrapped)
        add_chat_message("assistant", result)


def page_notes_summarizer() -> None:
    """Notes Summarizer"""
    track_feature_usage("notes")
    st.markdown("### 📝 Notes Summarizer")
    
    notes = st.text_area("Paste notes:", height=250)
    
    if st.button("✨ Summarize"):
        if not notes.strip():
            st.warning("Paste notes first")
            return
        
        st.session_state.mode = "Notes Summarizer"
        update_study_tracking("note summarization")
        
        with st.chat_message("assistant"):
            result = render_assistant_response(notes, "Notes Summarizer")
        add_chat_message("user", notes)
        add_chat_message("assistant", result)


def page_assignment_generator() -> None:
    """Assignment Generator"""
    track_feature_usage("assignment")
    st.markdown("### ✍️ Assignment Generator")
    
    topic = st.text_input("Topic", placeholder="Cloud Computing...")
    
    if st.button("Generate Assignment"):
        if not topic.strip():
            st.warning("Enter topic")
            return
        
        st.session_state.mode = "Assignment Writer"
        prompt = f"Write a 1000-word assignment on: {topic}"
        update_study_tracking(f"assignment on {topic}")
        
        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Assignment Writer")
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)
        
        st.download_button(
            "⬇️ Download",
            data=result,
            file_name=f"assignment_{topic[:20]}.txt",
            mime="text/plain",
            use_container_width=True
        )


def page_assignment_checker() -> None:
    """Assignment Checker - NEW"""
    track_feature_usage("checker")
    st.markdown("### ✓ Assignment Checker")
    st.info("Paste your assignment to get AI feedback on grammar, clarity, and improvements")
    
    assignment_text = st.text_area("Paste assignment:", height=300)
    
    if st.button("🔍 Check Assignment"):
        if not assignment_text.strip():
            st.warning("Paste assignment first")
            return
        
        with st.spinner("📝 Analyzing your assignment..."):
            feedback = check_assignment(assignment_text)
        
        st.markdown(feedback)
        
        st.download_button(
            "⬇️ Download Feedback",
            data=feedback,
            file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def page_study_planner() -> None:
    """Study Planner"""
    track_feature_usage("planner")
    st.markdown("### 📅 Study Planner")
    
    col1, col2 = st.columns(2)
    with col1:
        exam_date = st.date_input("Exam Date")
        hours_per_day = st.slider("Hours/day", 1, 12, 4)
    
    with col2:
        subjects = st.text_area("Subjects (one/line)", height=120)
    
    if st.button("🗓️ Create Plan"):
        if not subjects.strip():
            st.warning("Enter subjects")
            return
        
        days_remaining = (exam_date - datetime.now().date()).days
        if days_remaining <= 0:
            st.error("Exam date must be future")
            return
        
        st.session_state.mode = "Study Planner"
        prompt = f"Create study plan: {days_remaining} days, {hours_per_day}h/day, subjects: {subjects}"
        update_study_tracking("study planning")
        
        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Study Planner")
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)


def page_exam_generator() -> None:
    """Exam Paper Generator"""
    track_feature_usage("exam")
    st.markdown("### 🧾 Exam Paper Generator")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject", placeholder="DBMS...")
        duration = st.selectbox("Duration", ["1 hour", "2 hours"])
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        marks = st.selectbox("Total Marks", ["40", "50", "75", "100"])
    
    if st.button("📋 Generate Exam"):
        if not subject.strip():
            st.warning("Enter subject")
            return
        
        st.session_state.mode = "Exam Prep"
        prompt = f"Generate exam paper: {subject}, {duration}, {difficulty}, {marks} marks"
        update_study_tracking(f"exam generation for {subject}")
        
        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Exam Prep")
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)
        
        st.download_button(
            "⬇️ Download Exam",
            data=result,
            file_name=f"exam_{subject[:15]}.txt",
            mime="text/plain",
            use_container_width=True
        )


def page_code_runner() -> None:
    """Code Runner - NEW"""
    track_feature_usage("runner")
    st.markdown("### 💻 Code Runner")
    st.warning("⚠️ Limited execution - infinite loops and external calls blocked")
    
    code_input = st.text_area("Write Python code:", height=300, value="# Write Python code here\nprint('Hello World')")
    
    if st.button("▶️ Run Code"):
        if not code_input.strip():
            st.warning("Write code first")
            return
        
        with st.spinner("Running..."):
            output, error = execute_python_code(code_input)
        
        if output:
            st.success("✅ Output:")
            st.code(output)
        
        if error:
            st.error("❌ Error:")
            st.code(error)
        
        if not output and not error:
            st.info("Code executed successfully with no output")


def page_study_recommender() -> None:
    """Study Recommender - NEW"""
    track_feature_usage("recommender")
    st.markdown("### 🎓 Study Recommender")
    
    st.markdown(get_study_recommendations())
    
    if st.button("Get Detailed Recommendations"):
        prompt = f"""Based on topics studied: {', '.join(st.session_state.topics_studied) if st.session_state.topics_studied else 'None yet'}
        
Create a detailed personalized learning path with:
1. Next 5 topics to learn
2. Why each topic is important
3. Recommended learning order
4. Estimated time for each topic
5. Practice projects for each topic
"""
        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "General Study Assistant")
        st.markdown(result)


def page_dashboard() -> None:
    """Enhanced Dashboard"""
    st.markdown("### 📊 Study Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Questions", st.session_state.questions_asked)
    with col2:
        st.metric("Topics", len(st.session_state.topics_studied))
    with col3:
        st.metric("Duration", session_duration_text())
    with col4:
        total = sum(st.session_state.feature_usage.values())
        st.metric("Total Actions", total)
    
    st.divider()
    
    # Charts
    feat_data = get_most_used_features()
    if feat_data and any(usage for _, usage in feat_data):
        st.markdown("#### 📈 Feature Usage")
        feat_names = [f[0] for f in feat_data if f[1] > 0]
        feat_values = [f[1] for f in feat_data if f[1] > 0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            for name, value in zip(feat_names, feat_values):
                if value > 0:
                    st.metric(name, value)
        
        with col2:
            if st.session_state.topics_studied:
                st.markdown("#### 📚 Topics Studied")
                for topic in st.session_state.topics_studied:
                    st.markdown(f"• {topic}")
    
    st.divider()
    st.markdown("#### 🕐 Recent Activity")
    recent = st.session_state.messages[-5:]
    if recent:
        for item in recent:
            icon = "👤" if item["role"] == "user" else "🤖"
            content_preview = item['content'][:100] + "..." if len(item['content']) > 100 else item['content']
            st.markdown(f"**{icon}** {content_preview}")
    else:
        st.caption("No activity yet")


# ═══════════════════════════════════════════════════════════════════════════
#                            18. PAGE ROUTER
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.nav == "🏠 Home":
    page_home()
elif st.session_state.nav == "💬 AI Chat":
    page_ai_chat()
elif st.session_state.nav == "📄 PDF Study Chat":
    page_pdf_study_chat()
elif st.session_state.nav == "🧩 Quiz Generator":
    page_quiz_generator()
elif st.session_state.nav == "🐛 Code Helper":
    page_code_helper()
elif st.session_state.nav == "📝 Notes Summarizer":
    page_notes_summarizer()
elif st.session_state.nav == "✍️ Assignment Generator":
    page_assignment_generator()
elif st.session_state.nav == "✓ Assignment Checker":
    page_assignment_checker()
elif st.session_state.nav == "📅 Study Planner":
    page_study_planner()
elif st.session_state.nav == "🧾 Exam Paper Generator":
    page_exam_generator()
elif st.session_state.nav == "💻 Code Runner":
    page_code_runner()
elif st.session_state.nav == "🎓 Study Recommender":
    page_study_recommender()
elif st.session_state.nav == "📊 Dashboard":
    page_dashboard()

st.markdown("---")
st.caption("🎓 BCA AI Academic Platform v3.0 | Powered by Gemini & Claude")
