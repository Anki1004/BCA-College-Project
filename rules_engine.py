# rules_engine.py
"""
╔══════════════════════════════════════════════════════════════════════╗
║         BCA AI Academic Platform — Rules & Reasoning Engine          ║
║                                                                      ║
║  Covers:  BCA · BTech · BBA · Platform FAQ · Study Tools            ║
║  Logic:   keyword + regex pattern scoring → deterministic answers    ║
║  Fallback: Gemini (key rotation) → Claude → static message           ║
║                                                                      ║
║  SECURITY: Never hardcode API keys here. Pass at runtime.            ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import re
import json
from typing import Dict, List, Optional, Tuple

# ══════════════════════════════════════════════════════════════════════
#  INTENT CATALOGUE
#  Fields per intent:
#    name                – unique snake_case identifier
#    patterns            – list of regex strings (case-insensitive match)
#    examples            – sample user messages (documentation only)
#    response_templates  – list of answer strings; [0] is used by default
#    confidence_threshold– minimum pattern hits required to fire
#    category            – grouping label (used by the UI / dashboard)
# ══════════════════════════════════════════════════════════════════════

DEFAULT_INTENTS: List[Dict] = [

    # ──────────────────────────────────────────────────────────────────
    #  PLATFORM / SYSTEM INTENTS
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "greeting",
        "category": "platform",
        "patterns": [
            r"\bhi\b", r"\bhello\b", r"\bhey\b",
            r"namaste", r"good\s+(morning|evening|afternoon|night)",
        ],
        "examples": ["hi", "hello", "hey there", "namaste", "good morning"],
        "response_templates": [
            "👋 Hello! Welcome to the BCA AI Academic Platform.\n\n"
            "I can instantly answer questions about:\n"
            "• 🎓 **BCA** — course, subjects, career, salary\n"
            "• 💻 **BTech** — branches, JEE, IITs, career paths\n"
            "• 📊 **BBA** — MBA route, specializations, jobs\n"
            "• 🛠️ Study tools — quiz, assignments, code runner\n\n"
            "What would you like to know?"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "ask_model",
        "category": "platform",
        "patterns": [
            r"which (ai )?model", r"which ai", r"what model are you",
            r"are you (using )?(gemini|claude|gpt|llama)",
            r"which llm",
        ],
        "examples": ["Which model are you using?", "Are you Gemini or Claude?"],
        "response_templates": [
            "🤖 I run on a **hybrid system**:\n\n"
            "1. **Rules Engine** (this file) — instant answers for known questions, zero API cost.\n"
            "2. **Gemini** (primary LLM) — for complex, generative, or open-ended tasks.\n"
            "3. **Claude** (fallback) — if all Gemini keys are exhausted.\n\n"
            "Simple FAQs like this one never touch an external API."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "check_quota",
        "category": "platform",
        "patterns": [
            r"\bquota\b", r"rate.?limit", r"requests per minute",
            r"\brpm\b", r"\brpd\b", r"\btpm\b",
            r"api.?limit", r"too many requests",
        ],
        "examples": ["Why quota error?", "How many requests per minute?"],
        "response_templates": [
            "⚠️ **API Quota Guide**\n\n"
            "• RPM = Requests Per Minute | RPD = Requests Per Day | TPM = Tokens Per Minute\n"
            "• Free Gemini tier: ~15 RPM / 1500 RPD per key.\n"
            "• If keys are in the **same** Google Cloud project → quota is shared.\n"
            "• Use **separate projects** for each key to get independent quotas.\n"
            "• Check your dashboard: https://console.cloud.google.com/apis\n\n"
            "💡 Tip: Add more keys to `GEMINI_KEYS` in secrets.toml for automatic rotation."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "set_keys",
        "category": "platform",
        "patterns": [
            r"set (api )?keys?", r"add (api )?key", r"update (api )?key",
            r"streamlit secrets", r"secrets\.toml",
            r"where (do i |to )?put.{0,15}key",
        ],
        "examples": ["How do I set API keys?", "Where to put Gemini key?"],
        "response_templates": [
            "🔑 **Setting API Keys in Streamlit**\n\n"
            "Edit `.streamlit/secrets.toml`:\n\n"
            "```toml\n"
            "GEMINI_KEYS = [\"AIza_key1\", \"AIza_key2\", \"AIza_key3\"]\n"
            "CLAUDE_API_KEY = \"sk-ant-your_claude_key\"\n"
            "```\n\n"
            "• Multiple Gemini keys are rotated automatically.\n"
            "• **Never** commit this file to GitHub — add it to `.gitignore`.\n"
            "• On Streamlit Cloud: add keys via **Settings → Secrets**."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "explain_error",
        "category": "platform",
        "patterns": [
            r"all api attempts failed",
            r"api attempts failed",
            r"error.{0,10}all api",
            r"app (is )?not (working|responding)",
            r"getting (an )?error",
        ],
        "examples": ["All API attempts failed", "App not working"],
        "response_templates": [
            "🛠️ **Troubleshooting 'All API Attempts Failed'**\n\n"
            "**Most common causes:**\n"
            "1. `GEMINI_KEYS` in secrets.toml is empty or has expired keys.\n"
            "2. Wrong model name (use `gemini-1.5-flash` not `gemini-pro`).\n"
            "3. SDK version mismatch — run `pip install -U google-generativeai`.\n"
            "4. All keys hit quota simultaneously.\n\n"
            "**Quick fix steps:**\n"
            "• Add a `print(e)` inside the `except` block to see the real error.\n"
            "• Verify keys at https://aistudio.google.com/app/apikey\n"
            "• Check `CLAUDE_API_KEY` as a last resort fallback."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "offline_options",
        "category": "platform",
        "patterns": [
            r"\boffline\b", r"local.?model", r"\bollama\b",
            r"run (it )?locally", r"self.?hosted", r"host (my own|the) model",
            r"without internet",
        ],
        "examples": ["Can I use this offline?", "How to run Ollama locally?"],
        "response_templates": [
            "🖥️ **Running AI Models Locally / Offline**\n\n"
            "**Option 1 — Ollama (easiest):**\n"
            "```bash\n"
            "curl https://ollama.ai/install.sh | sh\n"
            "ollama run llama3\n"
            "```\n"
            "Then point your app to `http://localhost:11434`.\n\n"
            "**Option 2 — VPS / EC2:**\n"
            "• Deploy on AWS EC2 (g4dn.xlarge recommended for GPU).\n"
            "• Expose via ngrok or a reverse proxy.\n\n"
            "⚠️ Streamlit Cloud **cannot** host local models — you need your own server."
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  BCA — BACHELOR OF COMPUTER APPLICATIONS
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "bca_what_is",
        "category": "BCA",
        "patterns": [
            r"^\s*bca\s*$",                    # bare "bca" or "BCA"
            r"what is bca\b",
            r"bca (course|degree|full form)",
            r"bca\b.{0,10}\bprogram\b",
            r"bachelor of computer applications",
            r"tell me about bca",
            r"bca explain",
            r"about bca",
        ],
        "examples": ["What is BCA?", "Explain BCA course"],
        "response_templates": [
            "🎓 **What is BCA (Bachelor of Computer Applications)?**\n\n"
            "BCA is a **3-year undergraduate degree** focused on computer science, "
            "software development, and IT applications.\n\n"
            "**Key Highlights:**\n"
            "• Full form: **B**achelor of **C**omputer **A**pplications\n"
            "• Duration: **3 years** (6 semesters)\n"
            "• Level: Undergraduate (UG) degree\n"
            "• Focus: Programming, databases, networking, web development\n\n"
            "**Why choose BCA?**\n"
            "✅ Pathway into software industry without JEE\n"
            "✅ Lower fees than BTech (~₹1–3 LPA vs ₹5–15 LPA)\n"
            "✅ MCA/MBA possible after BCA\n"
            "✅ Strong job market for fresher developers"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_subjects",
        "category": "BCA",
        "patterns": [
            r"bca (subjects?|syllabus|curriculum|topics?)",
            r"subjects?.{0,15}bca",
            r"what (do|does).{0,15}bca (teach|cover|include)",
            r"bca (semester|sem).{0,10}(subjects?|topics?)",
        ],
        "examples": ["BCA subjects", "BCA syllabus semester 1"],
        "response_templates": [
            "📚 **BCA Subjects & Syllabus (Semester-wise)**\n\n"
            "**Sem 1–2 (Foundation):**\n"
            "• C Programming · Mathematics · Digital Electronics\n"
            "• PC Software · English Communication · Introduction to IT\n\n"
            "**Sem 3–4 (Core):**\n"
            "• Data Structures · DBMS · Java Programming\n"
            "• Operating Systems · Computer Networks · Web Technology\n\n"
            "**Sem 5–6 (Advanced + Project):**\n"
            "• Software Engineering · Python/Advanced Java\n"
            "• Cloud Computing / AI Basics · Minor Project · Major Project\n\n"
            "💡 **Must-learn languages for BCA students:**\n"
            "C → Python → Java → SQL → JavaScript"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_eligibility",
        "category": "BCA",
        "patterns": [
            r"bca (eligibility|requirement|admission|criteria|qualify)",
            r"(who|how).{0,20}(apply|get into|eligible).{0,15}bca",
            r"bca (10\+2|12th|twelfth|class 12)",
            r"bca after (10th|12th|school)",
        ],
        "examples": ["BCA eligibility criteria", "How to get admission in BCA?"],
        "response_templates": [
            "📋 **BCA Eligibility & Admission**\n\n"
            "**Minimum Requirements:**\n"
            "• Passed **10+2** (any stream — Science/Commerce/Arts)\n"
            "• Minimum **45–50% marks** in 12th (varies by college)\n"
            "• Mathematics in 12th is **preferred** (mandatory at some colleges)\n\n"
            "**Admission Process:**\n"
            "• Most colleges: **Merit-based** (12th marks)\n"
            "• Some colleges: Entrance test (IPU CET, BCA entrance, NIMCET)\n"
            "• DU BCA: CUET score required\n\n"
            "**Important Entrance Exams:**\n"
            "| Exam | Conducting Body |\n"
            "|------|----------------|\n"
            "| CUET | Central Universities |\n"
            "| IPU CET | Indraprastha University |\n"
            "| NIMCET | NITs (for MCA, not BCA) |\n\n"
            "📅 Applications typically open **March–June** each year."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_career",
        "category": "BCA",
        "patterns": [
            r"bca (career|job|scope|future|after|placement)",
            r"jobs?.{0,15}bca",
            r"what (can i|to) do after bca",
            r"bca (graduate|fresher).{0,20}(job|career|work)",
            r"bca (worth|good|useful)",
        ],
        "examples": ["BCA career options", "Jobs after BCA", "Is BCA worth it?"],
        "response_templates": [
            "💼 **BCA Career Options & Job Roles**\n\n"
            "**Top Job Roles for BCA Graduates:**\n"
            "• 👨‍💻 Software Developer / Web Developer\n"
            "• 🗄️ Database Administrator (DBA)\n"
            "• 🔍 QA / Test Engineer\n"
            "• 🌐 Network Administrator\n"
            "• 📊 Data Analyst (with extra SQL/Python skills)\n"
            "• 🛡️ Cybersecurity Analyst (with certifications)\n"
            "• 💼 IT Support / Systems Analyst\n\n"
            "**Top Recruiting Companies:**\n"
            "TCS · Infosys · Wipro · HCL · Cognizant · Accenture · Tech Mahindra\n\n"
            "**Higher Study Options:**\n"
            "📖 MCA → Senior Developer / Architect roles\n"
            "📖 MBA (IT/Finance) → Management + Tech hybrid roles\n"
            "📖 MTech (lateral entry possible at some universities)\n\n"
            "🌍 **International options:** MSc CS abroad (Canada, UK, Germany)"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_salary",
        "category": "BCA",
        "patterns": [
            r"bca (salary|pay|package|ctc|lpa|stipend)",
            r"(how much|salary).{0,20}bca",
            r"bca (fresher|graduate|pass.?out).{0,15}(earn|salary|pay)",
        ],
        "examples": ["BCA salary", "How much does a BCA graduate earn?"],
        "response_templates": [
            "💰 **BCA Salary Expectations (India)**\n\n"
            "| Experience | Average CTC |\n"
            "|------------|-------------|\n"
            "| Fresher (0–1 yr) | ₹2.5 – 4.5 LPA |\n"
            "| Mid-level (2–4 yr) | ₹4.5 – 8 LPA |\n"
            "| Senior (5+ yr) | ₹8 – 18 LPA |\n"
            "| After MCA + 3 yr | ₹8 – 20 LPA |\n\n"
            "**Highest paying skills for BCA graduates:**\n"
            "• Full-Stack Development (React + Node) → ₹5–12 LPA fresher\n"
            "• Data Science / ML (Python + stats) → ₹6–15 LPA\n"
            "• Cloud (AWS/Azure certifications) → ₹6–14 LPA\n"
            "• DevOps (Docker, Kubernetes) → ₹7–16 LPA\n\n"
            "💡 Tip: BCA + MCA from NIT = BTech-equivalent package at top companies."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_vs_btech",
        "category": "BCA",
        "patterns": [
            r"bca (vs|versus|or|compared to) b\.?tech",
            r"b\.?tech (vs|versus|or|compared to) bca",
            r"difference.{0,20}bca.{0,20}b\.?tech",
            r"(which is better|choose between).{0,20}bca.{0,20}b\.?tech",
        ],
        "examples": ["BCA vs BTech", "Which is better BCA or BTech?"],
        "response_templates": [
            "⚖️ **BCA vs BTech — Full Comparison**\n\n"
            "| Factor | BCA | BTech |\n"
            "|--------|-----|-------|\n"
            "| Duration | 3 years | 4 years |\n"
            "| Stream | Computer Applications | Engineering |\n"
            "| Eligibility | 10+2 (any stream) | 10+2 PCM + JEE |\n"
            "| Avg Fees | ₹1–3 LPA | ₹2–15 LPA |\n"
            "| Maths depth | Moderate | High |\n"
            "| Coding focus | High | High |\n"
            "| Hardware/Electronics | No | Yes |\n"
            "| Fresher salary | ₹2.5–4.5 LPA | ₹3.5–8 LPA |\n"
            "| Higher study | MCA / MBA | MTech / MBA |\n"
            "| IIT/NIT option | No | Yes (JEE) |\n\n"
            "**Choose BCA if:** You want to save a year, avoid JEE, focus on pure software development.\n"
            "**Choose BTech if:** You want engineering tag, IIT/NIT campus, or hardware/electronics interest."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_best_colleges",
        "category": "BCA",
        "patterns": [
            r"best.{0,15}bca.{0,15}college",
            r"top.{0,15}bca.{0,15}(college|university|institute)",
            r"bca.{0,15}(college|university).{0,15}(best|top|rank)",
        ],
        "examples": ["Best colleges for BCA", "Top BCA universities in India"],
        "response_templates": [
            "🏫 **Top BCA Colleges in India**\n\n"
            "**Government / Central Universities:**\n"
            "• Delhi University (DU) — CUET required\n"
            "• Jamia Millia Islamia, Delhi\n"
            "• BHU Varanasi · University of Hyderabad\n\n"
            "**Deemed / Private (Top):**\n"
            "• Christ University, Bangalore\n"
            "• Symbiosis Institute of Computer Studies (SICSR), Pune\n"
            "• Manipal University · Lovely Professional University (LPU)\n"
            "• Amity University\n\n"
            "**State-level top picks:**\n"
            "• IGNOU (distance BCA — for working students)\n"
            "• IP University colleges, Delhi\n"
            "• Savitribai Phule Pune University affiliates\n\n"
            "📌 **How to pick:** NAAC A+ grade + placement records > brand name."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_languages",
        "category": "BCA",
        "patterns": [
            r"bca.{0,25}(programming|coding|language)",
            r"(programming|coding|language).{0,25}bca",
            r"bca (student|graduate).{0,20}(learn|study|know)",
            r"bca.{0,15}should (learn|know|study)",
        ],
        "examples": ["Which languages should BCA students learn?", "BCA programming languages"],
        "response_templates": [
            "💻 **Programming Languages for BCA Students**\n\n"
            "**Semester-by-semester learning path:**\n\n"
            "🔹 **Year 1:** `C` → logic building, memory, pointers\n"
            "🔹 **Year 2:** `Java` → OOP, data structures · `SQL` → databases\n"
            "🔹 **Year 3:** `Python` → automation, data science · `JavaScript` → web\n\n"
            "**Recommended learning order:**\n"
            "```\n"
            "C → Python → Java → SQL → HTML/CSS → JavaScript → React\n"
            "```\n\n"
            "**High-demand skills by career path:**\n"
            "| Career Path | Key Skills |\n"
            "|-------------|------------|\n"
            "| Web Dev | JS, React, Node.js, SQL |\n"
            "| Data Analyst | Python, SQL, Excel, Power BI |\n"
            "| Android Dev | Java/Kotlin, Android Studio |\n"
            "| Backend Dev | Python/Java, REST APIs, Docker |\n"
            "| ML/AI | Python, NumPy, Pandas, TensorFlow |"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bca_mca",
        "category": "BCA",
        "patterns": [
            r"bca (then|after|then do|followed by) mca",
            r"mca after bca",
            r"bca.{0,10}mca.{0,20}(good|worth|career|salary|scope)",
            r"should i do mca after bca",
        ],
        "examples": ["Should I do MCA after BCA?", "BCA then MCA career"],
        "response_templates": [
            "🎓 **BCA → MCA: Is It Worth It?**\n\n"
            "**YES — if you want:**\n"
            "✅ Higher salary (₹6–20 LPA vs ₹3–5 LPA)\n"
            "✅ Core software roles at product companies\n"
            "✅ BTech-equivalent recognition at many MNCs\n"
            "✅ GATE score → PSU / IIT MTech option\n\n"
            "**MCA from NIT (via NIMCET):**\n"
            "• NIT Trichy, NIT Surathkal, MNNIT Allahabad\n"
            "• Package: ₹8–25 LPA (similar to NIT BTech CSE)\n"
            "• Entrance: NIMCET (national level)\n\n"
            "**Timeline:** BCA (3 yr) + MCA (2 yr) = 5 years total\n"
            "vs BTech = 4 years — one extra year but often more affordable.\n\n"
            "💡 **Shortcut:** BCA + MCA from NIT > BTech from average private college."
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  BTECH — BACHELOR OF TECHNOLOGY
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "btech_what_is",
        "category": "BTech",
        "patterns": [
            r"^\s*b\.?tech\s*$",               # bare "btech" or "BTech"
            r"what is b\.?tech\b",
            r"b\.?tech (course|degree|program|full form)",
            r"bachelor of technology",
            r"tell me about b\.?tech",
            r"b\.?tech explain",
            r"about b\.?tech",
        ],
        "examples": ["What is BTech?", "Explain BTech course"],
        "response_templates": [
            "🔧 **What is BTech (Bachelor of Technology)?**\n\n"
            "BTech is a **4-year undergraduate engineering degree** that combines "
            "theoretical knowledge with practical engineering skills.\n\n"
            "**Key Highlights:**\n"
            "• Full form: **B**achelor of **Tech**nology\n"
            "• Duration: **4 years** (8 semesters)\n"
            "• Level: Undergraduate (UG) Engineering degree\n"
            "• Entry: JEE Main/Advanced for top colleges\n\n"
            "**BTech vs BE:**\n"
            "• BTech = Technology-focused (IITs, NITs, BITS)\n"
            "• BE = Engineering-focused (VTU, SPPU affiliates)\n"
            "• Both are **equivalent** in industry recognition.\n\n"
            "**Top BTech branches by demand (2024):**\n"
            "1. CSE / CS with AI & ML\n"
            "2. Electronics & Communication (ECE)\n"
            "3. Mechanical Engineering\n"
            "4. Electrical Engineering (EE)\n"
            "5. Civil Engineering"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_branches",
        "category": "BTech",
        "patterns": [
            r"b\.?tech (branches?|specialization|streams?|fields?)",
            r"(branches?|specialization).{0,15}b\.?tech",
            r"b\.?tech (cse|ece|mech|civil|eee|it)\b",
            r"which b\.?tech (branch|stream|field)",
        ],
        "examples": ["BTech branches", "Which BTech specialization is best?"],
        "response_templates": [
            "🌿 **BTech Branches & Specializations**\n\n"
            "**Core Branches:**\n"
            "| Branch | Short | Best For |\n"
            "|--------|-------|----------|\n"
            "| Computer Science & Engg | CSE | Software, AI, web, apps |\n"
            "| Information Technology | IT | Software, networking |\n"
            "| Electronics & Communication | ECE | Chips, IoT, telecom |\n"
            "| Electrical Engineering | EE/EEE | Power, automation |\n"
            "| Mechanical Engineering | Mech | Manufacturing, design |\n"
            "| Civil Engineering | Civil | Infrastructure, construction |\n"
            "| Chemical Engineering | Chem | Process industries |\n"
            "| Aerospace Engineering | Aero | Defense, ISRO, airlines |\n\n"
            "**Emerging Specializations (CSE sub-branches):**\n"
            "• CSE (AI & ML) · CSE (Data Science) · CSE (Cybersecurity)\n"
            "• CSE (IoT) · CSE (Cloud Computing) · CSE (Blockchain)\n\n"
            "📊 **2024 Placement rankings:** CSE > ECE > Mech > Civil"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_eligibility_jee",
        "category": "BTech",
        "patterns": [
            r"b\.?tech (eligibility|requirement|admission|criteria|qualify)",
            r"jee (main|advanced|exam|preparation|score|eligibility|criteria)",
            r"\bjee\b",
            r"how to (get into|join|apply).{0,15}b\.?tech",
            r"b\.?tech (entrance|exam|test)",
            r"(iit|nit).{0,15}(admission|entrance|jee)",
        ],
        "examples": ["BTech eligibility", "JEE exam details", "How to get into IIT?"],
        "response_templates": [
            "📋 **BTech Eligibility & Admission Process**\n\n"
            "**Minimum Requirements:**\n"
            "• Passed **10+2** with **PCM** (Physics, Chemistry, Math)\n"
            "• Minimum **75% marks** in 12th (65% for SC/ST)\n"
            "• Age: Born on or after Oct 1, 2000 (JEE 2025)\n\n"
            "**National Entrance Exams:**\n"
            "| Exam | Colleges | Attempts |\n"
            "|------|----------|----------|\n"
            "| JEE Main | NITs, IIITs, GFTIs + private | 2/year × 3 years |\n"
            "| JEE Advanced | IITs only | After JEE Main top 2.5L |\n"
            "| BITSAT | BITS Pilani/Goa/Hyderabad | 1 per year |\n"
            "| MHT-CET | Maharashtra colleges | — |\n"
            "| COMEDK | Karnataka colleges | — |\n"
            "| KCET | Karnataka govt colleges | — |\n\n"
            "**JEE Main 2025:**\n"
            "• January session + April session\n"
            "• Total: 90 questions · 300 marks · 3 hours\n"
            "• Subjects: Physics (30) + Chemistry (30) + Math (30)"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_career",
        "category": "BTech",
        "patterns": [
            r"b\.?tech (career|job|scope|future|after|placement)",
            r"jobs?.{0,15}b\.?tech",
            r"what (can i|to) do after b\.?tech",
            r"b\.?tech (graduate|fresher).{0,20}(job|career|work)",
            r"b\.?tech (worth|good|useful|salary)",
        ],
        "examples": ["BTech career options", "Jobs after BTech CSE"],
        "response_templates": [
            "💼 **BTech Career Options & Paths**\n\n"
            "**Software / CSE BTech:**\n"
            "• Software Engineer (SDE) — Google, Amazon, Microsoft\n"
            "• Data Scientist / ML Engineer — ₹10–30 LPA fresher at top firms\n"
            "• DevOps / Cloud Engineer — AWS, Azure roles\n"
            "• Product Manager (MBA + BTech combo)\n\n"
            "**Core Engineering BTech:**\n"
            "• Mechanical: Design Engineer, R&D, ISRO/DRDO/PSU\n"
            "• ECE: VLSI Engineer, Embedded Systems, Telecom\n"
            "• Civil: Structural Engineer, Urban Planner, NHAI\n"
            "• EE: Power Systems, Automation, NTPC/BHEL\n\n"
            "**Non-technical paths after BTech:**\n"
            "• MBA (IIM via CAT) → Management consulting\n"
            "• UPSC Civil Services → IAS/IPS/IFS\n"
            "• GATE → PSU jobs (ONGC, BHEL, BEL) + MTech at IITs\n\n"
            "**IIT CSE fresher packages (2024):** ₹20–1.2 Cr CTC"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_salary",
        "category": "BTech",
        "patterns": [
            r"b\.?tech (salary|pay|package|ctc|lpa)",
            r"(how much|salary|package).{0,20}b\.?tech",
            r"iit.{0,15}(salary|package|ctc|placement)",
            r"nit.{0,15}(salary|package|ctc|placement)",
        ],
        "examples": ["BTech salary", "IIT package", "NIT placement"],
        "response_templates": [
            "💰 **BTech Salary & Placement Data (India 2024)**\n\n"
            "**By college tier:**\n"
            "| Tier | Avg Package | Highest |\n"
            "|------|-------------|--------|\n"
            "| IIT (top 5) | ₹20–30 LPA | ₹1–4 Cr (international) |\n"
            "| IIT (other) | ₹15–22 LPA | ₹60–100 LPA |\n"
            "| NIT (top 10) | ₹8–15 LPA | ₹40–60 LPA |\n"
            "| BITS Pilani | ₹12–20 LPA | ₹70 LPA+ |\n"
            "| Avg private college | ₹3.5–6 LPA | ₹12–18 LPA |\n\n"
            "**By branch (avg fresher, mid-tier college):**\n"
            "• CSE: ₹4–8 LPA → ₹12–25 LPA (3 yrs exp)\n"
            "• ECE: ₹3.5–6 LPA\n"
            "• Mechanical: ₹3–5 LPA\n"
            "• Civil: ₹2.5–4.5 LPA\n\n"
            "💡 Skills like DSA + System Design + open source = 2–3x salary boost."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_cse_vs_it",
        "category": "BTech",
        "patterns": [
            r"(cse|computer science).{0,10}(vs|versus|or).{0,10}(it|information technology)",
            r"(it|information technology).{0,10}(vs|versus|or).{0,10}(cse|computer science)",
            r"difference.{0,20}cse.{0,20}(it|information technology)",
            r"(which is better|choose).{0,20}(cse|it)\b",
        ],
        "examples": ["CSE vs IT BTech", "Which is better CSE or IT?"],
        "response_templates": [
            "⚖️ **BTech CSE vs IT — What's the Difference?**\n\n"
            "| Factor | CSE | IT |\n"
            "|--------|-----|----|\n"
            "| Theory depth | Higher (algorithms, compilers) | Moderate |\n"
            "| Application focus | OS, compilers, AI, hardware | Networks, web, software |\n"
            "| Industry perception | Slightly preferred | Equivalent at most companies |\n"
            "| Syllabus overlap | ~80% the same | ~80% the same |\n"
            "| GATE scope | Better for core CS topics | Slightly narrower |\n\n"
            "**In practice:**\n"
            "• MNCs (TCS, Google, Amazon) hire both equally.\n"
            "• **Your skills and projects matter more** than CSE vs IT tag.\n"
            "• If both available at same college → take CSE.\n"
            "• If CSE is at a lower-ranked college → take IT at a better college.\n\n"
            "🏆 **College rank > Branch name** for placements."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_iit_nit",
        "category": "BTech",
        "patterns": [
            r"\biit\b.{0,20}(best|top|rank|list|college)",
            r"\bnit\b.{0,20}(best|top|rank|list|college)",
            r"top (engineering|b\.?tech|iit|nit) (college|institute|university)",
            r"best.{0,15}engineering.{0,15}(college|institute)",
            r"iit (bombay|delhi|madras|kanpur|kharagpur|roorkee|guwahati)",
        ],
        "examples": ["Top IITs in India", "Best engineering colleges", "NIT ranking"],
        "response_templates": [
            "🏫 **Top Engineering Colleges in India**\n\n"
            "**Old IITs (Tier 1):**\n"
            "1. IIT Bombay · 2. IIT Delhi · 3. IIT Madras\n"
            "4. IIT Kanpur · 5. IIT Kharagpur · 6. IIT Roorkee · 7. IIT Guwahati\n\n"
            "**New IITs (Tier 2):**\n"
            "IIT Hyderabad · IIT Indore · IIT Jodhpur · IIT Patna · IIT Gandhinagar\n\n"
            "**Top NITs:**\n"
            "1. NIT Trichy · 2. NIT Surathkal · 3. NIT Warangal\n"
            "4. NIT Calicut · 5. MNNIT Allahabad\n\n"
            "**Other Tier-1 institutes:**\n"
            "• BITS Pilani / Goa / Hyderabad\n"
            "• IIITs (Hyderabad, Delhi, Allahabad)\n"
            "• Jadavpur University · COEP Pune · VIT Vellore\n\n"
            "📊 Source: NIRF 2024 | JoSAA cutoffs at josaa.nic.in"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "btech_after_mba",
        "category": "BTech",
        "patterns": [
            r"b\.?tech.{0,15}(then|after|followed by).{0,15}mba",
            r"mba after b\.?tech",
            r"b\.?tech.{0,10}mba.{0,20}(good|worth|career|salary|scope)",
            r"(cat|iim).{0,20}(b\.?tech|engineering)",
        ],
        "examples": ["BTech then MBA", "Should I do MBA after BTech?"],
        "response_templates": [
            "🎓 **BTech → MBA: The Power Combo**\n\n"
            "**Why BTech + MBA works:**\n"
            "• Tech background + management skills = product manager, consultant, founder\n"
            "• IIMs accept BTech grads with 2+ years work experience\n"
            "• Average IIM package (BTech+MBA): ₹25–35 LPA\n\n"
            "**Timeline options:**\n"
            "• BTech → Work 2–3 yrs → MBA (recommended by IIMs)\n"
            "• BTech → MBA directly (possible but less preferred)\n\n"
            "**Top MBA entrance exams:**\n"
            "| Exam | Institutes |\n"
            "|------|------------|\n"
            "| CAT | IIMs, FMS, MDI, IITs |\n"
            "| XAT | XLRI, SP Jain |\n"
            "| GMAT | ISB, IIM (PGPX), abroad |\n\n"
            "**Best MBA specializations for BTech grads:**\n"
            "Operations · Product Management · Tech Consulting · Entrepreneurship"
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  BBA — BACHELOR OF BUSINESS ADMINISTRATION
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "bba_what_is",
        "category": "BBA",
        "patterns": [
            r"^\s*bba\s*$",                    # bare "bba" or "BBA"
            r"what is bba\b",
            r"bba (course|degree|program|full form)",
            r"bachelor of business administration",
            r"tell me about bba",
            r"bba explain",
            r"about bba",
        ],
        "examples": ["What is BBA?", "Explain BBA course"],
        "response_templates": [
            "📊 **What is BBA (Bachelor of Business Administration)?**\n\n"
            "BBA is a **3-year undergraduate business degree** that prepares students "
            "for management, entrepreneurship, and MBA programmes.\n\n"
            "**Key Highlights:**\n"
            "• Full form: **B**achelor of **B**usiness **A**dministration\n"
            "• Duration: **3 years** (6 semesters)\n"
            "• Focus: Management, Marketing, Finance, HR, Entrepreneurship\n"
            "• Direct pathway to MBA without work experience requirement\n\n"
            "**Why choose BBA?**\n"
            "✅ Best route to MBA (especially IIM Indore IPM — integrated 5-year)\n"
            "✅ Builds leadership, communication, analytical skills early\n"
            "✅ Lower fees than BTech\n"
            "✅ Open to Arts/Commerce/Science students from 12th"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_subjects",
        "category": "BBA",
        "patterns": [
            r"bba (subjects?|syllabus|curriculum|topics?)",
            r"subjects?.{0,15}bba",
            r"what (do|does).{0,15}bba (teach|cover|include)",
            r"bba (semester|sem).{0,10}(subjects?|topics?)",
        ],
        "examples": ["BBA subjects", "BBA syllabus"],
        "response_templates": [
            "📚 **BBA Subjects & Syllabus**\n\n"
            "**Year 1 — Foundation:**\n"
            "• Business Communication · Principles of Management\n"
            "• Business Mathematics · Financial Accounting · Micro Economics\n\n"
            "**Year 2 — Core:**\n"
            "• Marketing Management · Human Resource Management\n"
            "• Financial Management · Business Law · Macro Economics\n"
            "• Organizational Behaviour · Business Statistics\n\n"
            "**Year 3 — Advanced + Electives:**\n"
            "• Strategic Management · International Business\n"
            "• Entrepreneurship · Research Methodology\n"
            "• Elective: Marketing / Finance / HR / IT / Operations\n"
            "• Internship + Project Report\n\n"
            "💡 **Extra skills BBA students should learn:**\n"
            "Excel · Power BI · Tally · SAP basics · Google Analytics · LinkedIn"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_eligibility",
        "category": "BBA",
        "patterns": [
            r"bba (eligibility|requirement|admission|criteria|qualify)",
            r"(who|how).{0,20}(apply|get into|eligible).{0,15}bba",
            r"bba (after|10\+2|12th|twelfth)",
            r"bba entrance",
        ],
        "examples": ["BBA eligibility", "How to get admission in BBA?"],
        "response_templates": [
            "📋 **BBA Eligibility & Admission**\n\n"
            "**Minimum Requirements:**\n"
            "• Passed **10+2** in any stream (Science / Commerce / Arts)\n"
            "• Minimum **50% marks** in 12th (varies by college)\n"
            "• No specific subject restriction (Maths helpful, not mandatory)\n\n"
            "**Admission Modes:**\n"
            "• Merit-based (most private colleges)\n"
            "• Entrance exam + interview (DU, Christ, Symbiosis)\n\n"
            "**Top BBA Entrance Exams:**\n"
            "| Exam | Colleges |\n"
            "|------|----------|\n"
            "| IPMAT | IIM Indore + Rohtak (5-yr IPM) |\n"
            "| SET (Symbiosis) | Symbiosis Pune |\n"
            "| CUET | DU and central universities |\n"
            "| DU JAT | Delhi University colleges |\n"
            "| Christ Entrance | Christ University Bangalore |\n\n"
            "📌 **IPMAT tip:** Crack IPMAT → IIM Indore IPM = effectively free MBA at 18!"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_career",
        "category": "BBA",
        "patterns": [
            r"bba (career|job|scope|future|after|placement)",
            r"jobs?.{0,15}bba",
            r"what (can i|to) do after bba",
            r"bba (graduate|fresher).{0,20}(job|career|work)",
            r"bba (worth|good|useful)",
        ],
        "examples": ["BBA career options", "Jobs after BBA", "Is BBA worth it?"],
        "response_templates": [
            "💼 **BBA Career Options**\n\n"
            "**Direct Jobs after BBA:**\n"
            "• 📣 Marketing Executive / Brand Manager\n"
            "• 💰 Sales Executive / Business Development\n"
            "• 👥 HR Executive / Talent Acquisition\n"
            "• 🏦 Banking (HDFC, ICICI, Axis — management trainee)\n"
            "• 📊 Financial Analyst (with good accounting skills)\n"
            "• 🛒 Retail Manager / Operations Trainee\n\n"
            "**Higher Study (strongly recommended):**\n"
            "• MBA (IIM / XLRI / MDI) → ₹15–35 LPA average\n"
            "• Chartered Accountancy (CA) if Finance track\n"
            "• CFA / CMA for Finance specialization\n"
            "• Digital Marketing certifications (Google, HubSpot)\n\n"
            "**Entrepreneurship path:**\n"
            "BBA provides the foundation — many BBA grads launch businesses directly.\n\n"
            "🎯 **Value multiplier:** BBA + MBA from tier-1 = management consulting entry"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_salary",
        "category": "BBA",
        "patterns": [
            r"bba (salary|pay|package|ctc|lpa|stipend)",
            r"(how much|salary).{0,20}bba",
            r"bba (fresher|graduate|pass.?out).{0,15}(earn|salary|pay)",
        ],
        "examples": ["BBA salary", "How much does a BBA graduate earn?"],
        "response_templates": [
            "💰 **BBA Salary Guide (India)**\n\n"
            "| Level | Average CTC |\n"
            "|-------|-------------|\n"
            "| BBA Fresher | ₹2 – 4 LPA |\n"
            "| BBA + 2–3 yrs exp | ₹4 – 7 LPA |\n"
            "| BBA + MBA (tier-2) | ₹6 – 12 LPA |\n"
            "| BBA + IIM MBA | ₹18 – 35 LPA |\n\n"
            "**Salary by function:**\n"
            "• Marketing: ₹3–5 LPA fresher, ₹8–15 LPA (5 yrs)\n"
            "• Finance/Banking: ₹3–6 LPA fresher\n"
            "• Sales: ₹3–5 LPA + incentives (can reach ₹8–12 LPA)\n"
            "• HR: ₹2.5–4 LPA fresher\n\n"
            "⚠️ **Reality check:** BBA alone gives modest salary.\n"
            "**BBA + MBA** is the real career accelerator.\n\n"
            "💡 Top BBA colleges (Christ, Symbiosis, DU) place in FMCG, banking at ₹4–8 LPA freshers."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_vs_bcom",
        "category": "BBA",
        "patterns": [
            r"bba (vs|versus|or|compared to) b\.?com",
            r"b\.?com (vs|versus|or|compared to) bba",
            r"difference.{0,20}bba.{0,20}b\.?com",
            r"(which is better|choose between).{0,20}(bba|b\.?com)",
        ],
        "examples": ["BBA vs BCom", "Which is better BBA or BCom?"],
        "response_templates": [
            "⚖️ **BBA vs BCom — Full Comparison**\n\n"
            "| Factor | BBA | BCom |\n"
            "|--------|-----|------|\n"
            "| Focus | Management & leadership | Accounting & commerce |\n"
            "| Duration | 3 years | 3 years |\n"
            "| Maths requirement | Low | Moderate |\n"
            "| CA compatibility | Low | High |\n"
            "| MBA pathway | Strong | Possible |\n"
            "| Avg fees | ₹1–4 LPA | ₹0.3–1.5 LPA |\n"
            "| Govt job scope | Moderate | Higher (banking exams) |\n"
            "| Entrepreneurship | Better | Moderate |\n"
            "| Finance depth | Moderate | High |\n\n"
            "**Choose BBA if:** MBA, management career, marketing, HR, or entrepreneurship.\n"
            "**Choose BCom if:** CA, government banking exams, lower fees, or accounting roles."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_mba",
        "category": "BBA",
        "patterns": [
            r"bba.{0,15}(then|after|followed by).{0,15}mba",
            r"mba after bba",
            r"bba.{0,10}mba.{0,20}(good|worth|career|salary|scope)",
            r"iim.{0,20}bba",
        ],
        "examples": ["MBA after BBA", "BBA then MBA career path"],
        "response_templates": [
            "🎓 **BBA → MBA Career Path**\n\n"
            "**The classic route:**\n"
            "BBA (3 yrs) → Work 1–2 yrs → MBA (2 yrs) = Management career\n\n"
            "**Or the fast route (no work experience needed):**\n"
            "IPMAT → IIM Indore / Rohtak IPM (5-yr integrated BBA+MBA)\n\n"
            "**Top MBA colleges after BBA:**\n"
            "| College | Entrance | Avg Package |\n"
            "|---------|----------|-------------|\n"
            "| IIM Ahmedabad | CAT | ₹35 LPA |\n"
            "| IIM Bangalore | CAT | ₹33 LPA |\n"
            "| XLRI Jamshedpur | XAT | ₹28 LPA |\n"
            "| MDI Gurgaon | CAT | ₹24 LPA |\n"
            "| SP Jain Mumbai | CAT/XAT | ₹22 LPA |\n\n"
            "**Specializations to pick:**\n"
            "• Marketing · Finance · HR · General Management\n\n"
            "💡 Work experience (2–3 yrs) before MBA significantly increases IIM call chances."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_specializations",
        "category": "BBA",
        "patterns": [
            r"bba (specialization|specialisation|stream|track|elective)",
            r"(types|kinds|options) of bba",
            r"bba (finance|marketing|hr|international|it|digital)",
        ],
        "examples": ["BBA specializations", "Types of BBA courses"],
        "response_templates": [
            "🌿 **BBA Specializations**\n\n"
            "**Core BBA Tracks:**\n"
            "| Specialization | Key Skills | Best For |\n"
            "|----------------|-----------|----------|\n"
            "| Marketing | Branding, digital ads, CRM | Ad agencies, FMCG, startups |\n"
            "| Finance | Accounting, investments, Excel | Banking, CA, wealth mgmt |\n"
            "| Human Resources | Talent, training, labor law | HR, L&D, consulting |\n"
            "| International Business | Forex, trade, global markets | Export firms, MNCs |\n"
            "| Entrepreneurship | Business plans, startup ops | Founders, family business |\n"
            "| IT/Digital Business | Tech + business hybrid | IT companies, product mgmt |\n\n"
            "**Trending in 2024:**\n"
            "• BBA (Business Analytics) — high demand from data-driven companies\n"
            "• BBA (Digital Marketing) — startup and agency roles\n"
            "• BBA (Hospital Management) — healthcare sector boom\n\n"
            "💡 Most BBA programmes let you choose electives in Year 3."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "bba_best_colleges",
        "category": "BBA",
        "patterns": [
            r"best.{0,15}bba.{0,15}college",
            r"top.{0,15}bba.{0,15}(college|university|institute)",
            r"bba.{0,15}(college|university).{0,15}(best|top|rank)",
        ],
        "examples": ["Best BBA colleges in India", "Top BBA universities"],
        "response_templates": [
            "🏫 **Top BBA Colleges in India**\n\n"
            "**Tier 1 (Premium):**\n"
            "• **IIM Indore / Rohtak** — IPM (5-yr BBA+MBA via IPMAT)\n"
            "• **Shaheed Sukhdev College of Business Studies** — DU (via CUET)\n"
            "• **Christ University** — Bangalore (entrance + interview)\n"
            "• **Symbiosis BBA** (SCMS Pune) — via SET\n"
            "• **NMIMS Mumbai** — BBA via NPAT\n\n"
            "**Tier 2 (Value for Money):**\n"
            "• Amity University · LPU · Bennett University\n"
            "• Jain University Bangalore · Manipal University\n\n"
            "**Government / Affordable:**\n"
            "• Delhi University BMS/BBA colleges\n"
            "• BHU · Jamia Millia · Osmania University\n\n"
            "📌 **Key metrics:** NAAC Grade · Placement % · Avg salary · Alumni network"
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  STUDY TOOLS — always routed to LLM (generated content required)
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "study_help",
        "category": "study_tools",
        "patterns": [
            r"\bexplain\b", r"summariz", r"what is\b",
            r"\bdefine\b", r"explain concept", r"summary of",
            r"in detail", r"elaborate",
        ],
        "examples": ["Explain OOP", "What is normalization?"],
        "response_templates": [
            "📖 I'll explain that in detail. Please ask your question and I'll generate a full explanation."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "generate_quiz",
        "category": "study_tools",
        "patterns": [
            r"\bquiz\b", r"make questions", r"generate questions",
            r"create quiz", r"practice questions", r"\bmcq\b", r"test me on",
        ],
        "examples": ["Generate quiz on DBMS", "Make MCQs on networking"],
        "response_templates": [
            "🧩 Quiz Generator is ready! Tell me the topic and number of questions.\n"
            "Example: 'quiz on OS scheduling, 5 questions'"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "assignment_help",
        "category": "study_tools",
        "patterns": [
            r"\bassignment\b", r"\bhomework\b",
            r"write.{0,15}(on|about)", r"write assignment", r"create assignment",
        ],
        "examples": ["Write assignment on data structures"],
        "response_templates": [
            "✍️ Assignment Generator ready! Share the topic, word count, and any special requirements."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "code_help",
        "category": "study_tools",
        "patterns": [
            r"fix (my )?code", r"error in code", r"python error",
            r"npm error", r"stacktrace", r"debug (this|my|the)?",
            r"code (not working|broken|error)",
        ],
        "examples": ["Python IndexError", "Fix my code"],
        "response_templates": [
            "🐛 Code Helper ready! Paste your code and the error message."
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  STATIC CS / GENERAL TOPIC ANSWERS
    #  These handle common bare-keyword and "what is X" queries so the
    #  app never shows an error even when the LLM is unavailable.
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "topic_python",
        "category": "cs_topics",
        "patterns": [
            r"^\s*python\s*$",
            r"what is python\b",
            r"\bpython\b",                     # extra hit → score 2 on "what is python"
            r"tell me about python",
            r"python (language|programming|basics)",
        ],
        "examples": ["python", "what is python"],
        "response_templates": [
            "🐍 **Python** is a high-level, interpreted programming language known for its simple, readable syntax.\n\n"
            "**Key uses:**\n"
            "• 🌐 Web Development (Django, Flask)\n"
            "• 🤖 Artificial Intelligence & Machine Learning (TensorFlow, PyTorch)\n"
            "• 📊 Data Science & Analytics (Pandas, NumPy)\n"
            "• ⚙️ Automation & Scripting\n"
            "• 🔒 Cybersecurity tools\n\n"
            "**Why Python is popular:**\n"
            "✅ Beginner-friendly syntax\n"
            "✅ Huge library ecosystem (PyPI has 400k+ packages)\n"
            "✅ Cross-platform and free\n"
            "✅ Most-used language in AI/ML industry\n\n"
            "**Quick start:**\n"
            "```python\n"
            "print('Hello, World!')   # your first Python program\n"
            "```\n\n"
            "💡 Ask 'explain Python OOP' or 'Python data structures' for deeper topics."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_java",
        "category": "cs_topics",
        "patterns": [
            r"^\s*java\s*$",
            r"what is java\b",
            r"\bjava\b",                       # extra hit → score 2 on "what is java"
            r"tell me about java",
            r"java (language|programming|basics)",
        ],
        "examples": ["java", "what is java"],
        "response_templates": [
            "☕ **Java** is a class-based, object-oriented programming language designed to run on any platform (Write Once, Run Anywhere).\n\n"
            "**Key uses:**\n"
            "• 🏢 Enterprise applications (Spring, Hibernate)\n"
            "• 📱 Android app development\n"
            "• 🌐 Backend web development\n"
            "• 🔒 Banking & financial systems\n\n"
            "**Core concepts:**\n"
            "• OOP: Classes, Objects, Inheritance, Polymorphism\n"
            "• JVM (Java Virtual Machine) enables platform independence\n"
            "• Strong typing and memory management (Garbage Collector)\n\n"
            "**Quick start:**\n"
            "```java\n"
            "public class Hello {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hello, World!\");\n"
            "    }\n"
            "}\n"
            "```"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_dbms",
        "category": "cs_topics",
        "patterns": [
            r"\bdbms\b",                     # keyword anchor → higher score
            r"^\s*dbms\s*$",
            r"what is dbms\b",
            r"database management system",
            r"tell me about dbms",
        ],
        "examples": ["dbms", "what is DBMS"],
        "response_templates": [
            "🗄️ **DBMS (Database Management System)** is software that stores, manages, and retrieves structured data efficiently.\n\n"
            "**Key concepts:**\n"
            "• **Tables** — Data stored in rows and columns\n"
            "• **SQL** — Structured Query Language to interact with data\n"
            "• **ACID** — Atomicity, Consistency, Isolation, Durability\n"
            "• **Normalization** — Organizing data to reduce redundancy (1NF, 2NF, 3NF)\n"
            "• **Keys** — Primary Key, Foreign Key, Candidate Key\n\n"
            "**Popular DBMS:**\n"
            "| Type | Examples |\n"
            "|------|----------|\n"
            "| Relational (RDBMS) | MySQL, PostgreSQL, Oracle, MS SQL |\n"
            "| NoSQL | MongoDB, Redis, Cassandra |\n"
            "| In-memory | Redis, Memcached |\n\n"
            "💡 DBMS is a core subject in BCA, BTech CSE, and BBA IT specializations."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_os",
        "category": "cs_topics",
        "patterns": [
            r"\b(os|operating system)\b",                     # keyword anchor → higher score
            r"^\s*(os|operating system)\s*$",
            r"what is (an? )?operating system",
            r"what is \bos\b",
            r"explain operating system",
            r"tell me about operating system",
        ],
        "examples": ["operating system", "what is OS"],
        "response_templates": [
            "💻 **Operating System (OS)** is system software that manages hardware and software resources and provides services for computer programs.\n\n"
            "**Core functions:**\n"
            "• **Process Management** — Scheduling, creation, termination of processes\n"
            "• **Memory Management** — RAM allocation, virtual memory, paging\n"
            "• **File System** — File creation, deletion, access control\n"
            "• **Device Management** — I/O device drivers and communication\n"
            "• **Security** — User authentication, access control\n\n"
            "**Types of OS:**\n"
            "• Batch OS · Time-sharing OS · Distributed OS · Real-time OS\n\n"
            "**Popular OS examples:**\n"
            "• Windows · Linux (Ubuntu, Fedora) · macOS · Android · iOS\n\n"
            "**Key exam topics:** Scheduling algorithms (FCFS, SJF, Round Robin), "
            "Deadlock (Banker's algorithm), Virtual memory, Paging vs Segmentation."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_dsa",
        "category": "cs_topics",
        "patterns": [
            r"\b(dsa|data structures?)\b",                     # keyword anchor → higher score
            r"^\s*(dsa|data structures?)\s*$",
            r"what is (dsa|data structure)",
            r"explain (dsa|data structures?)",
            r"tell me about data structures",
        ],
        "examples": ["dsa", "what is data structures"],
        "response_templates": [
            "📐 **Data Structures & Algorithms (DSA)** is the study of organizing data efficiently and solving problems systematically.\n\n"
            "**Core Data Structures:**\n"
            "| Structure | Use Case |\n"
            "|-----------|----------|\n"
            "| Array | Fixed-size sequential data |\n"
            "| Linked List | Dynamic insertion/deletion |\n"
            "| Stack | Undo/redo, expression parsing |\n"
            "| Queue | Task scheduling, BFS |\n"
            "| Tree | Hierarchical data, BST |\n"
            "| Graph | Networks, maps, social media |\n"
            "| Hash Table | Fast lookup (O(1) avg) |\n\n"
            "**Key Algorithms:**\n"
            "• Sorting: Bubble, Merge, Quick, Heap\n"
            "• Searching: Binary Search, BFS, DFS\n"
            "• Dynamic Programming, Greedy algorithms\n\n"
            "💡 DSA is essential for cracking coding interviews at Google, Amazon, Microsoft."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_networking",
        "category": "cs_topics",
        "patterns": [
            r"\b(networking|computer networks?)\b",                     # keyword anchor → higher score
            r"^\s*(networking|computer networks?)\s*$",
            r"what is (computer )?network(ing)?\b",
            r"explain (computer )?network(ing)?",
        ],
        "examples": ["networking", "what is computer networks"],
        "response_templates": [
            "🌐 **Computer Networks** is the study of how computers communicate and share resources.\n\n"
            "**Key concepts:**\n"
            "• **OSI Model** — 7 layers: Physical, Data Link, Network, Transport, Session, Presentation, Application\n"
            "• **TCP/IP** — The foundation of the internet\n"
            "• **IP Addressing** — IPv4 (192.168.x.x) and IPv6\n"
            "• **Protocols:** HTTP/HTTPS, FTP, SMTP, DNS, DHCP\n"
            "• **Topologies:** Star, Bus, Ring, Mesh\n\n"
            "**TCP vs UDP:**\n"
            "| Feature | TCP | UDP |\n"
            "|---------|-----|-----|\n"
            "| Reliability | ✅ Guaranteed | ❌ Best-effort |\n"
            "| Speed | Slower | Faster |\n"
            "| Use | Web, Email | Video, DNS, Gaming |\n\n"
            "💡 Networks + Security = one of the highest-paying career paths in IT."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_ai_ml",
        "category": "cs_topics",
        "patterns": [
            r"\b(ai|ml|artificial intelligence|machine learning)\b",                     # keyword anchor → higher score
            r"^\s*(ai|ml|artificial intelligence|machine learning)\s*$",
            r"what is (ai|artificial intelligence|machine learning|ml)\b",
            r"explain (ai|artificial intelligence|machine learning)",
        ],
        "examples": ["AI", "what is machine learning"],
        "response_templates": [
            "🤖 **Artificial Intelligence (AI) & Machine Learning (ML)**\n\n"
            "**AI** = making machines mimic human intelligence (reasoning, learning, problem-solving).\n"
            "**ML** = a subset of AI where machines learn from data without being explicitly programmed.\n\n"
            "**ML Types:**\n"
            "• **Supervised** — Labelled data (e.g., spam detection, image classification)\n"
            "• **Unsupervised** — Unlabelled data (e.g., customer clustering)\n"
            "• **Reinforcement** — Learning by reward/punishment (e.g., game-playing bots)\n\n"
            "**Popular tools & libraries:**\n"
            "Python · TensorFlow · PyTorch · scikit-learn · Keras · Pandas · NumPy\n\n"
            "**Career in AI/ML:**\n"
            "• Data Scientist: ₹8–25 LPA\n"
            "• ML Engineer: ₹10–30 LPA\n"
            "• AI Researcher: ₹15–50 LPA (with research background)"
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_cloud",
        "category": "cs_topics",
        "patterns": [
            r"\bcloud\b",                     # keyword anchor → higher score
            r"^\s*cloud (computing)?\s*$",
            r"what is cloud\b",
            r"what is cloud (computing)?\b",
            r"\bcloud\b.{0,20}(what|computing)",
        ],
        "examples": ["cloud computing", "what is cloud"],
        "response_templates": [
            "☁️ **Cloud Computing** is the delivery of computing services (servers, storage, databases, software) over the internet on a pay-as-you-go basis.\n\n"
            "**Service Models:**\n"
            "| Model | Description | Example |\n"
            "|-------|-------------|---------|\n"
            "| IaaS | Infrastructure as a Service | AWS EC2, Azure VMs |\n"
            "| PaaS | Platform as a Service | Google App Engine, Heroku |\n"
            "| SaaS | Software as a Service | Gmail, Salesforce, Zoom |\n\n"
            "**Top Cloud Providers:**\n"
            "• ☁️ AWS (Amazon) — Market leader\n"
            "• 🔵 Microsoft Azure — Enterprise favorite\n"
            "• 🔴 Google Cloud Platform (GCP)\n\n"
            "**Certifications that pay:**\n"
            "AWS Solutions Architect · Azure AZ-900 · GCP Associate Cloud Engineer\n\n"
            "💰 Cloud skills add ₹3–8 LPA to any developer's package."
        ],
        "confidence_threshold": 1,
    },

    {
        "name": "topic_oops",
        "category": "cs_topics",
        "patterns": [
            r"\b(oop|oops|object.?oriented)\b",                     # keyword anchor → higher score
            r"^\s*(oop|oops|object oriented)\s*$",
            r"what is (oop|oops|object.?oriented)\b",
            r"explain (oop|oops|object.?oriented)",
            r"(pillars?|concepts?).{0,10}oop",
        ],
        "examples": ["oops", "what is OOP", "explain object oriented programming"],
        "response_templates": [
            "🏗️ **Object-Oriented Programming (OOP)**\n\n"
            "OOP is a programming paradigm that organises code into **objects** — "
            "reusable bundles of data (attributes) and behaviour (methods).\n\n"
            "**4 Pillars of OOP:**\n\n"
            "1. **Encapsulation** — Bundling data + methods; hiding internal details\n"
            "   ```python\n"
            "   class Student:\n"
            "       def __init__(self, name):\n"
            "           self.__name = name  # private\n"
            "   ```\n\n"
            "2. **Inheritance** — Child class inherits from parent class\n\n"
            "3. **Polymorphism** — Same method name, different behaviour\n\n"
            "4. **Abstraction** — Hiding complex implementation, showing only essentials\n\n"
            "**Languages:** Python, Java, C++, C#, Kotlin all support OOP."
        ],
        "confidence_threshold": 1,
    },

    # ──────────────────────────────────────────────────────────────────
    #  CATCH-ALL
    # ──────────────────────────────────────────────────────────────────

    {
        "name": "unknown",
        "category": "fallback",
        "patterns": [],
        "examples": [],
        "response_templates": [
            "🤔 I didn't quite understand that. Here are some things you can ask me:\n\n"
            "• **BCA:** 'What is BCA?', 'BCA career options', 'BCA vs BTech'\n"
            "• **BTech:** 'BTech branches', 'JEE eligibility', 'IIT vs NIT'\n"
            "• **BBA:** 'What is BBA?', 'BBA salary', 'BBA vs BCom'\n"
            "• **CS Topics:** 'python', 'java', 'dbms', 'operating system', 'DSA', 'OOP'\n"
            "• **Study Tools:** 'quiz on DBMS', 'explain recursion', 'fix my code'\n\n"
            "Or ask 'explain in detail' to let the AI generate a full answer."
        ],
        "confidence_threshold": 0,
    },
]


# ══════════════════════════════════════════════════════════════════════
#  ROUTING CONSTANTS
# ══════════════════════════════════════════════════════════════════════

# Intents that must go to LLM (templates are just routing prompts, not real answers)
_LLM_PREFERRED_INTENTS = {
    "study_help",
    "generate_quiz",
    "assignment_help",
    "code_help",
}

# cs_topics and college FAQ intents return templates directly — no LLM needed
# (they are NOT in _LLM_PREFERRED_INTENTS)

# Phrases that force LLM regardless of intent
_DEEP_TRIGGERS = [
    "explain in detail",
    "explain deeply",
    "deep dive",
    "in depth",
    "generate",
    "create",
    "write me",
    "make me",
    "give me an example",
    "show me code",
]


# ══════════════════════════════════════════════════════════════════════
#  CORE MATCHING LOGIC
# ══════════════════════════════════════════════════════════════════════

def score_intent(text: str, intent: Dict) -> int:
    """Return count of pattern hits for *intent* against *text*."""
    score = 0
    for pat in intent.get("patterns", []):
        try:
            if re.search(pat, text, flags=re.IGNORECASE):
                score += 1
        except re.error:
            if pat.lower() in text.lower():
                score += 1
    return score


def predict_intent(
    text: str,
    intents: Optional[List[Dict]] = None,
) -> Tuple[str, int, str]:
    """
    Returns (intent_name, score, response_template).
    Falls back to 'unknown' when no pattern fires.
    """
    if intents is None:
        intents = DEFAULT_INTENTS

    unknown_template = intents[-1]["response_templates"][0]
    best: Dict = {"name": "unknown", "score": 0, "response": unknown_template}

    for intent in intents:
        s = score_intent(text, intent)
        threshold = intent.get("confidence_threshold", 1)
        if s >= threshold and s > best["score"]:
            best = {
                "name": intent["name"],
                "score": s,
                "response": intent["response_templates"][0],
            }

    if best["score"] <= 0:
        return "unknown", 0, unknown_template

    return best["name"], best["score"], best["response"]


# ══════════════════════════════════════════════════════════════════════
#  OPTIONAL LLM FALLBACK  (Gemini → Claude)
# ══════════════════════════════════════════════════════════════════════

def llm_fallback(
    prompt: str,
    gemini_keys: Optional[List[str]] = None,
    claude_key: Optional[str] = None,
) -> Optional[str]:
    """
    Calls Gemini (rotating keys), then Claude.
    SECURITY: Keys must be passed at runtime — never hardcoded here.
    Returns None if all options fail.
    """
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        genai = None  # type: ignore

    if gemini_keys and genai is not None:
        for key in gemini_keys:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(prompt)
                text = getattr(resp, "text", None)
                if text and text.strip():
                    return text.strip()
            except Exception:
                continue

    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError:
        Anthropic = None  # type: ignore

    if claude_key and Anthropic is not None:
        try:
            client = Anthropic(api_key=claude_key)
            msg = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            if hasattr(msg, "content"):
                parts = msg.content if isinstance(msg.content, list) else [msg.content]
                text = "\n".join(getattr(p, "text", str(p)) for p in parts).strip()
                if text:
                    return text
        except Exception:
            pass

    return None


# ══════════════════════════════════════════════════════════════════════
#  PUBLIC API:  get_answer()
# ══════════════════════════════════════════════════════════════════════

def get_answer(
    user_text: str,
    gemini_keys: Optional[List[str]] = None,
    claude_key: Optional[str] = None,
) -> Dict:
    """
    Main entry point for the rules engine.

    Decision tree:
    ┌─ deep trigger phrase? ──────────────────────────► LLM
    ├─ intent in _LLM_PREFERRED_INTENTS? ────────────► LLM
    ├─ unknown intent? ──────────────────────────────► LLM
    └─ known FAQ/college intent? ────────────────────► template (zero API cost)

    Returns:
        {
            "intent":        str,   # matched intent name
            "category":      str,   # BCA / BTech / BBA / platform / study_tools
            "score":         int,   # regex hit count
            "answer":        str,   # final response text
            "used_fallback": bool,  # True if LLM was called
        }
    """
    intent_name, score, template = predict_intent(user_text)

    category = "unknown"
    for i in DEFAULT_INTENTS:
        if i["name"] == intent_name:
            category = i.get("category", "unknown")
            break

    user_lower = user_text.lower()
    forced_llm = any(trigger in user_lower for trigger in _DEEP_TRIGGERS)

    # Fast path — return template directly (no API call)
    if (
        not forced_llm
        and intent_name not in _LLM_PREFERRED_INTENTS
        and intent_name != "unknown"
        and score > 0
    ):
        return {
            "intent": intent_name,
            "category": category,
            "score": score,
            "answer": template,
            "used_fallback": False,
        }

    # LLM path
    llm_resp = llm_fallback(user_text, gemini_keys, claude_key)
    if llm_resp:
        return {
            "intent": intent_name,
            "category": category,
            "score": score,
            "answer": llm_resp,
            "used_fallback": True,
        }

    # All LLM attempts failed — best available template
    fallback_text = (
        template if intent_name != "unknown"
        else DEFAULT_INTENTS[-1]["response_templates"][0]
    )
    return {
        "intent": intent_name,
        "category": category,
        "score": score,
        "answer": fallback_text,
        "used_fallback": False,
    }


# ══════════════════════════════════════════════════════════════════════
#  UTILITY
# ══════════════════════════════════════════════════════════════════════

def export_intents_json(path: str = "intents.json") -> None:
    """Write DEFAULT_INTENTS to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(DEFAULT_INTENTS, fh, indent=2, ensure_ascii=False)
    print(f"✅ Exported {len(DEFAULT_INTENTS)} intents → {path}")


