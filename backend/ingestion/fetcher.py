"""URL-based document fetching.

This module handles fetching documents from:
1. Direct URLs (single files or HTML pages)
2. Local files directory (fallback when source_url is blank)
3. Web crawling (for sitemaps or directory listings)
"""

from pathlib import Path
from typing import List, Dict, Any
import httpx


async def fetch_from_url(
    source_url: str,
    collection_config: Dict[str, Any]
) -> List[Path]:
    """Fetch documents from source_url or local files directory.

    Args:
        source_url: URL from collection config (blank = use files dir)
        collection_config: Collection configuration dict

    Returns:
        List of file paths to process
    """
    # TODO: Implement URL fetching with httpx
    pass


async def fetch_single_page(url: str, client: httpx.AsyncClient) -> Path:
    """Fetch single HTML page or document from URL.

    Args:
        url: URL to fetch
        client: httpx AsyncClient

    Returns:
        Path to saved temporary file
    """
    # TODO: Implement single page fetching
    pass


async def crawl_website(
    base_url: str,
    client: httpx.AsyncClient,
    max_depth: int = 2
) -> List[Path]:
    """Crawl website starting from base_url.

    Args:
        base_url: Starting URL for crawl
        client: httpx AsyncClient
        max_depth: Maximum crawl depth

    Returns:
        List of fetched file paths
    """
    # TODO: Implement web crawling
    pass


def get_local_files(files_directory: Path) -> List[Path]:
    """Get all files from local files directory.

    Args:
        files_directory: Path to files directory

    Returns:
        List of file paths
    """
    # TODO: Implement local file discovery
    pass


def save_temp_file(content: bytes, filename: str) -> Path:
    """Save fetched content to temporary file.

    Args:
        content: File content as bytes
        filename: Name for temporary file

    Returns:
        Path to saved file
    """
    # TODO: Implement temporary file saving
    pass
