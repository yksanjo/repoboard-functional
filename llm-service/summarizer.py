"""Service for generating repository summaries using LLM."""

import sys
import os
from typing import Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db
from db.models import Repo, RepoSummary
from llm_service.llm_client import LLMClient
from shared.schemas import SkillLevel, ProjectHealth


class RepoSummarizer:
    """Service for generating and storing repository summaries."""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def summarize_repo(self, repo_id: int) -> Optional[RepoSummary]:
        """Generate and store summary for a repository."""
        with get_db() as db:
            repo = db.query(Repo).filter(Repo.id == repo_id).first()
            if not repo:
                return None
            
            # Prepare repo data
            repo_data = {
                "name": repo.name,
                "owner": repo.owner,
                "description": repo.description or "",
                "languages": repo.languages or {},
                "topics": repo.topics or [],
                "stars": repo.stars,
                "readme": repo.readme or "",
            }
            
            # Generate summary using LLM
            llm_result = self.llm_client.generate_repo_summary(repo_data)
            
            # Check if summary already exists
            existing = db.query(RepoSummary).filter(RepoSummary.repo_id == repo_id).first()
            
            if existing:
                # Update existing summary
                existing.summary = llm_result["summary"]
                existing.tags = llm_result["tags"]
                existing.category = llm_result["category"]
                existing.skill_level = llm_result["skill_level"]
                existing.skill_level_numeric = llm_result["skill_level_numeric"]
                existing.project_health = llm_result["project_health"]
                existing.project_health_score = llm_result["project_health_score"]
                existing.use_cases = llm_result.get("use_cases", [])
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                return existing
            else:
                # Create new summary
                summary = RepoSummary(
                    repo_id=repo_id,
                    summary=llm_result["summary"],
                    tags=llm_result["tags"],
                    category=llm_result["category"],
                    skill_level=llm_result["skill_level"],
                    skill_level_numeric=llm_result["skill_level_numeric"],
                    project_health=llm_result["project_health"],
                    project_health_score=llm_result["project_health_score"],
                    use_cases=llm_result.get("use_cases", []),
                )
                db.add(summary)
                db.commit()
                db.refresh(summary)
                return summary
    
    def summarize_batch(self, repo_ids: list[int]) -> list[RepoSummary]:
        """Generate summaries for multiple repositories."""
        summaries = []
        for repo_id in repo_ids:
            try:
                summary = self.summarize_repo(repo_id)
                if summary:
                    summaries.append(summary)
                    print(f"Summarized repo {repo_id}")
            except Exception as e:
                print(f"Error summarizing repo {repo_id}: {e}")
                continue
        return summaries

