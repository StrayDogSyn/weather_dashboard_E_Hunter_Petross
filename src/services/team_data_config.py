"""Configuration management for team data service deployment."""

import os
from pathlib import Path
from typing import Optional

from .team_data_service import TeamDataConfig


class DeploymentConfigManager:
    """Manages deployment-specific configuration for team data service."""
    
    @staticmethod
    def get_production_config() -> TeamDataConfig:
        """Get production-ready configuration with environment variable overrides."""
        return TeamDataConfig(
            github_repo_base=os.getenv(
                'TEAM_DATA_REPO_BASE',
                'https://raw.githubusercontent.com/StrayDogSyn/New_Team_Dashboard/main/exports'
            ),
            csv_filename=os.getenv(
                'TEAM_DATA_CSV_FILE',
                'team_weather_data_20250717_204218.csv'
            ),
            json_filename=os.getenv(
                'TEAM_DATA_JSON_FILE',
                'team_compare_cities_data_20250717_204218.json'
            ),
            cache_ttl_seconds=int(os.getenv('TEAM_DATA_CACHE_TTL', '3600')),
            max_retries=int(os.getenv('TEAM_DATA_MAX_RETRIES', '3')),
            request_timeout=int(os.getenv('TEAM_DATA_REQUEST_TIMEOUT', '30'))
        )
    
    @staticmethod
    def get_development_config() -> TeamDataConfig:
        """Get development configuration with shorter cache TTL."""
        return TeamDataConfig(
            cache_ttl_seconds=300,  # 5 minutes for development
            max_retries=2,
            request_timeout=15
        )
    
    @staticmethod
    def get_testing_config() -> TeamDataConfig:
        """Get testing configuration with minimal cache."""
        return TeamDataConfig(
            cache_ttl_seconds=60,  # 1 minute for testing
            max_retries=1,
            request_timeout=10
        )
    
    @staticmethod
    def create_deployment_env_template() -> str:
        """Create environment variable template for deployment."""
        return """# Team Data Service Configuration
# Production Environment Variables

# GitHub Repository Settings
TEAM_DATA_REPO_BASE=https://raw.githubusercontent.com/StrayDogSyn/New_Team_Dashboard/main/exports
TEAM_DATA_CSV_FILE=team_weather_data_20250717_204218.csv
TEAM_DATA_JSON_FILE=team_compare_cities_data_20250717_204218.json

# Performance Settings
TEAM_DATA_CACHE_TTL=3600
TEAM_DATA_MAX_RETRIES=3
TEAM_DATA_REQUEST_TIMEOUT=30

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
"""


def save_deployment_env_template(path: Optional[Path] = None) -> Path:
    """Save deployment environment template to file."""
    if path is None:
        path = Path(__file__).parent.parent.parent / '.env.team_data_template'
    
    path.write_text(DeploymentConfigManager.create_deployment_env_template())
    return path