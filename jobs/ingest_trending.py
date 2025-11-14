"""Job to ingest trending GitHub repositories."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import init_db
from ingestion_service.ingester import RepoIngester
from shared.config import settings


def main():
    """Main ingestion job."""
    print("Initializing database...")
    init_db()
    
    print("Starting ingestion of trending repositories...")
    ingester = RepoIngester()
    
    # Ingest trending repos
    repos = ingester.ingest_trending(limit=settings.ingestion_batch_size)
    
    print(f"Ingested {len(repos)} repositories")
    return repos


if __name__ == "__main__":
    main()

