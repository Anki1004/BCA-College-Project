"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     BCA AI STUDY ASSISTANT                                ║
║                  Advanced AI Learning Platform                            ║
║              Powered by Google Gemini API                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

Author: BCA AI Team
Version: 2.0 - Enhanced Edition
Date: March 2026

Features:
- AI Chat with Smart Prompts
- PDF Study Chat
- Quiz Generator
- Code Helper/Debugger
- Notes Summarizer
- Assignment Generator
- Study Planner
- Exam Paper Generator
- Dashboard with Analytics
- Responsive Design (Mobile/Tablet/Desktop)
"""

import json
import re
import time
import warnings
from datetime import datetime, timedelta
from io import BytesIO
from urllib import error as urlerror
from urllib import request as urlrequest

# Suppress deprecation warning for google.generativeai
warnings.filterwarnings('ignore', category=FutureWarning, module='google.generativeai')

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

GEMINI_MODEL_OPTIONS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
]

GROQ_MODEL_OPTIONS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
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
        "ai_provider": "Gemini",
        "model": GEMINI_MODEL_OPTIONS[0],
        "groq_model": GROQ_MODEL_OPTIONS[0],
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
    """Update session tracking metrics"""
    st.session_state.questions_asked += 1
    new_topics = extract_topics(user_text)
    st.session_state.topics_studied = unique_topics(st.session_state.topics_studied + new_topics)


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
    relevant_chunks = [chunk for score, chunk in chunk_scores[:3] if score > 0]
    
    if not relevant_chunks:
        relevant_chunks = [chunks[0]]
    
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


def build_system_prompt(mode: str) -> str:
    """Build system prompt based on mode"""
    mode_prompt = MODE_PROMPTS.get(mode, MODE_PROMPTS["General Study Assistant"])
    return f"""
{BASE_ACADEMIC_CONTEXT}

Mode Instruction:
{mode_prompt}

{RESPONSE_FORMAT_GUIDELINES}
""".strip()


def build_mode_specific_user_prompt(user_prompt: str, mode: str) -> str:
    """Enhance user prompt based on study mode"""
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
    
    if mode == "Assignment Writer":
        return (
            "Create a well-structured college assignment on the given topic.\n"
            "Include:\n"
            "1. Title\n"
            "2. Introduction (brief overview)\n"
            "3. Main body with clear headings and subheadings\n"
            "4. (conclusion summary)\n"
            "5. References (suggest 3-4 reference sources)\n"
            "Use formal academic language suitable for BCA students.\n"
            f"\nAssignment Topic: {user_prompt}"
        )
    
    if mode == "Study Planner":
        return (
            "Create a realistic day-by-day study plan based on the student's requirements.\n"
            "Include:\n"
            "- Daily topics to cover\n"
            "- Time allocation suggestions\n"
            "- Revision days\n"
            "- Exam preparation strategy\n"
            "- Motivational tips\n"
            f"\nStudent Requirements: {user_prompt}"
        )
    
    if mode == "Exam Prep":
        return (
            "Generate a realistic university exam paper format for BCA students.\n"
            "Include:\n"
            "- Section A: Multiple Choice Questions (5 questions, 1 mark each)\n"
            "- Section B: Short Answer Questions (5 questions, 3 marks each)\n"
            "- Section C: Long Answer Questions (3 questions, 5 marks each)\n"
            "- Total: 40 marks\n"
            "- Time: 2 hours\n"
            "Make questions exam-oriented and syllabus-based.\n"
            f"\nSubject/Topic: {user_prompt}"
        )

    return user_prompt


def get_gemini_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Get response from Gemini AI"""
    try:
        api_keys = st.secrets["GEMINI_KEYS"]
    except Exception:
        return "⚠️ API keys not found. Please configure `GEMINI_KEYS` in Streamlit secrets."

    if not isinstance(api_keys, list):
        api_keys = [api_keys]

    system_prompt = build_system_prompt(mode)
    mode_prompt = build_mode_specific_user_prompt(user_prompt, mode)

    # Build context from history
    context = ""
    if history:
        recent = history[-8:]
        if recent:
            lines = []
            for msg in recent:
                role = "Student" if msg["role"] == "user" else "Assistant"
                lines.append(f"{role}: {msg['content'][:350]}")
            context = "\n".join(lines)
    
    # Add PDF context if available
    pdf_section = ""
    if pdf_context:
        pdf_section = f"\n\nREFERENCE DOCUMENT CONTENT:\n{pdf_context}\n"

    full_prompt = (
        f"SYSTEM:\n{system_prompt}\n\n"
        f"RECENT CONTEXT:\n{context if context else 'No prior context.'}\n"
        f"{pdf_section}"
        f"STUDENT QUERY:\n{mode_prompt}"
    )

    models_to_try = [st.session_state.model] + [m for m in GEMINI_MODEL_OPTIONS if m != st.session_state.model]
    last_error = None

    # Try each API key and model fallback for better reliability.
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
                st.session_state.model = model_name
                return response.text.strip() if response.text else "No response generated."
            except Exception as err:
                last_error = err
                msg = str(err).lower()

                # Model not supported/not found: try next model.
                if "not found" in msg or "404" in msg or "unsupported" in msg:
                    continue

                # Quota/rate/API-key level issues: move to next API key.
                if "429" in msg or "quota" in msg or "invalid" in msg or "permission" in msg:
                    break

                # For other transient server issues, try next model/key fallback chain.
                continue

    if last_error:
        return f"⚠️ Error: {last_error}"
    return "🚀 All API keys are busy or exhausted. Please try again shortly."


