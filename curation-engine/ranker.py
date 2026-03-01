"""Repository ranking and scoring system."""

import sys
import os
from typing import List, Dict, Any
from datetime import datetime
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db
from db.models import Repo, RepoSummary, CurationScore
from shared.schemas import CurationScore as CurationScoreSchema


class RepoRanker:
    """Service for ranking and scoring repositories."""
    
    def __init__(self):
        # Scoring weights (as specified in requirements)
        self.weights = {
            "star_velocity": 0.35,
            "project_health": 0.25,
            "uniqueness": 0.20,
            "readme_quality": 0.10,
            "difficulty_weight": 0.10,
        }
    
    def calculate_star_velocity_score(self, star_velocity: float, max_velocity: float = 100.0) -> float:
        """Calculate normalized star velocity score."""
        if max_velocity == 0:
            return 0.0
        # Normalize to 0-1 range with logarithmic scaling
        normalized = min(star_velocity / max_velocity, 1.0)
        return math.log(1 + normalized * 9) / math.log(10)  # Log scale
    
    def calculate_project_health_score(self, summary: RepoSummary) -> float:
        """Get project health score from summary."""
        return summary.project_health_score if summary else 0.5
    
    def calculate_uniqueness_score(self, repo: Repo, all_repos: List[Repo]) -> float:
        """Calculate uniqueness based on language/topic diversity."""
        # Simple heuristic: repos with unique language combinations are more unique
        repo_languages = set(repo.languages.keys()) if repo.languages else set()
        repo_topics = set(repo.topics) if repo.topics else set()
        
        # Count how many repos share similar languages/topics
        similarity_count = 0
        for other_repo in all_repos:
            if other_repo.id == repo.id:
                continue
            other_languages = set(other_repo.languages.keys()) if other_repo.languages else set()
            other_topics = set(other_repo.topics) if other_repo.topics else set()
            
            # Calculate Jaccard similarity
            lang_overlap = len(repo_languages & other_languages) / max(len(repo_languages | other_languages), 1)
            topic_overlap = len(repo_topics & other_topics) / max(len(repo_topics | other_topics), 1)
            
            if lang_overlap > 0.5 or topic_overlap > 0.5:
                similarity_count += 1
        
        # More unique = fewer similar repos
        uniqueness = 1.0 / (1.0 + similarity_count / 10.0)
        return min(uniqueness, 1.0)
    
    def calculate_readme_quality_score(self, readme: Optional[str]) -> float:
        """Calculate README quality score."""
        if not readme:
            return 0.0
        
        score = 0.0
        readme_lower = readme.lower()
        
        # Check for common README sections
        if "installation" in readme_lower or "install" in readme_lower:
            score += 0.2
        if "usage" in readme_lower or "example" in readme_lower:
            score += 0.2
        if "license" in readme_lower:
            score += 0.1
        if "contributing" in readme_lower or "contribute" in readme_lower:
            score += 0.1
        if "documentation" in readme_lower or "docs" in readme_lower:
            score += 0.1
        
        # Length bonus (longer READMEs are generally better)
        length_score = min(len(readme) / 2000.0, 0.3)
        score += length_score
        
        return min(score, 1.0)
    
    def calculate_difficulty_weight(self, summary: RepoSummary) -> float:
        """Calculate difficulty weight (higher difficulty = higher weight for curation)."""
        if not summary:
            return 0.5
        
        # Convert skill level to weight (expert repos get higher weight)
        skill_numeric = summary.skill_level_numeric
        # Normalize 1-10 to 0-1, but invert so higher skill = higher weight
        return skill_numeric / 10.0
    
    def calculate_total_score(self, repo: Repo, summary: Optional[RepoSummary], all_repos: List[Repo], max_velocity: float) -> CurationScoreSchema:
        """Calculate total curation score for a repository."""
        star_velocity_score = self.calculate_star_velocity_score(repo.star_velocity, max_velocity)
        project_health_score = self.calculate_project_health_score(summary)
        uniqueness_score = self.calculate_uniqueness_score(repo, all_repos)
        readme_quality_score = self.calculate_readme_quality_score(repo.readme)
        difficulty_weight = self.calculate_difficulty_weight(summary) if summary else 0.5
        
        # Weighted sum
        total_score = (
            self.weights["star_velocity"] * star_velocity_score +
            self.weights["project_health"] * project_health_score +
            self.weights["uniqueness"] * uniqueness_score +
            self.weights["readme_quality"] * readme_quality_score +
            self.weights["difficulty_weight"] * difficulty_weight
        )
        
        return CurationScoreSchema(
            repo_id=repo.id,
            star_velocity=star_velocity_score,
            project_health=project_health_score,
            uniqueness=uniqueness_score,
            readme_quality=readme_quality_score,
            difficulty_weight=difficulty_weight,
            total_score=total_score,
            computed_at=datetime.utcnow()
        )
    
    def rank_repos(self, repo_ids: Optional[List[int]] = None) -> List[CurationScore]:
        """Rank all repositories and store scores."""
        with get_db() as db:
            if repo_ids:
                repos = db.query(Repo).filter(Repo.id.in_(repo_ids)).all()
            else:
                repos = db.query(Repo).filter(Repo.archived == False).all()
            
            # Get all summaries
            summaries = {s.repo_id: s for s in db.query(RepoSummary).all()}
            
            # Find max velocity for normalization
            max_velocity = max([r.star_velocity for r in repos], default=1.0)
            
            # Calculate scores
            scores = []
            for repo in repos:
                summary = summaries.get(repo.id)
                score_data = self.calculate_total_score(repo, summary, repos, max_velocity)
                
                # Store in database
                existing = db.query(CurationScore).filter(CurationScore.repo_id == repo.id).first()
                if existing:
                    existing.star_velocity = score_data.star_velocity
                    existing.project_health = score_data.project_health
                    existing.uniqueness = score_data.uniqueness
                    existing.readme_quality = score_data.readme_quality
                    existing.difficulty_weight = score_data.difficulty_weight
                    existing.total_score = score_data.total_score
                    existing.computed_at = datetime.utcnow()
                    scores.append(existing)
                else:
                    score = CurationScore(**score_data.dict(exclude={"computed_at"}))
                    db.add(score)
                    scores.append(score)
            
            db.commit()
            
            # Sort by total score
            scores.sort(key=lambda x: x.total_score, reverse=True)
            return scores

