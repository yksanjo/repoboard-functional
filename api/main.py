"""FastAPI application for RepoBoard API."""

import sys
import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db_session, SessionLocal
from db.models import Repo, RepoSummary, Board, BoardItem, CurationScore
from shared.schemas import (
    RepoMetadata, RepoSummary as RepoSummarySchema, Board as BoardSchema,
    BoardWithRepos, RepoWithSummary
)

# For Pydantic v2 compatibility
try:
    from pydantic import BaseModel
    PYDANTIC_V2 = True
except ImportError:
    PYDANTIC_V2 = False
from shared.config import settings

app = FastAPI(
    title="RepoBoard API",
    description="API for GitHub repository curation and boards",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def repo_to_dict(repo: Repo) -> dict:
    """Convert SQLAlchemy Repo to dict for Pydantic."""
    return {
        "url": repo.url,
        "full_name": repo.full_name,
        "name": repo.name,
        "owner": repo.owner,
        "description": repo.description,
        "readme": repo.readme,
        "languages": repo.languages or {},
        "stars": repo.stars,
        "forks": repo.forks,
        "watchers": repo.watchers,
        "open_issues": repo.open_issues,
        "created_at": repo.created_at,
        "updated_at": repo.updated_at,
        "pushed_at": repo.pushed_at,
        "default_branch": repo.default_branch,
        "topics": repo.topics or [],
        "license": repo.license,
        "archived": repo.archived,
        "file_tree": repo.file_tree,
        "commit_count": repo.commit_count,
        "contributor_count": repo.contributor_count,
        "star_velocity": repo.star_velocity,
    }


def summary_to_dict(summary: RepoSummary) -> dict:
    """Convert SQLAlchemy RepoSummary to dict for Pydantic."""
    return {
        "repo_id": summary.repo_id,
        "summary": summary.summary,
        "tags": summary.tags or [],
        "category": summary.category,
        "skill_level": summary.skill_level,
        "skill_level_numeric": summary.skill_level_numeric,
        "project_health": summary.project_health,
        "project_health_score": summary.project_health_score,
        "use_cases": summary.use_cases or [],
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RepoBoard API", "version": "1.0.0"}


@app.get("/repos", response_model=List[RepoWithSummary])
async def list_repos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    language: Optional[str] = None,
    min_stars: Optional[int] = Query(None, ge=0),
    skill_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List repositories with optional filters."""
    query = db.query(Repo).filter(Repo.archived == False)
    
    if category:
        query = query.join(RepoSummary).filter(RepoSummary.category == category)
    
    if language:
        # Filter by language in languages JSON field
        query = query.filter(Repo.languages.has_key(language))
    
    if min_stars:
        query = query.filter(Repo.stars >= min_stars)
    
    if skill_level:
        query = query.join(RepoSummary).filter(RepoSummary.skill_level == skill_level)
    
    repos = query.offset(skip).limit(limit).all()
    
    result = []
    for repo in repos:
        summary = repo.summary
        result.append(RepoWithSummary(
            repo=RepoMetadata(**repo_to_dict(repo)),
            summary=RepoSummarySchema(**summary_to_dict(summary)) if summary else None
        ))
    
    return result


@app.get("/repos/{repo_id}", response_model=RepoWithSummary)
async def get_repo(repo_id: int, db: Session = Depends(get_db)):
    """Get a single repository by ID."""
    repo = db.query(Repo).filter(Repo.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    summary = repo.summary
    return RepoWithSummary(
        repo=RepoMetadata(**repo_to_dict(repo)),
        summary=RepoSummarySchema(**summary_to_dict(summary)) if summary else None
    )


@app.get("/boards", response_model=List[BoardSchema])
async def list_boards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all boards."""
    query = db.query(Board)
    
    if category:
        query = query.filter(Board.category == category)
    
    boards = query.order_by(Board.created_at.desc()).offset(skip).limit(limit).all()
    return [
        BoardSchema(
            id=board.id,
            name=board.name,
            description=board.description,
            category=board.category,
            repo_count=board.repo_count,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
        for board in boards
    ]


@app.get("/boards/{board_id}", response_model=BoardWithRepos)
async def get_board(board_id: int, db: Session = Depends(get_db)):
    """Get a board with its repositories."""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Get board items ordered by rank
    items = db.query(BoardItem).filter(
        BoardItem.board_id == board_id
    ).order_by(BoardItem.rank_position).all()
    
    repos = []
    for item in items:
        repo = db.query(Repo).filter(Repo.id == item.repo_id).first()
        if repo:
            summary = repo.summary
            repos.append(RepoWithSummary(
                repo=RepoMetadata(**repo_to_dict(repo)),
                summary=RepoSummarySchema(**summary_to_dict(summary)) if summary else None
            ))
    
    return BoardWithRepos(
        board=BoardSchema(
            id=board.id,
            name=board.name,
            description=board.description,
            category=board.category,
            repo_count=board.repo_count,
            created_at=board.created_at,
            updated_at=board.updated_at,
        ),
        repos=repos
    )


@app.get("/search")
async def search_repos(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search repositories by name, description, or tags."""
    query = db.query(Repo).join(RepoSummary).filter(Repo.archived == False)
    
    # Simple text search (in production, use full-text search)
    search_term = f"%{q}%"
    query = query.filter(
        (Repo.name.ilike(search_term)) |
        (Repo.description.ilike(search_term)) |
        (RepoSummary.summary.ilike(search_term))
    )
    
    repos = query.limit(limit).all()
    
    result = []
    for repo in repos:
        summary = repo.summary
        result.append(RepoWithSummary(
            repo=RepoMetadata(**repo_to_dict(repo)),
            summary=RepoSummarySchema(**summary_to_dict(summary)) if summary else None
        ))
    
    return result


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics."""
    total_repos = db.query(Repo).filter(Repo.archived == False).count()
    total_boards = db.query(Board).count()
    total_categories = db.query(RepoSummary.category).distinct().count()
    
    return {
        "total_repos": total_repos,
        "total_boards": total_boards,
        "total_categories": total_categories,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

