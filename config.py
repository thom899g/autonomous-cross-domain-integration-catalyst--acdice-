"""
ACDICE Configuration Manager with Environment-Based Settings
Architectural Choice: Using Pydantic for runtime validation and type safety.
This prevents configuration errors from propagating through the system.
"""
import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field, validator
from loguru import logger
from pathlib import Path

class ACDCIConfig(BaseSettings):
    """Main configuration class for ACDICE system"""
    
    # Firebase Configuration
    firebase_project_id: str = Field(
        default="acdice-production",
        description="Firebase project ID for state management"
    )
    firestore_collection_prefix: str = Field(
        default="acdice_",
        description="Prefix for Firestore collections to avoid collisions"
    )
    
    # ML Model Configuration
    ml_model_path: str = Field(
        default="models/integration_predictor.joblib",
        description="Path to trained ML model for integration point prediction"
    )
    prediction_confidence_threshold: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for ML predictions"
    )
    
    # Integration Settings
    max_concurrent_integrations: int = Field(
        default=10,
        gt=0,
        description="Maximum number of concurrent cross-domain integrations"
    )
    integration_timeout_seconds: int = Field(
        default=30,
        gt=0,
        description="Timeout for integration operations"
    )
    
    # Research Module Settings
    exploration_rate: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Rate at which research module explores new integration opportunities"
    )
    knowledge_base_refresh_hours: int = Field(
        default=24,
        gt=0,
        description="Frequency of knowledge base updates in hours"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    log_retention_days: int = Field(
        default=30,
        gt=0,
        description="Days to retain log files"
    )
    
    # Performance Monitoring
    metrics_collection_interval: int = Field(
        default=300,
        gt=0,
        description="Seconds between metrics collection cycles"
    )
    
    @validator("ml_model_path")
    def validate_model_path(cls, v: str) -> str:
        """Ensure model directory exists"""
        model_dir = Path(v).parent
        model_dir.mkdir(parents=True, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_prefix = "acdice_"
        case_sensitive = False

# Global configuration instance
config = ACDCIConfig()

def validate_configuration() -> bool:
    """Validate all configuration parameters on startup"""
    try:
        # Test Firebase connectivity if credentials are provided
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            logger.info("Firebase credentials found, will validate on initialization")
        
        # Validate critical paths
        critical_paths = ["ml_model_path"]
        for path_attr in critical_paths:
            path = getattr(config, path_attr, None)
            if path:
                parent_dir = Path(path).parent
                if not parent_dir.exists():
                    logger.warning(f"Directory does not exist: {parent_dir}")
                    parent_dir.mkdir(parents=True, exist_ok=True)
        
        logger.success("Configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return False