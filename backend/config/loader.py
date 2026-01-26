"""Configuration loader for RAG system.

This module provides utilities for loading and accessing collection
configurations from YAML files, including routing rules for automatic
collection assignment.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from fnmatch import fnmatch


def load_collections_config() -> Dict[str, Any]:
    """Load collections.yaml configuration.

    Returns:
        Dictionary containing collections and routing rules configuration

    Raises:
        FileNotFoundError: If collections.yaml doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    config_path = Path(__file__).parent / "collections.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_collection_config(collection_name: str) -> Dict[str, Any]:
    """Get configuration for specific collection.

    Args:
        collection_name: Name of the collection

    Returns:
        Configuration dictionary for the collection, or empty dict if not found

    Example:
        >>> config = get_collection_config("technical_docs")
        >>> config['chunk_size']
        1000
    """
    config = load_collections_config()
    collections = config.get('collections', {})
    return collections.get(collection_name, {})


def determine_collection(filename: str, explicit_collection: Optional[str] = None) -> str:
    """Determine collection from filename using routing rules.

    Args:
        filename: Name of the file being uploaded
        explicit_collection: Explicitly specified collection (takes precedence)

    Returns:
        Collection name determined from routing rules or default

    Example:
        >>> determine_collection("report.pdf")
        'technical_docs'
        >>> determine_collection("FAQ_support.docx")
        'customer_support'
    """
    # If explicitly specified, use that
    if explicit_collection:
        return explicit_collection

    config = load_collections_config()
    routing_rules = config.get('routing_rules', [])

    # Match against patterns (first match wins)
    for rule in routing_rules:
        pattern = rule.get('pattern', '')
        if fnmatch(filename, pattern):
            return rule['collection']

    # Default to first collection if no pattern matches
    collections = config.get('collections', {})
    if collections:
        return list(collections.keys())[0]

    # Fallback default
    return 'default'


def list_collections() -> list[str]:
    """Get list of all configured collection names.

    Returns:
        List of collection names

    Example:
        >>> list_collections()
        ['technical_docs', 'customer_support', 'financial_reports', 'web_articles']
    """
    config = load_collections_config()
    collections = config.get('collections', {})
    return list(collections.keys())
