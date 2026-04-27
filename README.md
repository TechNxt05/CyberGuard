# 🛡️ CyberGuardAI One: Authentic Cyber Defense

**The Production-Grade, Multimodal AI Investigator for Cybercrime Resolution.**

CyberGuardAI One is a powerful **Multi-Agent Orchestrator** and multimodal investigation system that actively researches the open internet, analyzes evidence (vision, text), and guides users through the complex legal and technical steps of recovering from cybercrimes (UPI Fraud, Sextortion, Ransomware, etc.).

![CyberGuard Architecture](https://placehold.co/1200x400/000000/FFF?text=CyberGuard+One+Architecture)

---

## 🚀 Key Features

### 1. **Multimodal Evidence Analysis (Vision)** 👁️ *(New)*
- **Vision Analysis**: Upload screenshots of suspicious messages, emails, or transactions. Powered by Gemini 1.5, it extracts text, identifies URLs, and pinpoints threat vectors instantly.
- **Context-Aware Processing**: Seamlessly merges visual and textual evidence for a comprehensive case understanding.

### 2. **Authentic Research & Knowledge Engine** 🔍 
The system stays relevant by connecting to the real world:
- **Multi-Source Research Agent**: Automatically scours **DuckDuckGo**, **Reddit**, and **Twitter (X)** to validate scams and find the absolute latest recovery forms.
- **Authenticity Check**: Validates your suspicion by citing real victim reports from the last 24 hours.

### 3. **CyberResolve Agentic Workflow** 🧩
A graph of specialized agents working together:
- **Understanding Agent**: Forensically analyzes your story and evidence to extract key data (Transaction IDs, Attack Vectors, Entities).
- **Strategy Agent**: Creates a custom **Lifecycle Plan** (Containment -> Reporting -> Recovery) based on verified playbooks.
- **Authority Mapper**: Identifies the *exact* Nodal Officer for your bank/platform using live search.
- **Guidance Agent**: Provides step-by-step, click-by-click navigation for confusing official portals.

### 4. **Futuristic Split-Screen Investigation Dashboard** 💻 *(New)*
- **Advanced Interactive UI**: Features like the `InteractiveTimeline` for threat visualization and `ProbabilityMeter` for tracking scam likelihood and recovery chances.
- **Case View**: A modern, split-screen interface with Chat, Tasks, and an Analysis Panel (50-50 split).
- **Dark Mode**: Sleek, modern "Glassmorphism" design built with Next.js, TailwindCSS, and Shadcn/UI.

### 5. **Comprehensive Evidence Management** 🗄️ *(New)*
- **Expanded Database Schema**: Robust MongoDB Atlas backend to securely store case states, multimodal evidence, chat histories, and action plans.
- **Real-time Synchronization**: Tasks and case status update dynamically as the AI analyzes new inputs.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js, TailwindCSS, Shadcn/UI (Modern Glassmorphism Design).
- **Backend**: Python FastAPI, LangGraph (Agent Orchestration).
- **AI Core**: Google Gemini 1.5 (Multimodal Vision), Groq Llama-3 (High Speed Text).
- **Tools**: DuckDuckGo Search, PRAW (Reddit), Tweepy (Twitter), BeautifulSoup4.
- **Database**: MongoDB Atlas (Vector Store + State Persistence + Evidence Management).
- **Authentication**: Clerk.

---

## ⚡ Deployment Guide

This project is optimized for deployment on **Vercel** (Frontend) and **Render** (Backend).

### 1. Prerequisites
- GitHub Account (Push this code to a repo).
- MongoDB Atlas Cluster (Get the Connection String).
- API Keys: `GROQ_API_KEY`, `GEMINI_API_KEY`, `CLERK_...` keys.

### 2. Backend Deployment (Render)
1. Create a **New Web Service** on [Render](https://render.com).
2. Connect your GitHub Repository.
3. **Settings**:
    - **Root Directory**: `backend`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
4. **Environment Variables**: Add all keys from your `backend/.env` file. (GROQ_API_KEY, GEMINI_API_KEY, MONGODB_URI, etc.).

### 3. Frontend Deployment (Vercel)
1. Import the project in [Vercel](https://vercel.com).
2. **Settings**:
    - **Root Directory**: `frontend`
    - **Framework Preset**: Next.js
3. **Environment Variables**: Add keys from `frontend/.env`.
    - `NEXT_PUBLIC_API_URL`: Set this to your **Render Backend URL** (e.g., `https://cyberguard-backend.onrender.com`).
4. **Deploy**!

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
