"""Vector database client for Qdrant."""

import sys
import os
from typing import List, Dict, Any, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import settings


class QdrantClient:
    """Client for Qdrant vector database."""
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        try:
            from qdrant_client import QdrantClient as QdrantSDK
            from qdrant_client.models import Distance, VectorParams, PointStruct
        except ImportError:
            raise ImportError("qdrant-client package required. Install with: pip install qdrant-client")
        
        self.url = url or settings.qdrant_url
        self.api_key = api_key or settings.qdrant_api_key
        self.client = QdrantSDK(url=self.url, api_key=self.api_key)
        self.collection_name = "repo_embeddings"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the collection exists."""
        from qdrant_client.models import Distance, VectorParams
        
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-3-small
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Error ensuring collection: {e}")
    
    def upsert(self, collection_name: str, points: List[Dict[str, Any]]):
        """Upsert points into collection."""
        from qdrant_client.models import PointStruct
        
        point_structs = [
            PointStruct(
                id=point["id"],
                vector=point["vector"],
                payload=point.get("payload", {})
            )
            for point in points
        ]
        
        self.client.upsert(
            collection_name=collection_name,
            points=point_structs
        )
    
    def search(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def delete(self, collection_name: str, point_ids: List[int]):
        """Delete points from collection."""
        self.client.delete(
            collection_name=collection_name,
            points_selector=point_ids
        )

