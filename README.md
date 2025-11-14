# 🔍 RepoBoard - GitHub Curation AI Agent

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

An autonomous system that ingests, analyzes, clusters, and curates GitHub repositories into discoverable boards using AI.

## ✨ Features

- 🤖 **AI-Powered Summaries** - Automatically generates summaries, tags, and categories using LLMs
- 📊 **Smart Clustering** - Groups similar repositories into curated boards
- 🎯 **Intelligent Ranking** - Scores repositories using star velocity, health, uniqueness, and more
- 🔍 **Semantic Search** - Find similar repositories using vector embeddings
- 🌐 **Browser Extension** - Access RepoBoard directly from GitHub
- 🚀 **One-Click Deploy** - Deploy to Railway or Render in minutes

## 🎯 Target Audience

Perfect for:
- **Developer Advocates** - Curating resources for communities
- **Tech Bloggers** - Finding trending repos to write about
- **Open Source Maintainers** - Discovering similar projects
- **Companies** - Building internal knowledge bases
- **Educational Platforms** - Curating learning resources

## 🚀 Quick Start

### Option 1: One-Click Deploy (Easiest)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click the button above
2. Add your API keys (OpenAI, GitHub)
3. Deploy!

### Option 2: Docker Compose

```bash
git clone https://github.com/yourusername/repoboard.git
cd repoboard
docker-compose up -d
```

### Option 3: Local Development

```bash
# Clone repo
git clone https://github.com/yourusername/repoboard.git
cd repoboard

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from db.connection import init_db; init_db()"

# Run the pipeline
python jobs/ingest_trending.py      # Fetch repos
python jobs/process_repos.py        # Generate summaries
python jobs/generate_boards.py      # Create boards

# Start services
cd api && uvicorn main:app --reload  # API at http://localhost:8000
cd web && npm install && npm run dev  # Frontend at http://localhost:3000
```

## 📖 Documentation

- **[START_HERE.md](START_HERE.md)** - Step-by-step setup guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[DEPLOY.md](DEPLOY.md)** - Deployment guides
- **[DISTRIBUTION_STRATEGY.md](DISTRIBUTION_STRATEGY.md)** - Distribution strategy

## 🏗️ Architecture

```
GitHub API
    ↓
[Ingestion Service] → PostgreSQL (Metadata)
    ↓
[LLM Service] → Summaries & Tags
    ↓
[Embedding Service] → Qdrant (Vectors)
    ↓
[Curation Engine] → Clustering & Ranking
    ↓
[API] → [Web Frontend]
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Vector DB**: Qdrant
- **LLM**: OpenAI/Anthropic/Ollama (configurable)
- **Frontend**: React, Vite, React Query
- **Infrastructure**: Docker Compose

## 📦 Components

- **ingestion-service** - GitHub API client, ingestion pipeline
- **embedding-service** - Vector embedding generation
- **llm-service** - LLM prompts and summarization
- **curation-engine** - Clustering and ranking
- **api** - FastAPI REST API
- **web** - React frontend
- **extension** - Browser extension for GitHub

## 🌐 Browser Extension

Install the Chrome/Firefox extension to:
- Browse curated boards from GitHub
- See similar repositories on any repo page
- Quick access to RepoBoard

See [extension/README.md](extension/README.md) for installation.

## 📊 API Endpoints

- `GET /repos` - List/search repositories
- `GET /repos/{id}` - Get repository details
- `GET /boards` - List all boards
- `GET /boards/{id}` - Get board with repositories
- `GET /search?q=query` - Search repositories
- `GET /stats` - Get statistics

API docs: http://localhost:8000/docs

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

Built with ❤️ for the developer community

---

**Made with**: Python, FastAPI, React, OpenAI, Qdrant
