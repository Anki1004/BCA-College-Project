"""
ai_engine.py — AI Academic Platform
=====================================
7-tier fallback cascade
  1. OpenRouter #1 → stepfun/step-3.5-flash:free       (fast, general)
  2. OpenRouter #2 → arcee-ai/trinity-large-preview:free (coding/tech)
  3. OpenRouter #3 → liquid/lfm-2.5-1.2b-thinking:free  (Liquid AI thinking)
  4. Gemini (4 keys, round-robin)                        (Google)
  5. Claude (haiku)                                      (Anthropic)
  6. Rules Engine (FAQ fallback)                          (deterministic)
  7. Static error message

Public surface
  get_response(prompt, system_prompt, fallback_msg) -> (text, source)
  ai_available() -> bool
"""

from __future__ import annotations

import re
import streamlit as st

# ── Toggle for local development ─────────────────────────────────────────────
DEBUG: bool = True

# ── OpenRouter model cascade ─────────────────────────────────────────────────
OPENROUTER_MODELS: list[str] = [
    "stepfun/step-3.5-flash:free",
    "arcee-ai/trinity-large-preview:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
]


# ─────────────────────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _log(tag: str, msg: str) -> None:
    if DEBUG:
        print(f"[AI-ENGINE | {tag}] {msg}", flush=True)


def _load_openrouter_key() -> str | None:
    """Read OPENROUTER_API_KEY from st.secrets."""
    try:
        key = str(st.secrets["OPENROUTER_API_KEY"]).strip()
        return key if key else None
    except Exception as exc:
        _log("KEYS", f"OPENROUTER_API_KEY missing — {exc}")
        return None


def _load_gemini_keys() -> list[str]:
    """
    Read GEMINI_KEYS from st.secrets.
    Accepts both a TOML array  →  ["key1", "key2"]
    and a comma-separated string  →  "key1,key2"
    """
    try:
        raw = st.secrets["GEMINI_KEYS"]
        if isinstance(raw, str):
            keys = [k.strip() for k in raw.split(",") if k.strip()]
        else:
            keys = [str(k).strip() for k in raw if str(k).strip()]
        _log("KEYS", f"{len(keys)} Gemini key(s) loaded")
        return keys
    except Exception as exc:
        _log("KEYS", f"GEMINI_KEYS missing or unreadable — {exc}")
        return []


def _load_claude_key() -> str | None:
    """Read CLAUDE_API_KEY from st.secrets."""
    try:
        key = str(st.secrets["CLAUDE_API_KEY"]).strip()
        return key if key else None
    except Exception as exc:
        _log("KEYS", f"CLAUDE_API_KEY missing — {exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  OpenRouter (3 models in cascade)
# ─────────────────────────────────────────────────────────────────────────────

def _call_openrouter(prompt: str, system_prompt: str) -> tuple[str | None, str | None]:
    """
    Try each OpenRouter free model in order.
    Returns (response_text, model_name) on first success; (None, None) if all fail.
    Uses the requests library for a simple OpenAI-compatible POST.
    """
    try:
        import requests  # already in requirements
    except ImportError:
        _log("OPENROUTER", "requests not installed")
        return None, None

    key = _load_openrouter_key()
    if not key:
        return None, None

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    for model in OPENROUTER_MODELS:
        try:
            _log("OPENROUTER", f"Trying → {model}")
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
                timeout=45,
            )
            if resp.status_code != 200:
                _log("OPENROUTER", f"{model} HTTP {resp.status_code}: {resp.text[:200]}")
                continue

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                _log("OPENROUTER", f"{model} returned no choices")
                continue

            text = (choices[0].get("message", {}).get("content") or "").strip()
            if text:
                _log("OPENROUTER", f"✓ Success with {model}")
                return text, model
            _log("OPENROUTER", f"{model} returned empty content")
        except Exception as exc:
            _log("OPENROUTER", f"{model} FAILED: {type(exc).__name__}: {exc}")

    _log("OPENROUTER", "All 3 models exhausted")
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
#  Gemini (4 keys, round-robin)
# ─────────────────────────────────────────────────────────────────────────────

def _call_gemini(prompt: str, system_prompt: str) -> str | None:
    """
    Rotate through all Gemini keys, trying gemini-1.5-flash on each.
    Returns response text on first success; None if all keys fail.
    """
    try:
        import google.generativeai as genai  # type: ignore
    except ImportError:
        _log("GEMINI", "google-generativeai not installed — run: pip install google-generativeai")
        return None

    keys = _load_gemini_keys()
    if not keys:
        return None

    num   = len(keys)
    start = int(st.session_state.get("_gemini_key_index", 0)) % num
    full_prompt = f"{system_prompt}\n\n{prompt}"

    for i in range(num):
        idx = (start + i) % num
        try:
            _log("GEMINI", f"Trying key[{idx}] → gemini-1.5-flash")
            genai.configure(api_key=keys[idx])
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={"temperature": 0.7, "max_output_tokens": 2048},
            )
            response = model.generate_content(full_prompt)
            text = (response.text or "").strip()
            if text:
                st.session_state["_gemini_key_index"] = (idx + 1) % num
                _log("GEMINI", f"✓ Success with key[{idx}]")
                return text
            _log("GEMINI", f"key[{idx}] returned empty response")
        except Exception as exc:
            _log("GEMINI", f"key[{idx}] FAILED: {type(exc).__name__}: {exc}")

    _log("GEMINI", "All keys exhausted")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Claude (haiku)
