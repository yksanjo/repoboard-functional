"""Repository ingestion pipeline."""

import sys
import os
from typing import List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db, init_db
from db.models import Repo
from ingestion_service.github_client import GitHubClient
from shared.schemas import RepoMetadata


class RepoIngester:
    """Service for ingesting GitHub repositories."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_client = GitHubClient(github_token)
    
    def ingest_repo(self, repo_url: str) -> Optional[Repo]:
        """Ingest a single repository by URL."""
        # Parse owner/repo from URL
        parts = repo_url.replace("https://github.com/", "").replace("http://github.com/", "").strip("/").split("/")
        if len(parts) < 2:
            print(f"Invalid repo URL: {repo_url}")
            return None
        
        owner, name = parts[0], parts[1]
        
        try:
            # Fetch repo data
            repo_data = self.github_client.get_repo_details(owner, name)
            metadata = self.github_client.fetch_repo_metadata(repo_data)
            
            # Save to database
            with get_db() as db:
                # Check if repo already exists
                existing = db.query(Repo).filter(Repo.url == str(metadata.url)).first()
                
                if existing:
                    # Update existing repo
                    for key, value in metadata.dict(exclude={"id", "created_at_db", "updated_at_db"}).items():
                        setattr(existing, key, value)
                    existing.updated_at_db = datetime.utcnow()
                    db.commit()
                    return existing
                else:
                    # Create new repo
                    repo = Repo(**metadata.dict(exclude={"id", "created_at_db", "updated_at_db"}))
                    db.add(repo)
                    db.commit()
                    db.refresh(repo)
                    return repo
        except Exception as e:
            print(f"Error ingesting {repo_url}: {e}")
            return None
    
    def ingest_trending(self, language: Optional[str] = None, limit: int = 100) -> List[Repo]:
        """Ingest trending repositories."""
        print(f"Fetching trending repos (language={language}, limit={limit})...")
        trending_repos = self.github_client.get_trending_repos(language=language)
        
        ingested = []
        for repo_data in trending_repos[:limit]:
            try:
                metadata = self.github_client.fetch_repo_metadata(repo_data)
                
                with get_db() as db:
                    existing = db.query(Repo).filter(Repo.url == str(metadata.url)).first()
                    
                    if existing:
                        # Update
                        for key, value in metadata.dict(exclude={"id", "created_at_db", "updated_at_db"}).items():
                            setattr(existing, key, value)
                        existing.updated_at_db = datetime.utcnow()
                        db.commit()
                        ingested.append(existing)
                    else:
                        # Create
                        repo = Repo(**metadata.dict(exclude={"id", "created_at_db", "updated_at_db"}))
                        db.add(repo)
                        db.commit()
                        db.refresh(repo)
                        ingested.append(repo)
                
                print(f"Ingested: {metadata.full_name}")
            except Exception as e:
                print(f"Error ingesting {repo_data.get('full_name', 'unknown')}: {e}")
                continue
        
        print(f"Ingested {len(ingested)} repositories")
        return ingested
    
    def update_repo(self, repo_id: int) -> Optional[Repo]:
        """Update an existing repository's metadata."""
        with get_db() as db:
            repo = db.query(Repo).filter(Repo.id == repo_id).first()
            if not repo:
                return None
            
            owner, name = repo.owner, repo.name
            repo_data = self.github_client.get_repo_details(owner, name)
            metadata = self.github_client.fetch_repo_metadata(repo_data)
            
            # Update fields
            for key, value in metadata.dict(exclude={"id", "created_at_db", "updated_at_db"}).items():
                setattr(repo, key, value)
            repo.updated_at_db = datetime.utcnow()
            db.commit()
            db.refresh(repo)
            return repo