def list_intents_by_category() -> None:
    """Print a grouped summary of all loaded intents."""
    from collections import defaultdict
    groups: dict = defaultdict(list)
    for intent in DEFAULT_INTENTS:
        groups[intent.get("category", "?")].append(intent["name"])
    print("\n📋 Intent catalogue:")
    for cat, names in sorted(groups.items()):
        print(f"  [{cat}]  {' · '.join(names)}")
    print(f"\n  Total: {len(DEFAULT_INTENTS)} intents\n")


# ══════════════════════════════════════════════════════════════════════
#  COMMAND-LINE REPL  →  python rules_engine.py
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 64)
    print("  BCA AI Platform — Rules & Reasoning Engine REPL")
    print("  FAQ intents return instant answers (no API needed).")
    print("  Commands:  'list' · 'export' · 'exit'")
    print("=" * 64)
    list_intents_by_category()

    while True:
        try:
            q = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not q:
            continue
        if q.lower() in ("exit", "quit"):
            print("Bye!")
            break
        if q.lower() == "list":
            list_intents_by_category()
            continue
        if q.lower() == "export":
            export_intents_json()
            continue

        out = get_answer(q)
        mode = "🤖 LLM fallback" if out["used_fallback"] else "⚡ Rules engine"
        print(f"\n[intent={out['intent']} | category={out['category']} | score={out['score']} | {mode}]")
        print(out["answer"] + "\n")
