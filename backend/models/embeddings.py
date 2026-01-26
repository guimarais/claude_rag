"""Embedding model wrapper for text vectorization.

This module provides a unified interface for generating embeddings
using sentence-transformers. Default model is nomic-embed-text-v1.5
(SOTA for retrieval, 768-dim, long context).
"""

from typing import List, Union
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding models.

    Provides consistent interface for embedding generation across
    the RAG system. Supports batch processing and caching.
    """

    def __init__(
        self,
        model_name: str = "nomic-ai/nomic-embed-text-v1.5",
        device: str = "cpu"
    ):
        """Initialize embedding model.

        Args:
            model_name: Name of sentence-transformers model
            device: Device to run model on ('cpu' or 'cuda')
        """
        self.model_name = model_name
        self.device = device
        self.model = SentenceTransformer(model_name, device=device, trust_remote_code=True)

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> Union[List[float], List[List[float]]]:
        """Generate embeddings for text(s).

        Args:
            texts: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar

        Returns:
            Single embedding or list of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )

        if single:
            return embeddings[0].tolist()
        return [emb.tolist() for emb in embeddings]

    def encode_query(self, query: str) -> List[float]:
        """Generate embedding for search query.

        Some models use different prompts for queries vs documents.

        Args:
            query: Search query text

        Returns:
            Query embedding vector
        """
        # nomic-embed uses special prefix for queries
        prefixed_query = f"search_query: {query}"
        embedding = self.model.encode(prefixed_query, convert_to_numpy=True)
        return embedding.tolist()

    def encode_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for documents.

        Args:
            documents: List of document texts

        Returns:
            List of document embeddings
        """
        # nomic-embed uses special prefix for documents
        prefixed_docs = [f"search_document: {doc}" for doc in documents]
        embeddings = self.model.encode(prefixed_docs, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    @property
    def embedding_dimension(self) -> int:
        """Get embedding dimension.

        Returns:
            Dimension of embedding vectors
        """
        return self.model.get_sentence_embedding_dimension()
