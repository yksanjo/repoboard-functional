# RepoBoard Setup Guide - Step by Step

Let's get you up and running! I'll walk you through each step.

## Current Status

✅ Python virtual environment created
⏳ Installing dependencies...
⏳ Need to set up database
⏳ Need to configure API keys

## Step 1: Complete Python Installation

```bash
cd /Users/yoshikondo/awesome-generative-ai/repoboard
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Choose Your Database Setup

### Option A: Use Docker (Easiest)

If you can install Docker Desktop:
1. Download from: https://www.docker.com/products/docker-desktop
2. Install and start Docker
3. Run: `docker-compose up -d`

### Option B: Install PostgreSQL Manually

**On macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
createdb repoboard
```

**On Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres createdb repoboard
```

### Option C: Quick Test with SQLite (Simplest)

I can modify the code to use SQLite for quick testing. Just let me know!

## Step 3: Set Up Qdrant (Vector Database)

### Option A: Docker
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### Option B: Skip for Now
We can skip embeddings initially and add them later.

## Step 4: Configure Environment

```bash
cp .env.example .env
```

Then edit `.env` and add:
- **GitHub Token** (optional): Get from https://github.com/settings/tokens
- **OpenAI API Key** (for LLM): Get from https://platform.openai.com/api-keys
- **OR use Ollama** (local, free): Install from https://ollama.ai and set `LLM_PROVIDER=ollama`

## Step 5: Initialize Database

```bash
python -c "from db.connection import init_db; init_db()"
```

## Step 6: Run the Pipeline

1. **Ingest repositories:**
   ```bash
   python jobs/ingest_trending.py
   ```

2. **Process repositories** (generate summaries):
   ```bash
   python jobs/process_repos.py
   ```

3. **Generate boards:**
   ```bash
   python jobs/generate_boards.py
   ```

## Step 7: Start the Services

**Terminal 1 - API Server:**
```bash
cd api
uvicorn main:app --reload
```
API will be at: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd web
npm install
npm run dev
```
Frontend will be at: http://localhost:3000

## Quick Start (Minimal Setup)

Want to test quickly? Here's the minimal setup:

1. ✅ Python venv (done)
2. Install dependencies: `pip install -r requirements.txt`
3. Use SQLite (I can modify code)
4. Skip Qdrant initially
5. Use Ollama for LLM (free, local)
6. Start with a few repos manually

Let me know which path you want to take!

