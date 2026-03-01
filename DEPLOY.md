# RepoBoard Deployment Guide

## One-Click Deploy Options

### 🚀 Railway.app (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

**Steps:**
1. Click the button above
2. Connect your GitHub account
3. Add environment variables:
   - `OPENAI_API_KEY` (or set `LLM_PROVIDER=ollama`)
   - `GITHUB_TOKEN` (optional)
4. Railway automatically sets up PostgreSQL
5. Deploy!

**After deployment:**
- Database is auto-configured
- Run migrations: `railway run python -c "from db.connection import init_db; init_db()"`
- Ingest repos: `railway run python jobs/ingest_trending.py`

### 🌐 Render.com

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database (free tier)
6. Add environment variables
7. Deploy!

### 🐳 Docker Compose (Self-Hosted)

```bash
# Clone repo
git clone <your-repo>
cd repoboard

# Copy and configure .env
cp .env.example .env
# Edit .env with your API keys

# Start everything
docker-compose up -d

# Initialize database
docker-compose exec api python -c "from db.connection import init_db; init_db()"

# Ingest repos
docker-compose exec api python jobs/ingest_trending.py
```

### ☁️ Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Add PostgreSQL
fly postgres create

# Attach database
fly postgres attach <db-name>

# Deploy
fly deploy
```

## Environment Variables

Required:
- `DATABASE_URL` (auto-set on Railway/Render)
- `OPENAI_API_KEY` or `OLLAMA_BASE_URL`
- `GITHUB_TOKEN` (optional)

Optional:
- `QDRANT_URL` (for vector search)
- `LLM_PROVIDER` (default: openai)

## Post-Deployment

1. **Initialize database:**
   ```bash
   python -c "from db.connection import init_db; init_db()"
   ```

2. **Ingest repositories:**
   ```bash
   python jobs/ingest_trending.py
   ```

3. **Process repositories:**
   ```bash
   python jobs/process_repos.py
   ```

4. **Generate boards:**
   ```bash
   python jobs/generate_boards.py
   ```

5. **Access:**
   - API: `https://your-app.railway.app`
   - Docs: `https://your-app.railway.app/docs`

## Scheduled Jobs

Set up cron jobs or scheduled tasks:

- **Ingest trending:** Every 6 hours
- **Process repos:** Every hour
- **Generate boards:** Daily at 2 AM

On Railway: Use Railway Cron
On Render: Use Render Cron Jobs

