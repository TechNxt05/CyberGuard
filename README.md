# 🛡️ CyberGuardAI One: Authentic Cyber Defense

**The First "Hand-in-Hand" AI Agent for Cybercrime Resolution.**

CyberGuardAI One is not just a chatbot. It is a **Multi-Agent Orchestrator** that actively researches the open internet, verifies facts, and guides users through the complex legal and technical steps of recovering from cybercrimes (UPI Fraud, Sextortion, Ransomware, etc.).

![CyberGuard Architecture](https://placehold.co/1200x400/000000/FFF?text=CyberGuard+Architecture)

---

## 🚀 Key Features

### 1. **Authentic Research & Knowledge Engine** 🔍 *(New)*
The system stays relevant by connecting to the real world:
-   **Multi-Source Research Agent**: Automatically scours **DuckDuckGo**, **Reddit**, and **Twitter (X)** to validate scams and find the absolute latest recovery forms.
-   **Authenticity Check**: If a scam is trending (e.g., "FedEx Customs Scam 2025"), the AI validates your suspicion by citing real victim reports from the last 24 hours.

### 2. **CyberResolve Agentic Workflow** 🧩
A graph of specialized agents working together:
-   **Understanding Agent**: Forensically analyzes your story to extract key data (Transaction IDs, Attack Vectors).
-   **Strategy Agent**: Creates a custom **Lifecycle Plan** (Containment -> Reporting -> Recovery) based on verified playbooks.
-   **Authority Mapper**: Identifies the *exact* Nodal Officer for your bank/platform using live search.
-   **Guidance Agent**: Provides step-by-step, click-by-click navigation for confusing official portals (e.g., cybercrime.gov.in).

### 3. **ScamShield Detector** 🛡️
-   **Multi-Modal Analysis**: Upload screenshots or paste messages.
-   **Cross-Reference**: Checks the input against a database of 500+ known Indian scam patterns AND performs a live web search to confirm validity.
-   **Explainability**: Tells you *why* it's a scam in simple language with logic, mechanism, and consequences.

### 4. **"The Exact Solution"** 🔗
-   **One-Click Portals**: Sidebar tasks link directly to the *correct* official dispute pages (validated by AI).
-   **Smart Guidance**: Step-by-step navigation for confused users (e.g., "Where is the 'Cyber Cell' button?").
-   **Real-time Updates**: Analysis and Tasks update dynamically as the conversation progresses.

### 5. **Advanced User Interface** 💻
-   **Dashboard**: Manage multiple cases with status tracking.
-   **Case View**: Split-screen interface with Chat, Tasks, and Analysis Panel (50-50 split).
-   **Dark Mode**: Sleek, modern "Glassmorphism" design built with TailwindCSS and Shadcn/UI.

---

## 🛠️ Technology Stack

-   **Frontend**: Next.js 14, TailwindCSS, Shadcn/UI (Modern Glassmorphism Design).
-   **Backend**: Python FastAPI, LangGraph (Agent Orchestration).
-   **AI Core**: Groq Llama-3 (High Speed), Google Gemini (Multimodal).
-   **Tools**: DuckDuckGo Search, PRAW (Reddit), Tweepy (Twitter), BeautifulSoup4.
-   **Database**: MongoDB Atlas (Vector Store + State Persistence).
-   **Authentication**: Clerk.

---

## ⚡ Deployment Guide

This project is optimized for deployment on **Vercel** (Frontend) and **Render** (Backend).

### 1. Prerequisites
-   GitHub Account (Push this code to a repo).
-   MongoDB Atlas Cluster (Get the Connection String).
-   API Keys: `GROQ_API_KEY`, `GEMINI_API_KEY`, `CLERK_...` keys.

### 2. Backend Deployment (Render)
1.  Create a **New Web Service** on [Render](https://render.com).
2.  Connect your GitHub Repository.
3.  **Settings**:
    -   **Root Directory**: `backend`
    -   **Build Command**: `pip install -r requirements.txt`
    -   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4.  **Environment Variables**: Add all keys from your `backend/.env` file. (GROQ_API_KEY, MONGODB_URI, etc.).

### 3. Frontend Deployment (Vercel)
1.  Import the project in [Vercel](https://vercel.com).
2.  **Settings**:
    -   **Root Directory**: `frontend`
    -   **Framework Preset**: Next.js
3.  **Environment Variables**: Add keys from `frontend/.env`.
    -   `NEXT_PUBLIC_API_URL`: Set this to your **Render Backend URL** (e.g., `https://cyberguard-backend.onrender.com`).
4.  **Deploy**!

---

## 🏃‍♂️ Local Development

### Backend
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

**Built for a Safer Digital India.**
