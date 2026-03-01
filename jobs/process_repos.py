"""Job to process repositories: generate summaries and embeddings."""

import sys
import os
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db, init_db
from db.models import Repo, RepoSummary
from llm_service.summarizer import RepoSummarizer
from embedding_service.embedder import EmbeddingService
from embedding_service.vector_db import QdrantClient
from shared.config import settings


def process_repos(batch_size: int = 50):
    """Process repositories: generate summaries and embeddings."""
    print("Initializing services...")
    init_db()
    
    summarizer = RepoSummarizer()
    embedder = EmbeddingService()
    vector_db = QdrantClient()
    
    with get_db() as db:
        # Get repos without summaries
        repos_without_summaries = db.query(Repo).outerjoin(RepoSummary).filter(
            RepoSummary.id == None,
            Repo.archived == False
        ).limit(batch_size).all()
        
        print(f"Found {len(repos_without_summaries)} repos to process")
        
        for repo in repos_without_summaries:
            try:
                print(f"Processing repo {repo.id}: {repo.full_name}")
                
                # Generate summary
                summary = summarizer.summarize_repo(repo.id)
                if not summary:
                    print(f"  Failed to generate summary")
                    continue
                
                print(f"  Generated summary: {summary.category}")
                
                # Generate embedding
                embedding = embedder.generate_repo_embedding(repo, summary)
                
                # Store in vector DB
                embedder.store_embedding(repo.id, embedding, vector_db)
                print(f"  Stored embedding")
                
            except Exception as e:
                print(f"  Error processing repo {repo.id}: {e}")
                continue
    
    print("Processing complete")


if __name__ == "__main__":
    process_repos(batch_size=settings.ingestion_batch_size)

