# RepoBoard - Project Summary

## What Was Built

RepoBoard is a complete GitHub repository curation AI agent system that:

1. **Ingests** repositories from GitHub (trending, search, manual)
2. **Analyzes** them using LLMs (summaries, tags, categories, health scores)
3. **Embeds** them for semantic search (vector embeddings in Qdrant)
4. **Clusters** similar repositories together
5. **Ranks** repositories using a scoring model
6. **Creates** curated boards with names and descriptions
7. **Exposes** everything through a REST API and web dashboard

## Project Structure

```
repoboard/
├── ingestion-service/     # GitHub API client, ingestion pipeline
├── embedding-service/     # Vector embedding generation, Qdrant client
├── llm-service/          # LLM prompts, summarization, board naming
├── curation-engine/      # Clustering, ranking, board generation
├── api/                  # FastAPI REST API
├── web/                  # React frontend
├── db/                   # Database models, connection
├── jobs/                 # Automation scripts
├── shared/               # Common schemas, config
└── scripts/              # Utility scripts
```

## Key Features

### Backend Services

- **GitHub Ingestion**: Fetches trending repos, extracts metadata, READMEs, file trees
- **LLM Summarization**: Generates summaries, tags, categories, skill levels, health scores
- **Vector Embeddings**: Creates embeddings for semantic similarity search
- **Clustering**: Groups similar repos using KMeans on metadata features
- **Ranking**: Scores repos using weighted formula (star velocity, health, uniqueness, etc.)
- **Board Generation**: Creates curated boards with LLM-generated names/descriptions

### API Endpoints

- `GET /repos` - List/search repositories with filters
- `GET /repos/{id}` - Get repository details
- `GET /boards` - List all boards
- `GET /boards/{id}` - Get board with repositories
- `GET /search?q=query` - Search repositories
- `GET /stats` - Get statistics

### Frontend

- Browse curated boards
- View repository details
- Search functionality
- Responsive design

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Vector DB**: Qdrant
- **LLM**: OpenAI/Anthropic/Ollama (configurable)
- **Frontend**: React, Vite, React Query
- **Infrastructure**: Docker Compose

## Scoring Model

Repositories are ranked using:

```
total_score = 
  0.35 * star_velocity +
  0.25 * project_health +
  0.20 * uniqueness +
  0.10 * readme_quality +
  0.10 * difficulty_weight
```

## Getting Started

1. **Start infrastructure**: `docker-compose up -d`
2. **Configure**: Copy `.env.example` to `.env` and set API keys
3. **Initialize DB**: `python -c "from db.connection import init_db; init_db()"`
4. **Ingest repos**: `python jobs/ingest_trending.py`
5. **Process repos**: `python jobs/process_repos.py`
6. **Generate boards**: `python jobs/generate_boards.py`
7. **Start API**: `cd api && uvicorn main:app --reload`
8. **Start frontend**: `cd web && npm install && npm run dev`

## What's Next (Future Enhancements)

### Phase 2: Personalization
- User profiles and preferences
- Custom board generation via prompts
- Follow/unfollow boards
- Personalized recommendations

### Phase 3: Automation
- Scheduled ingestion jobs
- Auto-refresh clusters
- Detect trending repos
- Clean abandoned repos
- Email digests

### Phase 4: Advanced Features
- Semantic search using embeddings
- Multi-language support
- Export functionality (JSON, CSV)
- API webhooks
- Analytics dashboard

## Architecture Decisions

1. **Modular Services**: Each service is independent and can be scaled separately
2. **Vector DB**: Qdrant for efficient similarity search
3. **LLM Abstraction**: Support for multiple providers (OpenAI, Anthropic, Ollama)
4. **Hybrid Clustering**: Uses metadata features (faster) with option for embedding-based
5. **Scoring Model**: Configurable weights for different factors

## Performance Considerations

- **Current Scale**: Designed for 500-10,000 repos
- **Bottlenecks**: LLM API calls (sequential), clustering (in-memory)
- **Optimizations**: Batch processing, caching, async operations
- **Scaling**: Can be containerized and orchestrated with Kubernetes

## Documentation

- `README.md` - Overview
- `SETUP.md` - Detailed setup instructions
- `QUICKSTART.md` - Quick start guide
- `ARCHITECTURE.md` - System architecture details
- `PROJECT_SUMMARY.md` - This file

## License

See LICENSE file (to be added)

## Contributing

See CONTRIBUTING.md (to be added)

