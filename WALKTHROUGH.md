# RepoBoard Walkthrough Guide

Let's get RepoBoard running step by step!

## Prerequisites Check

✅ Python 3.9+ - You have Python 3.9.11
✅ Node.js - You have Node.js v24.7.0
❌ Docker - Not installed (we'll set up manually)

## Step-by-Step Setup

### Step 1: Set Up Python Environment

```bash
cd repoboard
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Database Options

**Option A: Use Docker (Recommended)**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Then run: `docker-compose up -d`

**Option B: Install PostgreSQL Manually**
- macOS: `brew install postgresql@14`
- Start: `brew services start postgresql@14`
- Create DB: `createdb repoboard`

**Option C: Use SQLite (Simplest for testing)**
- We can modify the code to use SQLite temporarily

### Step 4: Set Up Qdrant (Vector Database)

**Option A: Use Docker**
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

**Option B: Install Qdrant Locally**
- Download from: https://qdrant.tech/documentation/guides/installation/

### Step 5: Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your settings.

### Step 6: Initialize Database

```bash
python -c "from db.connection import init_db; init_db()"
```

### Step 7: Get API Keys

- **GitHub Token** (optional but recommended): https://github.com/settings/tokens
- **OpenAI API Key** (for LLM): https://platform.openai.com/api-keys
- OR use **Ollama** (local, free): https://ollama.ai

### Step 8: Run the Pipeline

1. Ingest repos: `python jobs/ingest_trending.py`
2. Process repos: `python jobs/process_repos.py`
3. Generate boards: `python jobs/generate_boards.py`

### Step 9: Start Services

**API Server:**
```bash
cd api
uvicorn main:app --reload
```

**Frontend:**
```bash
cd web
npm install
npm run dev
```

## Quick Test Without Full Setup

Want to test quickly? We can:
1. Use SQLite instead of PostgreSQL
2. Skip Qdrant initially (embeddings optional)
3. Use Ollama for local LLM (free)

Let me know which path you'd like to take!

