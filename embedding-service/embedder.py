"""Service for generating and managing embeddings."""

import sys
import os
from typing import List, Optional, Dict, Any
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import settings
from db.connection import get_db
from db.models import Repo, RepoSummary


class EmbeddingService:
    """Service for generating embeddings using OpenAI or other providers."""
    
    def __init__(self):
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # OpenAI text-embedding-3-small dimension
        
        # Initialize client based on provider
        if settings.llm_provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                self._generate_embedding = self._generate_openai_embedding
            except ImportError:
                raise ImportError("openai package required. Install with: pip install openai")
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    
    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def generate_repo_embedding(self, repo: Repo, summary: Optional[RepoSummary] = None) -> List[float]:
        """Generate embedding for a repository."""
        # Combine repo metadata into text for embedding
        text_parts = []
        
        # Add description
        if repo.description:
            text_parts.append(repo.description)
        
        # Add README (truncated to first 2000 chars)
        if repo.readme:
            text_parts.append(repo.readme[:2000])
        
        # Add summary if available
        if summary:
            text_parts.append(summary.summary)
            text_parts.append(" ".join(summary.tags))
            text_parts.append(summary.category)
        
        # Add languages
        if repo.languages:
            top_languages = sorted(repo.languages.items(), key=lambda x: x[1], reverse=True)[:5]
            text_parts.append(" ".join([lang for lang, _ in top_languages]))
        
        # Add topics
        if repo.topics:
            text_parts.append(" ".join(repo.topics))
        
        combined_text = "\n".join(text_parts)
        return self._generate_embedding(combined_text)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch."""
        if settings.llm_provider == "openai":
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        else:
            # Fallback to individual calls
            return [self._generate_embedding(text) for text in texts]
    
    def store_embedding(self, repo_id: int, embedding: List[float], vector_db_client):
        """Store embedding in vector database."""
        vector_db_client.upsert(
            collection_name="repo_embeddings",
            points=[{
                "id": repo_id,
                "vector": embedding,
                "payload": {"repo_id": repo_id}
            }]
        )
    
    def search_similar(self, query_embedding: List[float], vector_db_client, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar repositories using vector similarity."""
        results = vector_db_client.search(
            collection_name="repo_embeddings",
            query_vector=query_embedding,
            limit=limit
        )
        return results

