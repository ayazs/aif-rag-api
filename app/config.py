import os
from dotenv import load_dotenv
from typing import Any

# Load environment variables from .env file
load_dotenv()

# Dictionary to store all settings
_settings = {}
def _load_settings() -> None:
    """Load all settings from environment variables dynamically."""
    global _settings
    
    # Load all environment variables into settings
    _settings = {key: value for key, value in os.environ.items()}

def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a setting value by key.
    
    Args:
        key: The setting key to retrieve
        default: Default value if key not found
        
    Returns:
        The setting value or default if not found
    """
    if not _settings:
        _load_settings()
    return _settings.get(key, default) 