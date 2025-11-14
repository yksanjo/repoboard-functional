# RepoBoard Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Qdrant (vector database)
- GitHub API token (optional but recommended)

## Installation

### 1. Database Setup

```bash
# Install PostgreSQL and create database
createdb repoboard

# Or using Docker
docker run -d \
  --name postgres-repoboard \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=repoboard \
  -p 5432:5432 \
  postgres:14
```

### 2. Vector Database Setup (Qdrant)

```bash
# Using Docker
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```

### 3. Python Environment

```bash
cd repoboard
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `QDRANT_URL`: Qdrant server URL
- `LLM_PROVIDER`: `openai`, `anthropic`, or `ollama`
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: API key for LLM provider
- `GITHUB_TOKEN`: GitHub API token (optional but recommended)

### 5. Initialize Database

```bash
python -c "from db.connection import init_db; init_db()"
```

### 6. Frontend Setup

```bash
cd web
npm install
```

## Usage

### 1. Ingest Repositories

```bash
python jobs/ingest_trending.py
```

This will fetch trending repositories from GitHub and store them in the database.

### 2. Process Repositories

Generate summaries and embeddings:

```bash
python jobs/process_repos.py
```

This will:
- Generate LLM summaries for repositories
- Create vector embeddings
- Store embeddings in Qdrant

### 3. Generate Boards

Create curated boards from clustered repositories:

```bash
python jobs/generate_boards.py
```

### 4. Start API Server

```bash
cd api
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`

### 5. Start Frontend

```bash
cd web
npm run dev
```

Frontend will be available at `http://localhost:3000`

## API Endpoints

- `GET /` - API info
- `GET /repos` - List repositories (with filters)
- `GET /repos/{id}` - Get repository details
- `GET /boards` - List all boards
- `GET /boards/{id}` - Get board with repositories
- `GET /search?q=query` - Search repositories
- `GET /stats` - Get statistics

## Automation

Set up cron jobs for automated ingestion and curation:

```bash
# Ingest trending repos every 6 hours
0 */6 * * * cd /path/to/repoboard && python jobs/ingest_trending.py

# Process new repos every hour
0 * * * * cd /path/to/repoboard && python jobs/process_repos.py

# Regenerate boards daily
0 2 * * * cd /path/to/repoboard && python jobs/generate_boards.py
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

### Vector DB Issues

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check `QDRANT_URL` in `.env`

### LLM API Issues

- Verify API key is set correctly
- Check rate limits
- For Ollama, ensure model is downloaded: `ollama pull llama3`

### Import Errors

- Ensure you're in the correct directory
- Check Python path includes repoboard root
- Verify all dependencies are installed

## Development

### Running Tests

```bash
# Add tests as needed
pytest tests/
```

### Code Structure

- `ingestion-service/`: GitHub API client and ingestion logic
- `embedding-service/`: Vector embedding generation
- `llm-service/`: LLM prompts and summarization
- `curation-engine/`: Clustering and ranking
- `api/`: FastAPI REST API
- `web/`: React frontend
- `db/`: Database models and connection
- `jobs/`: Automation scripts
- `shared/`: Common schemas and config

## Next Steps

1. Set up monitoring and logging
2. Add authentication for API
3. Implement user preferences and personalization
4. Add email digest functionality
5. Scale with Redis caching
6. Add more sophisticated clustering algorithms

