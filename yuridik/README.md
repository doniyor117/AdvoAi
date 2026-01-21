# 🎯 Imtiyoz-AI

> AI-powered Smart Assistant for Uzbek Entrepreneur Privileges
> **Milliy AI Xakaton 2026 - Task T-3**

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Team](https://img.shields.io/badge/team-LumenAI-orange)

</div>

## 📋 Overview

**Imtiyoz-AI** helps small business owners in Uzbekistan discover government subsidies, grants, and tax holidays by:

1. **RAG-based Chat** - Query legal documents in natural language (Uzbek/Russian)
2. **Scout Agent** - Autonomous discovery of new decrees from lex.uz
3. **Business Matching** - Personalized privilege recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Groq API key OR Google AI API key

### 1. Clone & Setup

```bash
cd yuridik

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env
# Edit .env with your API key
```

### 2. Seed Database

```bash
# From backend directory
python -m scripts.seed_database
```

### 3. Start Backend

```bash
# From backend directory
uvicorn app.main:app --reload --port 8000
```

### 4. Start Frontend (New Terminal)

```bash
cd frontend
npm install
npm run dev
```

### 5. Open App

Visit [http://localhost:3000](http://localhost:3000)

## 🏗️ Architecture

```
yuridik/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── config.py        # Settings
│   │   ├── api/routers/     # API endpoints
│   │   ├── rag_engine/      # RAG & chunking
│   │   └── scout_agent/     # Auto-discovery
│   ├── data/
│   │   └── chroma_db/       # Vector store
│   └── scripts/
│       └── seed_database.py # Data seeding
│
└── frontend/                # Next.js Frontend
    └── src/
        ├── app/             # Pages
        ├── components/      # React components
        └── lib/             # API client
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | RAG chat query |
| `/api/scout/status` | GET (SSE) | Live scout updates |
| `/api/scout/trigger` | POST | Manual scout trigger |
| `/health` | GET | Health check |

## 📜 Pre-loaded Decrees

| ID | Title |
|----|-------|
| PQ-60 | Yoshlar tadbirkorligini qo'llab-quvvatlash |
| PD-50 | Kichik va o'rta biznes ulushini oshirish |
| PQ-306 | Kichik biznesni uzluksiz qo'llab-quvvatlash |
| IT-PARK | IT Park rezidentlari uchun soliq imtiyozlari |
| FERMER | Fermer xo'jaliklarini qo'llab-quvvatlash |

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, ChromaDB
- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **LLM**: Groq (GPT-OSS-120B) or Google Gemini
- **Scraper**: DuckDuckGo Search, BeautifulSoup

## 👥 Team LumenAI

Built for Milliy AI Xakaton (Samarkand 2026)

---

<div align="center">
Made with ❤️ in Uzbekistan
</div>
