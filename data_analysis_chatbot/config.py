"""
Configuration management for the Data Analysis Chatbot.
"""
import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from multiple sources:
    1. Default configuration
    2. Config file (YAML or JSON)
    3. Environment variables
    
    Args:
        config_path: Path to a config file (YAML or JSON)
        
    Returns:
        Dict containing the merged configuration
    """
    # Default configuration
    config = {
        "app": {
            "name": "Data Analysis Chatbot",
            "version": "0.1.0",
            "debug": False,
        },
        "database": {
            "type": "sqlite",  # sqlite, postgresql, mongodb
            "connection_string": "sqlite:///data/chatbot.db",
            "pool_size": 5,
            "max_overflow": 10,
        },
        "rag": {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "vector_db": {
                "type": "chroma",  # chroma, faiss, pinecone
                "persist_directory": "data/vectordb",
            },
        },
        "llm": {
            "provider": "openai",  # openai, huggingface, anthropic
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": ["*"],
            "auth_enabled": False,
        },
        "ui": {
            "theme": "light",
            "host": "0.0.0.0",
            "port": 8501,
        },
    }
    
    # Load from config file if provided
    if config_path:
        file_path = Path(config_path)
        if file_path.exists():
            try:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    with open(file_path, "r") as f:
                        file_config = yaml.safe_load(f)
                elif file_path.suffix.lower() == ".json":
                    with open(file_path, "r") as f:
                        file_config = json.load(f)
                else:
                    logger.warning(f"Unsupported config file format: {file_path.suffix}")
                    file_config = {}
                
                # Merge file config with default config
                _deep_merge(config, file_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
        else:
            logger.warning(f"Config file not found: {config_path}")
    
    # Override with environment variables
    _override_from_env(config)
    
    return config

def _deep_merge(target: Dict, source: Dict) -> Dict:
    """
    Deep merge two dictionaries. Values from source will override target.
    
    Args:
        target: Target dictionary
        source: Source dictionary
        
    Returns:
        Merged dictionary
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value
    return target

def _override_from_env(config: Dict, prefix: str = "APP_") -> None:
    """
    Override configuration values from environment variables.
    
    Environment variables should be prefixed with APP_ and use __ as separator
    for nested keys. For example, APP_DATABASE__CONNECTION_STRING will override
    config["database"]["connection_string"].
    
    Args:
        config: Configuration dictionary to update
        prefix: Prefix for environment variables
    """
    for env_key, env_value in os.environ.items():
        if env_key.startswith(prefix):
            # Remove prefix and split by double underscore
            key_path = env_key[len(prefix):].lower().split("__")
            
            # Convert env value to appropriate type
            if env_value.lower() in ["true", "false"]:
                env_value = env_value.lower() == "true"
            elif env_value.isdigit():
                env_value = int(env_value)
            elif env_value.replace(".", "", 1).isdigit() and env_value.count(".") == 1:
                env_value = float(env_value)
            
            # Apply the value to the nested config
            curr_dict = config
            for i, path_part in enumerate(key_path):
                if i == len(key_path) - 1:
                    # Last part of the path, set the value
                    curr_dict[path_part] = env_value
                else:
                    # Create nested dict if it doesn't exist
                    if path_part not in curr_dict:
                        curr_dict[path_part] = {}
                    curr_dict = curr_dict[path_part]