# RepoBoard Quick Start

Get RepoBoard running in 5 minutes!

## Prerequisites

- Docker and Docker Compose
- Python 3.9+ (if not using Docker)
- GitHub API token (optional but recommended)

## Quick Setup

### 1. Start Infrastructure

```bash
docker-compose up -d
```

This starts PostgreSQL and Qdrant.

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL=postgresql://repoboard:repoboard@localhost:5432/repoboard`
- `OPENAI_API_KEY=your_key_here` (or use Ollama)
- `GITHUB_TOKEN=your_token_here` (optional)

### 3. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python -c "from db.connection import init_db; init_db()"
```

### 5. Ingest Repositories

```bash
python jobs/ingest_trending.py
```

This fetches trending repos from GitHub.

### 6. Process Repositories

```bash
python jobs/process_repos.py
```

This generates summaries and embeddings (requires LLM API key).

### 7. Generate Boards

```bash
python jobs/generate_boards.py
```

This creates curated boards from clusters.

### 8. Start API

```bash
cd api
uvicorn main:app --reload
```

API available at http://localhost:8000

### 9. Start Frontend

```bash
cd web
npm install
npm run dev
```

Frontend available at http://localhost:3000

## Using Ollama (Local LLM)

If you don't have OpenAI/Anthropic API keys:

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3`
3. Set in `.env`: `LLM_PROVIDER=ollama`

## Next Steps

- Browse boards at http://localhost:3000
- Check API docs at http://localhost:8000/docs
- Set up cron jobs for automation (see SETUP.md)

## Troubleshooting

**Database connection error**: Ensure Docker containers are running: `docker-compose ps`

**LLM errors**: Check API key is set correctly in `.env`

**Import errors**: Make sure you're in the repoboard directory and venv is activated

