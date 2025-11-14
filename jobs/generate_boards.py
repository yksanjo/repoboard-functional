"""Job to generate boards from clustered repositories."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import init_db
from embedding_service.vector_db import QdrantClient
from curation_engine.clusterer import RepoClusterer
from shared.config import settings


def main():
    """Generate boards from clustered repositories."""
    print("Initializing services...")
    init_db()
    
    vector_db = QdrantClient()
    clusterer = RepoClusterer(vector_db)
    
    print("Generating boards...")
    boards = clusterer.generate_boards(n_clusters=15)
    
    print(f"Generated {len(boards)} boards:")
    for board in boards:
        print(f"  - {board.name}: {board.repo_count} repos")
    
    return boards


if __name__ == "__main__":
    main()