# ─────────────────────────────────────────────────────────────────────────────

def _call_claude(prompt: str, system_prompt: str) -> str | None:
    """
    Call Claude 3 Haiku via the official Anthropic SDK.
    Returns response text on success; None on failure.
    """
    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError:
        _log("CLAUDE", "anthropic not installed — run: pip install anthropic")
        return None

    key = _load_claude_key()
    if not key:
        return None

    try:
        _log("CLAUDE", "Trying claude-3-haiku-20240307")
        client = Anthropic(api_key=key, timeout=45.0)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )
        text = "\n".join(
            b.text for b in response.content if b.type == "text"
        ).strip()
        if text:
            _log("CLAUDE", "✓ Success")
            return text
        _log("CLAUDE", "Empty response")
    except Exception as exc:
        _log("CLAUDE", f"FAILED: {type(exc).__name__}: {exc}")

    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Rules Engine (deterministic FAQ fallback)
# ─────────────────────────────────────────────────────────────────────────────

_FAQ_RULES: list[tuple[list[str], str]] = [
    # Programming basics
    (
        ["what is python", "explain python", "define python"],
        "**Python** is a high-level, interpreted programming language known for its clear syntax and readability. "
        "It supports multiple paradigms (procedural, OOP, functional) and is widely used in web development, "
        "data science, AI/ML, and automation. Key features: dynamic typing, garbage collection, extensive standard library.",
    ),
    (
        ["what is java", "explain java", "define java"],
        "**Java** is a class-based, object-oriented programming language designed for portability (Write Once, Run Anywhere). "
        "It runs on the JVM and is used for enterprise applications, Android development, and large-scale systems. "
        "Key features: strong typing, automatic memory management, multithreading support.",
    ),
    (
        ["what is html", "explain html"],
        "**HTML (HyperText Markup Language)** is the standard markup language for creating web pages. "
        "It describes the structure of a page using elements like headings, paragraphs, links, images, and forms. "
        "HTML5 is the latest version, adding semantic elements, audio/video, and canvas support.",
    ),
    (
        ["what is css", "explain css"],
        "**CSS (Cascading Style Sheets)** controls the visual presentation of HTML documents — layout, colors, fonts, spacing. "
        "It separates content from design, supports responsive layouts via media queries, and modern features like Flexbox and Grid.",
    ),
    (
        ["what is javascript", "explain javascript"],
        "**JavaScript** is a dynamic, interpreted language primarily used for interactive web pages. "
        "It runs in browsers and on servers (Node.js), supporting event-driven and asynchronous programming. "
        "Key features: first-class functions, prototypal inheritance, DOM manipulation.",
    ),
    # CS theory
    (
        ["what is dbms", "explain dbms", "what is database management"],
        "**DBMS (Database Management System)** is software that stores, retrieves, and manages data in databases. "
        "Types include Relational (MySQL, PostgreSQL), NoSQL (MongoDB), and Object-Oriented. "
        "Key concepts: ACID properties, normalization, SQL queries, indexing, transactions.",
    ),
    (
        ["what is operating system", "explain os", "what is os"],
        "**An Operating System** is system software that manages hardware resources and provides services to programs. "
        "Key functions: process management, memory management, file systems, I/O handling, security. "
        "Examples: Windows, Linux, macOS. Concepts: scheduling, paging, virtual memory, deadlocks.",
    ),
    (
        ["what is data structure", "explain data structure", "what are data structures"],
        "**Data Structures** are ways of organizing and storing data for efficient access and modification. "
        "Common types: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables. "
        "Choosing the right structure depends on the operations needed (search, insert, delete) and their time complexity.",
    ),
    (
        ["what is algorithm", "explain algorithm", "what are algorithms"],
        "**An Algorithm** is a step-by-step procedure for solving a problem or performing a computation. "
        "Key concepts: time complexity (Big-O), space complexity, sorting (QuickSort, MergeSort), "
        "searching (Binary Search), dynamic programming, greedy algorithms, graph traversals (BFS, DFS).",
    ),
    (
        ["what is oops", "explain oops", "what is object oriented", "what is oop"],
        "**OOP (Object-Oriented Programming)** is a paradigm based on objects containing data (attributes) and code (methods). "
        "Four pillars: **Encapsulation** (data hiding), **Abstraction** (interface vs implementation), "
        "**Inheritance** (code reuse via parent-child classes), **Polymorphism** (same interface, different behavior).",
    ),
    (
        ["what is machine learning", "explain machine learning", "what is ml"],
        "**Machine Learning** is a subset of AI where systems learn patterns from data without explicit programming. "
        "Types: Supervised (classification, regression), Unsupervised (clustering, dimensionality reduction), "
        "Reinforcement Learning. Common algorithms: Linear Regression, Decision Trees, Neural Networks, SVM, k-NN.",
    ),
    (
        ["what is cloud computing", "explain cloud computing"],
        "**Cloud Computing** delivers computing services (servers, storage, databases, networking, AI) over the internet. "
        "Models: IaaS, PaaS, SaaS. Deployment: Public, Private, Hybrid. "
        "Major providers: AWS, Azure, Google Cloud. Benefits: scalability, cost efficiency, global availability.",
    ),
    (
        ["what is networking", "explain networking", "what is computer network"],
        "**Computer Networking** connects devices to share resources and communicate. "
        "Key models: OSI (7 layers), TCP/IP (4 layers). Protocols: HTTP, TCP, UDP, DNS, DHCP. "
        "Concepts: IP addressing, subnetting, routing, switching, firewalls, VPN.",
    ),
    (
        ["what is sql", "explain sql"],
        "**SQL (Structured Query Language)** is used to manage and query relational databases. "
        "Key commands: SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY, HAVING, CREATE TABLE. "
        "Advanced: subqueries, indexing, stored procedures, triggers, views, normalization (1NF–BCNF).",
    ),
    # Academic help
    (
        ["how to study", "study tips", "how to prepare for exam"],
        "**Effective Study Strategies:**\n"
        "1. **Active Recall** — test yourself instead of re-reading\n"
        "2. **Spaced Repetition** — review at increasing intervals\n"
        "3. **Pomodoro Technique** — 25 min focus + 5 min break\n"
        "4. **Feynman Technique** — explain concepts simply\n"
        "5. **Past Papers** — practice under timed conditions\n"
        "6. **Teach Others** — solidifies understanding",
    ),
    (
        ["what is normalization", "explain normalization", "database normalization"],
        "**Database Normalization** reduces redundancy and improves data integrity.\n"
        "- **1NF**: Atomic values, no repeating groups\n"
        "- **2NF**: 1NF + no partial dependencies\n"
        "- **3NF**: 2NF + no transitive dependencies\n"
        "- **BCNF**: Every determinant is a candidate key\n"
        "Trade-off: higher normal forms reduce redundancy but may need more JOINs.",
    ),
]


