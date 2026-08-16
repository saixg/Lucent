# Lucent 🔍

> **An independent verification layer and conversational fact-checking partner for the internet.**

Lucent helps anyone bring suspicious content — whether it's a viral claim, a news article URL, a screenshot, or an image — and receive a clear, evidence-backed explanation of what is actually true, rather than just a simple real/fake label.

---

## 🌟 What We're Building

Every day, people encounter ambiguous or misleading content across social media and the web:
- Out-of-context quotes and unverified viral claims
- Manipulated or AI-generated images
- Misleading articles and altered headlines

Today, the options are either blind trust, complete skepticism, or tedious manual research across multiple sources. **Lucent solves this by acting as your verification partner**:

1. **Multimodal Input**: Submit raw claims, article URLs, or upload images.
2. **Deep Claim Extraction & Forensics**: Identifies core checkable claims and runs reverse search, metadata inspection, and forensic consistency checks.
3. **Multi-Source Evidence Gathering**: Searches credible web sources and cross-references facts in real time.
4. **Structured Verdicts**: Provides clear verdicts (`True`, `False`, `Misleading`, `Missing Context`, `Altered/Manipulated`, `AI-Generated`, `Unverifiable`) along with confidence ratings and cited source links.
5. **Interactive Follow-Up Investigation**: Ask conversational follow-ups (e.g. *"Why is this misleading?"*, *"What actually happened in the original video?"*) without losing context or having to re-submit.

---

## 🏗️ Tech Stack

### Frontend
- **Framework**: [Next.js](https://nextjs.org/) (App Router, TypeScript)
- **Styling**: Tailwind CSS & Modern UI Components
- **Features**: Interactive verification dashboard, real-time investigation threads, evidence link cards.

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Database & Storage**: PostgreSQL (SQLAlchemy / Supabase)
- **Background Tasks**: Celery & Redis
- **AI & Analysis**: LLM-powered claim extraction & verdict synthesis, search APIs, and image forensics.

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # Configure your API keys and DB credentials
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000` to start verifying content.

---

## 📄 License

MIT License.
