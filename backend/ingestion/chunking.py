"""Text chunking strategies for RAG.

This module implements semantic chunking using recursive character splitting
with configurable chunk sizes and overlap based on collection configuration.
"""

from typing import List, Dict, Any
import uuid


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[str]:
    """Split text into semantic chunks with overlap.

    Uses recursive character splitting to create chunks that respect
    document structure (paragraphs, sentences, etc.).

    Args:
        text: Input text to chunk
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks

    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []

    # Separators in order of preference
    separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""]

    chunks = []
    start = 0

    while start < len(text):
        # Calculate end position
        end = start + chunk_size

        # If this is the last chunk, take everything
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Try to find a good split point using separators
        split_point = end
        for separator in separators:
            # Look for separator near the end of the chunk
            search_start = max(start, end - 100)  # Look back up to 100 chars
            idx = text.rfind(separator, search_start, end)
            if idx != -1:
                split_point = idx + len(separator)
                break

        # Extract chunk
        chunk = text[start:split_point].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = split_point - chunk_overlap if chunk_overlap > 0 else split_point

        # Prevent infinite loop
        if start <= chunks[-1].find(text[start:start+10]) if chunks else False:
            start = split_point

    return chunks


def create_chunks_with_metadata(
    document: Dict[str, Any],
    chunk_size: int,
    chunk_overlap: int
) -> List[Dict[str, Any]]:
    """Create chunks from document with preserved metadata.

    Args:
        document: Parsed document with text and metadata
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between chunks

    Returns:
        List of chunks, each with text and metadata
    """
    # Extract text and metadata from document
    text = document.get('text', '')
    metadata = document.get('metadata', {})

    # If no text, return empty list
    if not text or not text.strip():
        return []

    # Chunk the text
    chunks = chunk_text(text, chunk_size, chunk_overlap)

    # Create chunk objects with metadata
    chunk_objects = []
    for idx, chunk in enumerate(chunks):
        chunk_metadata = {
            **metadata,
            'chunk_index': idx,
            'total_chunks': len(chunks),
            'chunk_id': str(uuid.uuid4())
        }
        chunk_objects.append({
            'text': chunk,
            'metadata': chunk_metadata
        })

    return chunk_objects
