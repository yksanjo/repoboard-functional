"""Repository clustering service."""

import sys
import os
from typing import List, Dict, Any, Tuple
from datetime import datetime
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_db
from db.models import Repo, Board, BoardItem
from embedding_service.vector_db import QdrantClient
from llm_service.llm_client import LLMClient
from curation_engine.ranker import RepoRanker


class RepoClusterer:
    """Service for clustering repositories and creating boards."""
    
    def __init__(self, vector_db_client: QdrantClient):
        self.vector_db = vector_db_client
        self.llm_client = LLMClient()
        self.ranker = RepoRanker()
    
    def get_repo_embeddings(self, repo_ids: List[int]) -> Dict[int, List[float]]:
        """Fetch embeddings for repositories from vector DB."""
        embeddings = {}
        for repo_id in repo_ids:
            try:
                # Search for the exact repo_id
                results = self.vector_db.search(
                    collection_name="repo_embeddings",
                    query_vector=[0.0] * 1536,  # Dummy vector, we'll filter by payload
                    limit=1000
                )
                # Filter by repo_id in payload
                for result in results:
                    if result["payload"].get("repo_id") == repo_id:
                        # We need to get the actual vector - this is a limitation
                        # In production, you'd want a direct lookup method
                        break
            except Exception as e:
                print(f"Error fetching embedding for repo {repo_id}: {e}")
                continue
        return embeddings
    
    def cluster_repos(self, n_clusters: int = 15, min_cluster_size: int = 5) -> List[Dict[str, Any]]:
        """Cluster repositories using KMeans or HDBSCAN."""
        try:
            from sklearn.cluster import KMeans, DBSCAN
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            raise ImportError("scikit-learn required. Install with: pip install scikit-learn")
        
        with get_db() as db:
            # Get all repos with summaries and embeddings
            repos = db.query(Repo).join(RepoSummary).filter(Repo.archived == False).all()
            
            if len(repos) < min_cluster_size:
                print(f"Not enough repos for clustering: {len(repos)}")
                return []
            
            # Fetch embeddings (simplified - in production, batch fetch from vector DB)
            # For now, we'll use a hybrid approach: cluster based on metadata + categories
            repo_features = []
            repo_ids = []
            
            for repo in repos:
                summary = repo.summary
                if not summary:
                    continue
                
                # Create feature vector from metadata
                features = []
                
                # Category encoding (simplified)
                categories = ["Machine Learning", "Web Framework", "Developer Tools", "Data Science", 
                             "Game Engine", "Mobile", "DevOps", "Security", "Other"]
                category_idx = categories.index(summary.category) if summary.category in categories else len(categories) - 1
                features.extend([1.0 if i == category_idx else 0.0 for i in range(len(categories))])
                
                # Skill level
                features.append(summary.skill_level_numeric / 10.0)
                
                # Project health
                features.append(summary.project_health_score)
                
                # Star velocity (normalized)
                features.append(min(repo.star_velocity / 100.0, 1.0))
                
                # Languages (top 5)
                top_langs = sorted(repo.languages.items(), key=lambda x: x[1], reverse=True)[:5] if repo.languages else []
                lang_features = [0.0] * 5
                for i, (lang, score) in enumerate(top_langs):
                    if i < 5:
                        lang_features[i] = score
                features.extend(lang_features)
                
                repo_features.append(features)
                repo_ids.append(repo.id)
            
            if len(repo_features) < n_clusters:
                n_clusters = max(2, len(repo_features) // min_cluster_size)
            
            # Normalize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(repo_features)
            
            # Cluster using KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            # Group repos by cluster
            clusters = {}
            for repo_id, label in zip(repo_ids, cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(repo_id)
            
            # Filter small clusters
            valid_clusters = {k: v for k, v in clusters.items() if len(v) >= min_cluster_size}
            
            return [
                {
                    "cluster_id": cluster_id,
                    "repo_ids": repo_ids,
                    "size": len(repo_ids)
                }
                for cluster_id, repo_ids in valid_clusters.items()
            ]
    
    def create_board_from_cluster(self, cluster: Dict[str, Any]) -> Board:
        """Create a board from a cluster of repositories."""
        with get_db() as db:
            repo_ids = cluster["repo_ids"]
            repos = db.query(Repo).filter(Repo.id.in_(repo_ids)).all()
            
            # Prepare data for LLM board name generation
            repo_names = [repo.full_name for repo in repos]
            categories = [repo.summary.category for repo in repos if repo.summary]
            all_tags = []
            for repo in repos:
                if repo.summary:
                    all_tags.extend(repo.summary.tags)
            common_tags = list(set(all_tags))[:15]
            avg_stars = sum([repo.stars for repo in repos]) / len(repos) if repos else 0
            
            # Generate board name and description
            cluster_data = {
                "repo_names": repo_names[:10],
                "categories": list(set(categories)),
                "common_tags": common_tags,
                "avg_stars": avg_stars
            }
            
            board_info = self.llm_client.generate_board_name(cluster_data)
            
            # Check if board with similar name exists
            existing = db.query(Board).filter(Board.name == board_info["name"]).first()
            if existing:
                # Update existing board
                existing.description = board_info["description"]
                existing.updated_at = datetime.utcnow()
                board = existing
            else:
                # Create new board
                board = Board(
                    name=board_info["name"],
                    description=board_info["description"],
                    category=categories[0] if categories else None,
                    repo_count=len(repo_ids)
                )
                db.add(board)
                db.commit()
                db.refresh(board)
            
            # Rank repos in cluster and add to board
            scores = self.ranker.rank_repos(repo_ids)
            
            # Clear existing items
            db.query(BoardItem).filter(BoardItem.board_id == board.id).delete()
            
            # Add repos to board with ranking
            for rank, score in enumerate(scores, 1):
                board_item = BoardItem(
                    board_id=board.id,
                    repo_id=score.repo_id,
                    rank_score=score.total_score,
                    rank_position=rank
                )
                db.add(board_item)
            
            board.repo_count = len(scores)
            db.commit()
            db.refresh(board)
            
            return board
    
    def generate_boards(self, n_clusters: int = 15) -> List[Board]:
        """Generate boards from clustered repositories."""
        print(f"Clustering repositories into {n_clusters} clusters...")
        clusters = self.cluster_repos(n_clusters=n_clusters)
        
        print(f"Creating {len(clusters)} boards...")
        boards = []
        for cluster in clusters:
            try:
                board = self.create_board_from_cluster(cluster)
                boards.append(board)
                print(f"Created board: {board.name} ({board.repo_count} repos)")
            except Exception as e:
                print(f"Error creating board from cluster: {e}")
                continue
        
        return boards

