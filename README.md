# 🎓 AI Academic Platform

A clean, modular Streamlit-based AI study companion for all college students (BCA, BTech, BBA, BSc, BCom, MBA).

---

## 🗂️ Project Structure

```
AI-Academic-Platform/
├── app.py              ← Main Streamlit UI + 13 page functions
├── ai_engine.py        ← Gemini key rotation → Claude fallback
├── utils.py            ← All offline Python utilities
├── requirements.txt
├── README.md
└── .streamlit/
    ├── secrets.toml    ← API keys (never commit this file)
    └── config.toml     ← Streamlit server config
```

---

## 🛠️ 13 Tools (fixed sidebar order)

| # | Tool | Description |
|---|------|-------------|
| 1 | 🏠 Home | Dashboard overview |
| 2 | 📄 PDF Study Chat | Upload PDF → ask questions |
| 3 | 📝 Notes Summarizer | Long notes → concise summary |
| 4 | ✍️ Assignment Generator | Topic → full assignment |
| 5 | ✓ Assignment Checker | Grammar + AI feedback |
| 6 | 📅 Study Planner | Exam date → day-by-day schedule |
| 7 | 🧾 Exam Paper Generator | Subject → realistic exam paper |
| 8 | 💻 Code Runner | Write & run Python safely |
| 9 | 🎓 Study Recommender | Personalised resource recommendations |
| 10 | 📊 Dashboard | Session analytics |
| 11 | 💬 AI Chat | General AI assistant |
| 12 | 🧩 Quiz Generator | Topic → MCQ quiz |
| 13 | 🐛 Code Helper | Debug, explain, optimise code |

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
Create `.streamlit/secrets.toml`:
```toml
GEMINI_KEYS = ["AIza_key1", "AIza_key2", "AIza_key3"]
CLAUDE_API_KEY = "sk-ant-your_key"
```

### 3. Run
```bash
streamlit run app.py
```

---

## 🔄 AI Pipeline

```
User request
     │
     ▼
Gemini 1.5 Flash  ←  key rotation across all GEMINI_KEYS
     │  all keys fail?
     ▼
Claude 3 Haiku  ←  final fallback
     │  fails?
     ▼
Safe fallback message  ←  never crashes the app
```

---

## 🐛 Bugs Fixed

| Bug | Fix |
|-----|-----|
| `get_gemini_response()` called but never defined | Replaced with clean `_call_gemini()` in `ai_engine.py` |
| `CLAUDE_MODELS` undefined | Removed; Claude uses single model via Anthropic SDK |
| `urlrequest` / `urlerror` not imported | Replaced raw HTTP with Anthropic Python SDK |
| `ai_provider`, `claude_model`, `temperature` never initialised | Removed concept; unified pipeline in `ai_engine.py` |
| NAV_ITEMS had 17 items with 3 duplicates | Fixed to exactly 13 unique items in correct order |
| Voice assistant (speech_recognition, pyttsx3) | Completely removed |
| Real errors hidden by bare `except: pass` | All exceptions logged with `_log()` when `DEBUG=True` |
| `"All AI providers unavailable"` always shown | Real errors now visible in terminal; safe message for users |

---

## 🔐 Security

- API keys only in `.streamlit/secrets.toml`
- `.gitignore` excludes `secrets.toml`
- Code Runner blocks: `os`, `sys`, `subprocess`, `eval`, `exec`, `open()` etc.
- Errors logged to terminal in debug mode — never exposed to users