def get_groq_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Get response from Groq API using OpenAI-compatible chat completions."""
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        return "⚠️ GROQ_API_KEY not found in Streamlit secrets."

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

    pdf_section = ""
    if pdf_context:
        pdf_section = f"\n\nREFERENCE DOCUMENT CONTENT:\n{pdf_context}\n"

    combined_user_content = (
        f"RECENT CONTEXT:\n{context if context else 'No prior context.'}\n"
        f"{pdf_section}"
        f"STUDENT QUERY:\n{mode_prompt}"
    )

    models_to_try = [st.session_state.groq_model] + [m for m in GROQ_MODEL_OPTIONS if m != st.session_state.groq_model]
    last_error = None

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": combined_user_content},
            ],
            "temperature": st.session_state.temperature,
            "max_tokens": 2048,
        }

        req = urlrequest.Request(
            url="https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlrequest.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if content:
                st.session_state.groq_model = model_name
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
                return "⚠️ Groq API key is invalid or unauthorized."
            if err.code == 429:
                return "⚠️ Groq rate limit reached. Please try again shortly."
            continue
        except Exception as err:
            last_error = err
            continue

    if last_error:
        return f"⚠️ Groq error: {last_error}"
    return "⚠️ Unable to generate response from Groq."


def get_ai_response(user_prompt: str, mode: str, history: list[dict] | None = None, pdf_context: str | None = None) -> str:
    """Route model call based on selected provider."""
    if st.session_state.get("ai_provider", "Gemini") == "Groq":
        return get_groq_response(user_prompt, mode, history, pdf_context)
    return get_gemini_response(user_prompt, mode, history, pdf_context)


def export_chat_markdown() -> str:
    """Export chat history as Markdown"""
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
    """Export chat history as JSON"""
    return json.dumps(
        {
            "exported_at": datetime.now().isoformat(),
            "mode": st.session_state.mode,
            "messages": st.session_state.messages,
            "questions_asked": st.session_state.questions_asked,
            "topics_studied": st.session_state.topics_studied,
            "feature_usage": st.session_state.feature_usage,
        },
        indent=2,
    )


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
        index=NAV_ITEMS.index(st.session_state.nav) if st.session_state.nav in NAV_ITEMS else 0,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("#### 🎯 Study Mode")
    st.session_state.mode = st.selectbox(
        "Mode",
        STUDY_MODES,
        index=STUDY_MODES.index(st.session_state.mode) if st.session_state.mode in STUDY_MODES else 0,
        label_visibility="collapsed",
    )

    st.caption("Academic context: AI Study Assistant for BCA students")

    with st.expander("⚙️ Model Settings", expanded=False):
        st.session_state.ai_provider = st.selectbox(
            "AI Provider",
            ["Gemini", "Groq"],
            index=0 if st.session_state.ai_provider == "Gemini" else 1,
        )

        if st.session_state.ai_provider == "Gemini":
            st.session_state.model = st.selectbox(
                "Gemini Model",
                GEMINI_MODEL_OPTIONS,
                index=GEMINI_MODEL_OPTIONS.index(st.session_state.model) if st.session_state.model in GEMINI_MODEL_OPTIONS else 0,
            )
        else:
            st.session_state.groq_model = st.selectbox(
                "Groq Model",
                GROQ_MODEL_OPTIONS,
                index=GROQ_MODEL_OPTIONS.index(st.session_state.groq_model) if st.session_state.groq_model in GROQ_MODEL_OPTIONS else 0,
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


# ═══════════════════════════════════════════════════════════════════════════
#                              MAIN HEADER
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
#                              HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

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
        for idx, word in enumerate(words):
            final_text += word + " "
            if idx % 3 == 0:
                placeholder.markdown(final_text + "<span class='typing-indicator'>▌</span>", unsafe_allow_html=True)
                time.sleep(speed)
        placeholder.markdown(final_text.strip())
    else:
        placeholder.markdown(response)
        final_text = response

    return final_text.strip()


# ═══════════════════════════════════════════════════════════════════════════
#                              UI PAGES
# ═══════════════════════════════════════════════════════════════════════════

def page_home() -> None:
    """Home page with overview"""
    st.markdown("### 🏠 Home")
    st.markdown(
        """
        <div style="background: rgba(56,189,248,0.05); border: 1px solid rgba(56,189,248,0.15);
             border-radius: 16px; padding: 18px; margin-bottom: 16px;">
            <div style="font-size: 16px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">
                📚 Advanced AI Learning Platform for BCA Students
            </div>
            <div style="font-size: 13px; color: #94a3b8; line-height: 1.8;">
                Your all-in-one study companion powered by Google Gemini AI. Switch between study modes 
                for tutoring, debugging, quizzes, assignments, study planning, and exam preparation.
                Upload PDFs to chat with your study materials!
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

    st.markdown("### ✨ Available Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Core Features:**
        - 💬 **AI Chat** - Interactive learning conversations
        - 📄 **PDF Study Chat** - Chat with your study materials
        - 🧩 **Quiz Generator** - Practice MCQs
        - 🐛 **Code Helper** - Debug and fix code
        """)
    
    with col2:
        st.markdown("""
        **Advanced Tools:**
        - 📝 **Assignment Generator** - Create college assignments
        - 📅 **Study Planner** - Personalized study schedules
        - 🧾 **Exam Paper Generator** - Mock exam papers
        - 📊 **Dashboard** - Track your learning progress
        """)

    st.markdown("### 🚀 Quick Start Guide")
    st.markdown("1. **Select a Study Mode** from the sidebar based on what you need help with")
    st.markdown("2. **Navigate** to the appropriate tool using the sidebar menu")
    st.markdown("3. **Start learning** - ask questions, upload PDFs, generate assignments")
    st.markdown("4. **Track your progress** in the Dashboard")


def page_ai_chat() -> None:
    """AI Chat page with smart prompts"""
    track_feature_usage("AI Chat")
    st.markdown("### 💬 AI Chat")

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


def page_pdf_study_chat() -> None:
    """PDF Study Chat - Upload and chat with PDF documents"""
    track_feature_usage("PDF Study Chat")
    st.markdown("### 📄 PDF Study Chat")
    
    if not PDF_AVAILABLE:
        st.error("📦 PyPDF library is not installed. Please run: `pip install pypdf`")
        st.info("After installing, restart the app to use PDF Study Chat feature.")
        return
    
    st.info("Upload a PDF (lecture notes, textbook chapter, etc.) and ask questions about its content.")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'], key="pdf_uploader")
    
    if uploaded_file:
        if st.session_state.pdf_filename != uploaded_file.name:
            # New PDF uploaded
            with st.spinner("📖 Reading PDF..."):
                content, error = extract_pdf_text(uploaded_file)
                
                if error:
                    st.error(f"❌ {error}")
                    return
                
                st.session_state.pdf_content = content
                st.session_state.pdf_filename = uploaded_file.name
                st.session_state.pdf_chat_history = []
                st.success(f"✅ Loaded: **{uploaded_file.name}** ({len(content)} characters)")
        
        # Show PDF info
        st.markdown(f"**Current PDF:** {st.session_state.pdf_filename}")
        st.caption(f"Content length: {len(st.session_state.pdf_content)} characters")
        
        # Display chat history
        for msg in st.session_state.pdf_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if st.session_state.show_timestamps:
                    st.caption(f"🕐 {msg.get('timestamp', '')}")
        
        # Chat input
        pdf_question = st.chat_input("Ask a question about the PDF content...")
        
        if pdf_question:
            # Display user question
            with st.chat_message("user"):
                st.markdown(pdf_question)
                if st.session_state.show_timestamps:
                    st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
            
            # Add to PDF chat history
            st.session_state.pdf_chat_history.append({
                "role": "user",
                "content": pdf_question,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            
            # Find relevant content
            with st.spinner("🔍 Searching PDF content..."):
                relevant_content = find_relevant_pdf_content(
                    st.session_state.pdf_content,
                    pdf_question
                )
            
            # Generate AI response
            with st.chat_message("assistant"):
                pdf_prompt = f"Based on the provided document content, answer this question: {pdf_question}\n\nProvide a detailed answer with references to the document."
                final_response = render_assistant_response(pdf_prompt, "General Study Assistant", pdf_context=relevant_content)
                if st.session_state.show_timestamps:
                    st.caption(f"🕐 {datetime.now().strftime('%H:%M')}")
            
            # Add to PDF chat history
            st.session_state.pdf_chat_history.append({
                "role": "assistant",
                "content": final_response,
                "timestamp": datetime.now().strftime("%H:%M"),
            })
            
            update_study_tracking(pdf_question)
        
        # Clear PDF button
        if st.button("🗑️ Clear PDF & Chat", use_container_width=True):
            st.session_state.pdf_content = None
            st.session_state.pdf_filename = None
            st.session_state.pdf_chat_history = []
            st.rerun()
    
    else:
        st.markdown("""
        **How to use:**
        1. Upload a PDF file (lecture notes, textbook, etc.)
        2. Wait for it to load
        3. Ask questions about the content
        4. Get AI-powered answers based on your document
        
        **Example questions:**
        - "Summarize the main points from page 3"
        - "What is deadlock according to this document?"
        - "Explain the algorithm mentioned in the PDF"
        """)


def page_quiz_generator() -> None:
    """Quiz Generator page"""
    track_feature_usage("Quiz Generator")
    st.markdown("### 🧩 Quiz Generator")
    st.info("Generate 5 MCQ questions with 4 options each and the correct answer for exam practice.")

    topic = st.text_input("Enter topic", placeholder="Example: DBMS normalization, Python OOP, Operating System scheduling")
    
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
    with col2:
        focus_area = st.selectbox("Focus Area", ["Theory", "Practical", "Mixed"])
    
    if st.button("Generate 5 MCQs", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter a topic first.")
            return

        st.session_state.mode = "Quiz Generator"
        prompt = f"Create {difficulty.lower()} difficulty quiz with {focus_area.lower()} focus for topic: {topic.strip()}"
        update_study_tracking(prompt)

        with st.chat_message("assistant"):
            result = render_assistant_response(prompt, "Quiz Generator")
        
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)


def page_code_helper() -> None:
    """Code Helper/Debugger page"""
    track_feature_usage("Code Helper")
    st.markdown("### 🐛 Code Helper")
    st.info("Paste your code to detect language, identify syntax issues, and get corrected code.")

    code_input = st.text_area(
        "Paste code",
        height=280,
        placeholder="Paste code here. You can use plain code or fenced blocks.",
        key="code_helper_input",
    )
    extra_context = st.text_input("Error message (optional)", placeholder="Example: IndexError: list index out of range")

    if st.button("🔍 Analyze & Debug Code", use_container_width=True):
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
    """Notes Summarizer page"""
    track_feature_usage("Notes Summarizer")
    st.markdown("### 📝 Notes Summarizer")
    st.info("Paste long academic notes and convert them into revision-focused bullet points.")

    notes = st.text_area(
        "Paste notes",
        height=300,
        placeholder="Paste lecture notes, textbook paragraphs, or your own notes...",
        key="notes_summarizer_input",
    )
    
    summary_type = st.radio(
        "Summary Style",
        ["Quick Revision", "Detailed Explanation", "Exam Focus"],
        horizontal=True
    )

    if st.button("✨ Summarize Notes", use_container_width=True):
        if not notes.strip():
            st.warning("Please paste notes first.")
            return

        st.session_state.mode = "Notes Summarizer"
        enhanced_prompt = f"{notes}\n\n[Summarize in {summary_type} style]"
        update_study_tracking("notes summarization")
        with st.chat_message("assistant"):
            result = render_assistant_response(enhanced_prompt, "Notes Summarizer")
        add_chat_message("user", enhanced_prompt)
        add_chat_message("assistant", result)


def page_assignment_generator() -> None:
    """Assignment Generator page"""
    track_feature_usage("Assignment Generator")
    st.markdown("### 📝 Assignment Generator")
    st.info("Generate well-structured college assignments with proper formatting.")
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input(
            "Assignment Topic",
            placeholder="Example: Cloud Computing and its Applications"
        )
        word_count = st.selectbox(
            "Target Word Count",
            ["500 words", "1000 words", "1500 words", "2000 words"]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Academic Level",
            ["Undergraduate", "Advanced", "Research Level"]
        )
        include_refs = st.checkbox("Include References", value=True)
    
    if st.button("📄 Generate Assignment", use_container_width=True):
        if not topic.strip():
            st.warning("Please enter an assignment topic.")
            return
        
        st.session_state.mode = "Assignment Writer"
        prompt = (
            f"Write a {word_count} {difficulty} level assignment on: {topic}\n"
            f"Include references: {include_refs}"
        )
        update_study_tracking(f"assignment on {topic}")
        
        with st.spinner("✍️ Writing assignment..."):
            with st.chat_message("assistant"):
                result = render_assistant_response(prompt, "Assignment Writer")
        
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)
        
        # Download button for assignment
        st.download_button(
            "⬇️ Download Assignment",
            data=result,
            file_name=f"assignment_{topic.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def page_study_planner() -> None:
    """Study Planner page"""
    track_feature_usage("Study Planner")
    st.markdown("### 📅 Study Planner")
    st.info("Create personalized study schedules based on your exam dates and available time.")
    
    col1, col2 = st.columns(2)
    with col1:
        exam_date = st.date_input("Exam Date", value=datetime.now() + timedelta(days=15))
        hours_per_day = st.slider("Hours available per day", 1, 12, 4)
    
    with col2:
        subjects = st.text_area(
            "Subjects/Topics (one per line)",
            height=100,
            placeholder="DBMS\nOperating Systems\nPython Programming\nComputer Networks"
        )
    
    include_revision = st.checkbox("Include revision days", value=True)
    
    if st.button("🗓️ Create Study Plan", use_container_width=True):
        if not subjects.strip():
            st.warning("Please enter subjects/topics.")
            return
        
        days_remaining = (exam_date - datetime.now().date()).days
        
        if days_remaining <= 0:
            st.error("Exam date must be in the future!")
            return
        
        st.session_state.mode = "Study Planner"
        prompt = (
            f"Create a study plan for:\n"
            f"- Exam in {days_remaining} days\n"
            f"- {hours_per_day} hours available per day\n"
            f"- Subjects: {subjects}\n"
            f"- Include revision: {include_revision}"
        )
        update_study_tracking("study planning")
        
        with st.spinner("📋 Creating your personalized study plan..."):
            with st.chat_message("assistant"):
                result = render_assistant_response(prompt, "Study Planner")
        
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)


def page_exam_paper_generator() -> None:
    """Exam Paper Generator page"""
    track_feature_usage("Exam Paper Generator")
    st.markdown("### 🧾 Exam Paper Generator")
    st.info("Generate realistic university-style exam papers with multiple sections.")
    
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input(
            "Subject/Topic",
            placeholder="Example: Database Management Systems"
        )
        exam_duration = st.selectbox(
            "Exam Duration",
            ["1 hour", "2 hours", "3 hours"]
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            ["Easy", "Medium", "Hard", "Mixed"]
        )
        total_marks = st.selectbox(
            "Total Marks",
            ["40 marks", "50 marks", "75 marks", "100 marks"]
        )
    
    exam_type = st.radio(
        "Exam Type",
        ["Mid-Semester", "End-Semester", "Unit Test"],
        horizontal=True
    )
    
    if st.button("📋 Generate Exam Paper", use_container_width=True):
        if not subject.strip():
            st.warning("Please enter a subject/topic.")
            return
        
        st.session_state.mode = "Exam Prep"
        prompt = (
            f"Generate a {exam_type} exam paper for {subject}\n"
            f"- Duration: {exam_duration}\n"
            f"- Total Marks: {total_marks}\n"
            f"- Difficulty: {difficulty}\n"
            "Include: MCQs, Short Answer, and Long Answer sections with marks distribution."
        )
        update_study_tracking(f"exam paper for {subject}")
        
        with st.spinner("📝 Generating exam paper..."):
            with st.chat_message("assistant"):
                result = render_assistant_response(prompt, "Exam Prep")
        
        add_chat_message("user", prompt)
        add_chat_message("assistant", result)
        
        # Download button for exam paper
        st.download_button(
            "⬇️ Download Exam Paper",
            data=result,
            file_name=f"exam_{subject.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def page_dashboard() -> None:
    """Enhanced Dashboard with analytics"""
    st.markdown("### 📊 Study Dashboard")
    
    # Main metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Questions Asked", st.session_state.questions_asked)
    with m2:
        st.metric("Topics Studied", len(st.session_state.topics_studied))
    with m3:
        st.metric("Session Duration", session_duration_text())
    with m4:
        total_usage = sum(st.session_state.feature_usage.values())
        st.metric("Total Actions", total_usage)
    
    st.divider()
    
    # Feature Usage
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Feature Usage Stats")
        feature_data = get_most_used_features()
        if sum(usage for _, usage in feature_data) > 0:
            for feature, count in feature_data:
                if count > 0:
                    st.metric(feature, count)
        else:
            st.caption("No feature usage data yet. Start using the tools!")
    
    with col2:
        st.markdown("#### 📚 Topics Studied")
        if st.session_state.topics_studied:
            for topic in st.session_state.topics_studied:
                st.markdown(f"• {topic}")
        else:
            st.caption("No topics tracked yet. Ask questions to build your study list.")
    
    st.divider()
    
    # Most Used Study Mode
    st.markdown("#### 🎯 Study Mode Analytics")
    most_used = get_most_used_features()
    if most_used and most_used[0][1] > 0:
        st.success(f"🏆 Most Used Feature: **{most_used[0][0]}** ({most_used[0][1]} times)")
    
    # Recent Activity
    st.markdown("#### 🕐 Recent Activity")
    recent = st.session_state.messages[-8:]
    if recent:
        for item in recent:
            role_icon = "👤" if item["role"] == "user" else "🤖"
            role_label = "You" if item["role"] == "user" else "AI"
            content_preview = item['content'][:150] + "..." if len(item['content']) > 150 else item['content']
            st.markdown(
                f"**{role_icon} {role_label}** ({item.get('timestamp', '')})  \n"
                f"{content_preview}"
            )
            st.divider()
    else:
        st.caption("No activity yet. Start chatting to see your history here!")
    
    # Session Info
    st.markdown("#### ℹ️ Session Information")
    st.caption(f"Session started: {st.session_state.session_start_dt.strftime('%Y-%m-%d %H:%M')}")
    active_model = st.session_state.model if st.session_state.ai_provider == "Gemini" else st.session_state.groq_model
    st.caption(f"Current provider/model: {st.session_state.ai_provider} / {active_model}")
    st.caption(f"Temperature: {st.session_state.temperature}")


# ═══════════════════════════════════════════════════════════════════════════
#                              PAGE ROUTING
# ═══════════════════════════════════════════════════════════════════════════

if st.session_state.nav == "Home":
    page_home()
elif st.session_state.nav == "AI Chat":
    page_ai_chat()
elif st.session_state.nav == "📄 PDF Study Chat":
    page_pdf_study_chat()
elif st.session_state.nav == "Quiz Generator":
    page_quiz_generator()
elif st.session_state.nav == "Code Helper":
    page_code_helper()
elif st.session_state.nav == "Notes Summarizer":
    page_notes_summarizer()
elif st.session_state.nav == "📝 Assignment Generator":
    page_assignment_generator()
elif st.session_state.nav == "📅 Study Planner":
    page_study_planner()
elif st.session_state.nav == "🧾 Exam Paper Generator":
    page_exam_paper_generator()
elif st.session_state.nav == "Dashboard":
    page_dashboard()
