"""Agent Vault — central place for API keys and credentials.

Usage:
    from agent_vault import get_key
    openrouter_key = get_key('openrouter')
    typesafe_key = get_key('typesafe')

Keys are stored in ~/.agentvault/keys/<name>.txt
Environment variables override file-based keys.
"""
import os
from pathlib import Path

VAULT_DIR = Path.home() / '.agentvault' / 'keys'


def get_key(name: str) -> str:
    """Get an API key by name.
    
    Priority:
    1. Environment variable: UPPER_CASE_NAME_API_KEY
    2. File: ~/.agentvault/keys/<name>.txt
    3. Empty string (not found)
    """
    # Try environment variable first
    env_name = f"{name.upper()}_API_KEY"
    key = os.environ.get(env_name, '')
    if key:
        return key
    
    # Try file
    key_file = VAULT_DIR / f"{name}.txt"
    if key_file.exists():
        return key_file.read_text().strip()
    
    return ''


def has_key(name: str) -> bool:
    """Check if a key exists."""
    return bool(get_key(name))


def list_keys() -> list:
    """List available key names."""
    keys = []
    if VAULT_DIR.exists():
        for f in VAULT_DIR.iterdir():
            if f.suffix == '.txt':
                keys.append(f.stem)
    return keys
