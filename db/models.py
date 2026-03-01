"""SQLAlchemy models for RepoBoard database."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, 
    ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Repo(Base):
    """GitHub repository metadata."""
    __tablename__ = "repos"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    owner = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    readme = Column(Text)
    languages = Column(JSON, default=dict)
    stars = Column(Integer, default=0, index=True)
    forks = Column(Integer, default=0)
    watchers = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    pushed_at = Column(DateTime, index=True)
    default_branch = Column(String(100), default="main")
    topics = Column(JSON, default=list)
    license = Column(String(100))
    archived = Column(Boolean, default=False, index=True)
    file_tree = Column(JSON)
    commit_count = Column(Integer, default=0)
    contributor_count = Column(Integer, default=0)
    star_velocity = Column(Float, default=0.0, index=True)
    created_at_db = Column(DateTime, server_default=func.now())
    updated_at_db = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    summary = relationship("RepoSummary", back_populates="repo", uselist=False)
    board_items = relationship("BoardItem", back_populates="repo")
    
    __table_args__ = (
        Index("idx_repo_stars_velocity", "stars", "star_velocity"),
        Index("idx_repo_updated", "updated_at_db"),
    )


class RepoSummary(Base):
    """LLM-generated repository summary."""
    __tablename__ = "repo_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    tags = Column(JSON, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    skill_level = Column(String(50), nullable=False, index=True)
    skill_level_numeric = Column(Integer, nullable=False)
    project_health = Column(String(50), nullable=False, index=True)
    project_health_score = Column(Float, nullable=False)
    use_cases = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    repo = relationship("Repo", back_populates="summary")


class Board(Base):
    """Curated board of repositories."""
    __tablename__ = "boards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True)
    repo_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("BoardItem", back_populates="board", cascade="all, delete-orphan")


class BoardItem(Base):
    """Repository item in a board."""
    __tablename__ = "board_items"
    
    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False, index=True)
    rank_score = Column(Float, nullable=False)
    rank_position = Column(Integer, default=0, index=True)
    added_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    board = relationship("Board", back_populates="items")
    repo = relationship("Repo", back_populates="board_items")
    
    __table_args__ = (
        Index("idx_board_repo", "board_id", "repo_id", unique=True),
        Index("idx_board_rank", "board_id", "rank_position"),
    )


class User(Base):
    """User profile."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())


class UserPreference(Base):
    """User preferences for personalization."""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    preferred_categories = Column(JSON, default=list)
    preferred_languages = Column(JSON, default=list)
    skill_level_min = Column(Integer)
    skill_level_max = Column(Integer)
    preference_vector = Column(JSON)  # Stored as list
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CurationScore(Base):
    """Scoring breakdown for repository curation."""
    __tablename__ = "curation_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), unique=True, nullable=False, index=True)
    star_velocity = Column(Float, nullable=False)
    project_health = Column(Float, nullable=False)
    uniqueness = Column(Float, nullable=False)
    readme_quality = Column(Float, nullable=False)
    difficulty_weight = Column(Float, nullable=False)
    total_score = Column(Float, nullable=False, index=True)
    computed_at = Column(DateTime, server_default=func.now())

