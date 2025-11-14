# 🚀 RepoBoard - Start Here!

Welcome! Let's get RepoBoard running. I'll guide you through each step.

## ✅ What's Done

- ✅ Python virtual environment created
- ✅ All Python dependencies installed
- ✅ `.env` file created (needs configuration)

## 📋 Next Steps

### Step 1: Set Up Databases

You have 3 options:

#### Option A: Docker (Recommended - Easiest)
```bash
# Install Docker Desktop first: https://www.docker.com/products/docker-desktop
# Then run:
docker-compose up -d
```

#### Option B: Manual PostgreSQL + Qdrant
```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14
createdb repoboard

# Install Qdrant (or use Docker just for Qdrant)
docker run -d -p 6333:6333 qdrant/qdrant
```

#### Option C: Quick Test (SQLite - No setup needed)
I can modify the code to use SQLite for quick testing. Just ask!

### Step 2: Configure API Keys

Edit `.env` file and add:

1. **GitHub Token** (optional but recommended):
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Add to `.env`: `GITHUB_TOKEN=your_token_here`

2. **LLM Provider** (choose one):

   **Option A: OpenAI** (requires API key)
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-...
   ```
   Get key from: https://platform.openai.com/api-keys

   **Option B: Ollama** (free, local)
   ```bash
   LLM_PROVIDER=ollama
   ```
   Install: https://ollama.ai
   Then: `ollama pull llama3`

   **Option C: Anthropic**
   ```bash
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Step 3: Update Database URL

If using PostgreSQL, update in `.env`:
```bash
DATABASE_URL=postgresql://your_username:password@localhost:5432/repoboard
```

### Step 4: Initialize Database

```bash
source venv/bin/activate
python -c "from db.connection import init_db; init_db()"
```

### Step 5: Run the Pipeline

**1. Ingest repositories from GitHub:**
```bash
python jobs/ingest_trending.py
```
This fetches trending repos (takes a few minutes).

**2. Process repositories** (generate summaries with LLM):
```bash
python jobs/process_repos.py
```
This uses your LLM provider to generate summaries (takes time, costs money if using OpenAI).

**3. Generate boards:**
```bash
python jobs/generate_boards.py
```
This clusters repos and creates curated boards.

### Step 6: Start the Services

**Terminal 1 - Start API:**
```bash
cd api
uvicorn main:app --reload
```
Visit: http://localhost:8000/docs (API documentation)

**Terminal 2 - Start Frontend:**
```bash
cd web
npm install
npm run dev
```
Visit: http://localhost:3000 (Web interface)

## 🎯 Quick Test (Minimal Setup)

Want to test quickly without full setup?

1. I can modify code to use SQLite (no PostgreSQL needed)
2. Skip Qdrant initially (embeddings optional)
3. Use Ollama for free local LLM
4. Start with just 5-10 repos for testing

**Just tell me: "Let's do the quick test setup"**

## 📚 Need Help?

- Check `SETUP.md` for detailed instructions
- Check `ARCHITECTURE.md` for system overview
- Check `QUICKSTART.md` for quick reference

## 🐛 Troubleshooting

**Database connection error?**
- Make sure PostgreSQL is running: `brew services list`
- Check DATABASE_URL in `.env`

**LLM errors?**
- Verify API key is set correctly
- For Ollama: Make sure it's running and model is downloaded

**Import errors?**
- Make sure venv is activated: `source venv/bin/activate`
- Check you're in the repoboard directory

---

**Ready to continue?** Tell me which option you want:
1. "Set up with Docker"
2. "Set up manually"
3. "Quick test setup"
4. "I have questions about..."

