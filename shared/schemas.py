"""Pydantic schemas for RepoBoard data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class SkillLevel(str, Enum):
    """Skill level categories."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ProjectHealth(str, Enum):
    """Project health status."""
    EXCELLENT = "excellent"
    GOOD = "good"
    MODERATE = "moderate"
    POOR = "poor"
    ABANDONED = "abandoned"


class RepoMetadata(BaseModel):
    """GitHub repository metadata."""
    id: Optional[int] = None
    url: HttpUrl
    full_name: str
    name: str
    owner: str
    description: Optional[str] = None
    readme: Optional[str] = None
    languages: Dict[str, float] = Field(default_factory=dict)
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    default_branch: str = "main"
    topics: List[str] = Field(default_factory=list)
    license: Optional[str] = None
    archived: bool = False
    file_tree: Optional[Dict[str, Any]] = None
    commit_count: int = 0
    contributor_count: int = 0
    star_velocity: float = 0.0  # Stars gained per day
    created_at_db: Optional[datetime] = None
    updated_at_db: Optional[datetime] = None


class RepoSummary(BaseModel):
    """LLM-generated repository summary."""
    repo_id: int
    summary: str = Field(..., min_length=100, max_length=500)
    tags: List[str] = Field(..., min_items=5, max_items=12)
    category: str
    skill_level: SkillLevel
    skill_level_numeric: int = Field(..., ge=1, le=10)
    project_health: ProjectHealth
    project_health_score: float = Field(..., ge=0.0, le=1.0)
    use_cases: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Board(BaseModel):
    """Curated board of repositories."""
    id: Optional[int] = None
    name: str
    description: str
    category: Optional[str] = None
    repo_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BoardItem(BaseModel):
    """Repository item in a board."""
    board_id: int
    repo_id: int
    rank_score: float = Field(..., ge=0.0, le=1.0)
    rank_position: int = 0
    added_at: Optional[datetime] = None


class RepoEmbedding(BaseModel):
    """Vector embedding for a repository."""
    repo_id: int
    embedding: List[float]
    model: str = "text-embedding-3-small"
    created_at: Optional[datetime] = None


class User(BaseModel):
    """User profile."""
    id: Optional[int] = None
    email: str
    username: str
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class UserPreference(BaseModel):
    """User preferences for personalization."""
    user_id: int
    preferred_categories: List[str] = Field(default_factory=list)
    preferred_languages: List[str] = Field(default_factory=list)
    skill_level_range: Optional[tuple[int, int]] = None
    preference_vector: Optional[List[float]] = None
    updated_at: Optional[datetime] = None


class RepoWithSummary(BaseModel):
    """Repository with its summary and metadata."""
    repo: RepoMetadata
    summary: Optional[RepoSummary] = None
    embedding_id: Optional[str] = None


class BoardWithRepos(BaseModel):
    """Board with its repositories."""
    board: Board
    repos: List[RepoWithSummary] = Field(default_factory=list)


class CurationScore(BaseModel):
    """Scoring breakdown for repository curation."""
    repo_id: int
    star_velocity: float
    project_health: float
    uniqueness: float
    readme_quality: float
    difficulty_weight: float
    total_score: float
    computed_at: Optional[datetime] = None

