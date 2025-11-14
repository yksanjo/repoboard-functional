# RepoBoard Architecture

## System Overview

RepoBoard is an autonomous GitHub repository curation system that ingests, analyzes, clusters, and ranks repositories into discoverable boards.

## Data Flow

```
GitHub API
    ↓
[Ingestion Service]
    ↓
PostgreSQL (Metadata)
    ↓
[LLM Service] → [Embedding Service]
    ↓              ↓
PostgreSQL      Qdrant (Vectors)
    ↓
[Curation Engine]
    ↓
PostgreSQL (Boards)
    ↓
[API] → [Web Frontend]
```

## Components

### 1. Ingestion Service

**Purpose**: Fetch and store repository metadata from GitHub

**Key Files**:
- `ingestion-service/github_client.py`: GitHub API client
- `ingestion-service/ingester.py`: Ingestion pipeline

**Responsibilities**:
- Fetch trending repositories
- Extract README, languages, file tree
- Calculate star velocity
- Store in PostgreSQL

### 2. Embedding Service

**Purpose**: Generate vector embeddings for semantic search

**Key Files**:
- `embedding-service/embedder.py`: Embedding generation
- `embedding-service/vector_db.py`: Qdrant client

**Responsibilities**:
- Generate embeddings from repo content
- Store in Qdrant vector database
- Enable semantic similarity search

### 3. LLM Service

**Purpose**: Generate summaries, tags, and analysis

**Key Files**:
- `llm-service/llm_client.py`: LLM API client
- `llm-service/prompts.py`: Prompt templates
- `llm-service/summarizer.py`: Summarization pipeline

**Responsibilities**:
- Generate repository summaries
- Extract tags and categories
- Assess project health
- Determine skill level
- Generate board names and descriptions

### 4. Curation Engine

**Purpose**: Cluster and rank repositories

**Key Files**:
- `curation-engine/clusterer.py`: Clustering logic
- `curation-engine/ranker.py`: Ranking algorithm

**Responsibilities**:
- Cluster repositories by similarity
- Rank repositories using scoring model
- Generate curated boards
- Maintain board quality

### 5. API Service

**Purpose**: REST API for accessing data

**Key Files**:
- `api/main.py`: FastAPI application

**Endpoints**:
- `/repos`: List/search repositories
- `/boards`: List/get boards
- `/search`: Semantic search

### 6. Web Frontend

**Purpose**: User interface for browsing boards

**Key Files**:
- `web/src/App.jsx`: Main application
- `web/src/components/`: React components

**Features**:
- Browse boards
- View repository details
- Search functionality

## Database Schema

### PostgreSQL Tables

- `repos`: Repository metadata
- `repo_summaries`: LLM-generated summaries
- `boards`: Curated board definitions
- `board_items`: Repositories in boards (with ranking)
- `users`: User profiles (for future personalization)
- `user_preferences`: User preferences
- `curation_scores`: Repository ranking scores

### Qdrant Collections

- `repo_embeddings`: Vector embeddings for semantic search

## Scoring Model

Repository ranking uses weighted scoring:

```
total_score = 
  0.35 * star_velocity +
  0.25 * project_health +
  0.20 * uniqueness +
  0.10 * readme_quality +
  0.10 * difficulty_weight
```

## Clustering Algorithm

1. Extract features from repositories (category, languages, metadata)
2. Normalize features
3. Apply KMeans clustering
4. Filter small clusters
5. Generate board names using LLM
6. Rank repositories within each board

## LLM Prompts

### Repository Summary

Generates:
- 100-200 word summary
- 5-12 tags
- Category
- Skill level (1-10)
- Project health score
- Use cases

### Board Generation

Generates:
- Board name (2-5 words)
- Board description (1-2 sentences)

## Scalability Considerations

### Current Limitations

- In-memory clustering (limited to ~10K repos)
- Sequential LLM calls
- No caching layer

### Future Improvements

- Batch LLM processing
- Distributed clustering (Spark/Dask)
- Redis caching
- CDN for static assets
- Database read replicas
- Horizontal scaling of API

## Security

### Current State

- No authentication
- CORS open to all origins
- API keys in environment variables

### Future Enhancements

- JWT authentication
- Rate limiting
- API key management
- Secrets management (Vault)
- Input validation and sanitization

## Monitoring

### Recommended Metrics

- Ingestion rate
- LLM API latency
- Database query performance
- API response times
- Error rates
- Board generation time

### Logging

- Structured logging (JSON)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Centralized log aggregation

## Deployment

### Development

- Local PostgreSQL
- Local Qdrant
- Local API and frontend

### Production

- Managed PostgreSQL (RDS, Cloud SQL)
- Managed Qdrant or self-hosted
- Containerized services (Docker)
- Orchestration (Kubernetes, Docker Compose)
- Load balancer
- CI/CD pipeline

## Future Enhancements

1. **Personalization**
   - User preference vectors
   - Custom board generation
   - Follow/unfollow boards

2. **Automation**
   - Auto-refresh clusters
   - Detect trending repos
   - Clean abandoned repos

3. **Features**
   - Email digests
   - RSS feeds
   - API webhooks
   - Export functionality

4. **Analytics**
   - Board popularity
   - Repository trends
   - User engagement