def _rules_engine(prompt: str) -> str | None:
    """
    Match the user prompt against FAQ rules.
    Returns a deterministic answer if matched; None otherwise.
    """
    lower = prompt.lower().strip()
    # Strip common prefixes the AI prompt builder may add
    for prefix in ["generate 5 mcqs on the following topic:\n\n",
                   "summarise the following notes:\n\n",
                   "write a well-structured academic assignment on:\n\n",
                   "debug and explain the following code:\n\n"]:
        if lower.startswith(prefix):
            lower = lower[len(prefix):]

    for patterns, answer in _FAQ_RULES:
        if any(p in lower for p in patterns):
            _log("RULES", f"✓ Matched FAQ pattern")
            return answer

    _log("RULES", "No FAQ match")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def get_response(
    prompt:        str,
    system_prompt: str = "You are a helpful academic AI assistant for college students.",
    fallback_msg:  str | None = None,
) -> tuple[str, str]:
    """
    Main entry point used by app.py.

    Cascade order:
      1. OpenRouter #1  stepfun/step-3.5-flash:free
      2. OpenRouter #2  arcee-ai/trinity-large-preview:free
      3. OpenRouter #3  liquid/lfm-2.5-1.2b-thinking:free
      4. Gemini          (4 keys, round-robin)
      5. Claude          (haiku)
      6. Rules Engine    (FAQ deterministic fallback)
      7. Static error message

    Returns (answer, source) where source is one of:
        "openrouter" — answered by an OpenRouter model
        "gemini"     — answered by Gemini
        "claude"     — answered by Claude
        "rules"      — answered by deterministic FAQ engine
        "offline"    — caller-supplied fallback_msg was used
        "error"      — everything failed, generic message returned
    """
    # 1–3. OpenRouter (3 free models in cascade)
    text, model = _call_openrouter(prompt, system_prompt)
    if text:
        return text, "openrouter"

    # 4. Gemini (round-robin keys)
    text = _call_gemini(prompt, system_prompt)
    if text:
        return text, "gemini"

    # 5. Claude (haiku)
    text = _call_claude(prompt, system_prompt)
    if text:
        return text, "claude"

    # 6. Rules Engine — deterministic FAQ
    text = _rules_engine(prompt)
    if text:
        return text, "rules"

    # 6b. Caller-supplied offline fallback
    if fallback_msg:
        return fallback_msg, "offline"

    # 7. Safe generic message — NEVER show raw exception to user
    _log("ENGINE", f"All providers failed. Prompt preview: {prompt[:80]}")
    return (
        "⚠️ The AI service is temporarily unavailable. "
        "Please check your API keys in `.streamlit/secrets.toml` and try again in a moment.",
        "error",
    )


def ai_available() -> bool:
    """Return True if at least one provider key is configured."""
    return bool(_load_openrouter_key()) or bool(_load_gemini_keys()) or bool(_load_claude_key())
