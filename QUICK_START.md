# ⚡ BCA AI Platform v3.0 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run app_v3_upgraded.py
```

### Step 3: Configure Secrets (Optional)
If you haven't done this already, your API keys go in `.streamlit/secrets.toml`:

```toml
GEMINI_KEYS = [
  "your-first-gemini-key",
  "your-second-gemini-key"
]

GROQ_API_KEY = "your-groq-api-key"
```

### Step 4: Start Learning!
Open http://localhost:8501 and click 🏠 Home

---

## 🎯 First 5 Things to Try

### 1️⃣ Change Your Name (Personalization)
- Click sidebar: 👤 User Profile
- Enter your name
- AI will remember and use it!

### 2️⃣ Switch AI Models (Multi-Provider)
- Settings → AI Configuration
- Select: Gemini Flash, Gemini Pro, Groq Llama, etc.
- Instant switching, no reload needed!

### 3️⃣ Ask with Voice (Voice Assistant)
- Go to 💬 AI Chat
- Click 🎤 Voice button
- Speak your question
- (Requires: pip install speechrecognition)

### 4️⃣ Run Python Code (Code Executor)
- Go to 💻 Code Runner
- Paste Python code
- Click ▶️ Run Code
- Get instant output!

### 5️⃣ Check Your Assignment (AI Feedback)
- Go to ✓ Assignment Checker
- Paste your assignment
- Click 🔍 Check Assignment
- Get detailed feedback with improvements!

---

## 📍 Navigation Overview

```
Home (🏠)
├── 💬 AI Chat - Interactive conversations
├── 📄 PDF Chat - Learn from documents
├── 🧩 Quiz - Generate practice tests
├── 🐛 Code Helper - Debug code
├── 📝 Notes - Summarize notes
├── ✍️ Assignment Gen - Generate assignments
├── ✓ Assignment Checker - Get feedback (NEW)
├── 📅 Study Planner - Create study schedules
├── 🧾 Exam Gen - Mock exam papers
├── 💻 Code Runner - Execute Python (NEW)
├── 🎓 Study Recommender - Learning paths (NEW)
└── 📊 Dashboard - Progress analytics
```

---

## 💡 Smart Tool Routing (Auto-Detection)

You don't have to navigate manually! Just talk to the AI:

### Examples:
- **"Create MCQs on databases"** → Auto-switches to Quiz Generator
- **"Debug my Python code"** → Auto-switches to Code Debugger
- **"Summarize these notes"** → Auto-switches to Notes Summarizer
- **"Plan my study for 2 weeks"** → Auto-switches to Study Planner

Try it in 💬 AI Chat!

---

## 🎤 Voice Commands (If Installed)

### Enable Voice:
```bash
pip install speechrecognition pyttsx3
# Then restart the app
```

### Use Voice:
1. 💬 AI Chat page
2. Click 🎤 Voice button
3. Speak your question
4. Wait for response
5. Click 🔊 Read Aloud to hear it

---

## 📊 Track Your Progress

### Session Dashboard:
- **Questions Asked** - Number of questions
- **Topics Studied** - Unique topics covered
- **Session Duration** - Time spent learning
- **Feature Usage** - Which tools you use
- **Recent Activity** - Last 5 interactions

All auto-tracked! Check 📊 Dashboard.

---

## 📥 Export Your Work

### Download Chat:
1. Sidebar: 💾 Export
2. Choose: 📄 MD (Markdown) or 📦 JSON
3. Save for backup or sharing

### Download Generated Files:
- ✍️ Assignments → Download button
- 🧾 Exam Papers → Download button
- ✓ Checker Feedback → Download button

---

## ⚙️ Sidebar Settings

### AI Configuration:
- Select Model (Gemini or Groq)
- Adjust Temperature (0=Precise, 1=Creative)
- Voice settings

### User Profile:
- Set your name
- View learning stats
- See preferred subjects (auto-tracked)

### Session Snapshot:
- Questions asked
- Topics studied
- Session duration

---

## 🐛 Common Issues & Fixes

### "API key not found"
- **Fix:** Add GEMINI_KEYS or GROQ_API_KEY to .streamlit/secrets.toml
- **Restart** the app after saving secrets

### "Voice not working"
- **Fix:** `pip install speechrecognition`
- Make sure microphone is working
- Check browser permissions

### "PDF not reading"
- **Fix:** `pip install pypdf`
- Try a different PDF
- Make sure it contains text (not scanned images)

### "Code Runner errors"
- Make sure Python syntax is correct
- Try simpler code first
- Check imports are available

### "Slow responses"
- Try Groq Llama 3.1 (fastest)
- Lower temperature to 0.3
- Disable typing animation

---

## 📚 Learning Roadmap

### Day 1-2: Explore Basics
- [ ] Change name in profile
- [ ] Try AI Chat with different modes
- [ ] Switch between AI models
- [ ] Ask a voice question

### Day 3-4: Practice
- [ ] Generate and take a quiz
- [ ] Upload a PDF and chat with it
- [ ] Summarize some notes
- [ ] Try code debugging

### Day 5-6: Create & Check
- [ ] Generate an assignment
- [ ] Check it with Assignment Checker
- [ ] Generate mock exam paper
- [ ] Run Python code

### Day 7+: Master & Learn
- [ ] Get personalized recommendations
- [ ] Follow study planner
- [ ] Check dashboard progress
- [ ] Explore advanced features

---

## 🎓 Pro Tips

### Tip 1: Use Specific Study Modes
Different modes give different responses:
- "Programming Helper" for learning
- "Code Debugger" for fixing bugs
- "Quiz Generator" for testing
- "Exam Prep" for mock exams

### Tip 2: Provide Context
Instead of: "What is recursion?"
Try: "Explain recursion with a Python example showing factorial"
Better responses = More learning!

### Tip 3: Use Code Runner for Testing
Don't just ask about code, test it!
- Generate code with AI
- Run it in Code Runner
- See actual output
- Modify and test again

### Tip 4: Download Everything
- Download chat history as backup
- Download generated assignments
- Download exam papers for offline study
- Keep your work organized

### Tip 5: Check Assignment Before Submitting
- Always use ✓ Assignment Checker
- Fix issues before submission
- Improve grades with feedback
- Learn proper academic writing

---

## 🔄 Keyboard Shortcuts

- `Ctrl+C` - Stop Streamlit (in terminal)
- `R` - Refresh page (if needed)
- Enter in chat - Send message (fastest way)

---

## 📞 Need Help?

### Check These First:
1. **UPGRADE_GUIDE_v3.md** - Full documentation
2. **Error message** - Read the red error box
3. **Sidebar Help** - Hover over feature icons

### Still stuck?
- Check `.streamlit/secrets.toml` for API keys
- Verify Python version >= 3.8
- Try: `pip install -r requirements.txt`
- Restart the app

---

## 🎉 You're Ready!

Your BCA AI Platform is ready to use!

### Next Steps:
1. Open http://localhost:8501
2. Explore the Home page
3. Try 💬 AI Chat
4. Build your learning journey!

---

**Happy Learning! 🚀**

*BCA AI Platform v3.0 - Made for students, by students*
