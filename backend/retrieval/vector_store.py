"""Vector database for dense retrieval.

This module provides ChromaDB integration for storing and searching
document embeddings. Supports collection-based organization and
persistent storage.
"""

from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import uuid


class VectorStore:
    """ChromaDB-based vector store for document embeddings.

    Handles:
    - Document embedding and storage
    - Semantic search with similarity scoring
    - Collection management
    - Metadata filtering
    """

    def __init__(self, persist_directory: str = "./vector_db"):
        """Initialize vector store.

        Args:
            persist_directory: Path for persistent storage
        """
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.persist_directory = persist_directory

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        collection_name: str
    ):
        """Add documents to vector store.

        Args:
            texts: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            collection_name: Target collection
        """
        collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Generate unique IDs
        ids = [str(uuid.uuid4()) for _ in texts]

        # Clean metadata to only include primitive types
        clean_metadatas = [self._clean_metadata(m) for m in metadatas]

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=clean_metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        collection_name: str,
        top_k: int = 10,
        filter_dict: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            collection_name: Collection to search
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of results with text, metadata, and similarity scores
        """
        try:
            collection = self.client.get_collection(collection_name)
        except Exception:
            return []

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict
        )

        # Format results
        formatted = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted.append({
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        return formatted

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection.

        Args:
            collection_name: Collection name

        Returns:
            Statistics dictionary with counts and metadata
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
        except Exception:
            return {
                "name": collection_name,
                "count": 0,
                "metadata": {}
            }

    def delete_document(self, doc_id: str, collection_name: str):
        """Delete document from collection.

        Args:
            doc_id: Document identifier
            collection_name: Collection name
        """
        collection = self.client.get_collection(collection_name)
        collection.delete(ids=[doc_id])

    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Convert metadata values to ChromaDB-compatible types.

        ChromaDB only accepts str, int, float, or bool values.

        Args:
            metadata: Original metadata dictionary

        Returns:
            Cleaned metadata dictionary
        """
        cleaned = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            elif value is None:
                cleaned[key] = ""
            else:
                # Convert other types to string
                cleaned[key] = str(value)
        return cleaned
