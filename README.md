# 🎓 BCA AI Academic Platform — v3.0

An AI-powered academic companion for computer science & BCA students.  
Built with **Streamlit** · **Gemini** · **Claude** · **Rules Engine**

---

## Architecture Overview

```
User Message
     │
     ▼
┌─────────────────────────────┐
│  Rules Engine (rules_engine.py)   │  ← Fast, deterministic, zero API cost
│  keyword + regex matching         │
└─────────────┬───────────────┘
              │ match found?
         YES ─┴─ NO (or deep trigger / PDF)
         │                │
         ▼                ▼
  Template reply    ┌─────────────┐
  (instant)         │  Gemini LLM │  ← Key rotation across GEMINI_KEYS list
                    └──────┬──────┘
                           │ all keys fail?
                           ▼
                    ┌─────────────┐
                    │  Claude LLM │  ← CLAUDE_API_KEY fallback
                    └──────┬──────┘
                           │ fails?
                           ▼
                    Static error message
```

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application — all UI pages and LLM routing |
| `rules_engine.py` | Deterministic intent classifier; optional LLM fallback stub |
| `intents.json` | Intent schema (patterns, examples, response templates) |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml` | API key storage (never commit to git) |

---

## Setup

### 1 · Install dependencies

```bash
pip install -r requirements.txt
```

### 2 · Configure API keys

Edit `.streamlit/secrets.toml` — **never commit this file**:

```toml
# One or more Gemini keys (rotated automatically)
GEMINI_KEYS = ["AIza...", "AIza...", "AIza..."]

# Claude fallback
CLAUDE_API_KEY = "sk-ant-..."
```

Keys are loaded at runtime via `st.secrets`. They are **never** logged or echoed.

### 3 · Run

```bash
streamlit run app.py
```

---

## Rules Engine

`rules_engine.py` classifies messages **before** any API call.

| Intent | Example triggers | Action |
|---|---|---|
| `greeting` | hi, hello, namaste | Template reply |
| `ask_model` | "which model are you using" | Template reply |
| `check_quota` | quota, rpm, rate limit | Template reply |
| `set_keys` | streamlit secrets, secrets.toml | Template reply |
| `explain_error` | "all api attempts failed" | Template reply |
| `offline_options` | offline, ollama, run locally | Template reply |
| `study_help` | explain, what is, define | LLM (needs content) |
| `generate_quiz` | quiz, mcq, make questions | LLM (needs content) |
| `code_help` | fix code, python error | LLM (needs content) |
| `assignment_help` | assignment, homework | LLM (needs content) |
| `unknown` | anything else | LLM fallback |

**Deep triggers** — phrases like `"explain in detail"`, `"generate"`, `"create"` always escalate to LLM even for otherwise-templated intents.

---

## API Key Rotation

- Gemini keys are stored as a list and rotated round-robin via `st.session_state.gemini_key_index`.
- If a key raises an exception, the next key is tried automatically.
- Claude is only called if all Gemini keys fail.
- Quota errors from a shared Google project affect all keys — use separate projects for true independent quotas.

---

## Features

| Page | Description |
|---|---|
| 🏠 Home | Welcome & feature overview |
| 💬 AI Chat | General chat with mode switching & voice input |
| 📄 PDF Study Chat | Upload PDF and ask questions about it |
| 🧩 Quiz Generator | Auto-generate MCQs on any CS topic |
| 🐛 Code Helper | Paste code → get debug analysis |
| 📝 Notes Summarizer | Convert notes to exam-ready bullets |
| ✍️ Assignment Generator | Generate structured academic assignments |
| ✓ Assignment Checker | Paste your assignment for AI feedback |
| 📅 Study Planner | Day-by-day schedule with exam countdown |
| 🧾 Exam Paper Generator | Generate full exam papers with mark scheme |
| 💻 Code Runner | Execute Python code in a sandbox |
| 🎓 Study Recommender | Personalised learning path suggestions |
| 📊 Dashboard | Session analytics & feature usage |

---

## Security Notes

- API keys are read **only** from `st.secrets` at runtime.
- No keys are printed to logs, echoed in responses, or stored in session state in plain text.
- Code Runner runs user code in a subprocess with a 10-second timeout and no network access.
- The rules engine never calls any external service for template-matched intents.

---

## Running Tests (quick REPL)

```bash
python rules_engine.py
```

Expected behaviour:

| Input | Intent | Calls LLM? |
|---|---|---|
| `hi` | `greeting` | No |
| `Why does it say all API attempts failed` | `explain_error` | No |
| `Can I run model offline on Streamlit Cloud?` | `offline_options` | No |
| `Explain OOP in detail` | `study_help` | Yes ("in detail" trigger) |
| `Generate quiz on DBMS` | `generate_quiz` | Yes (LLM-preferred intent) |
