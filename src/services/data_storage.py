"""Data storage service implementations."""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from ..interfaces.weather_interfaces import IDataStorage


class FileDataStorage(IDataStorage):
    """File-based data storage implementation."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize file storage.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        logging.info(f"File storage initialized at: {self.data_dir.absolute()}")
    
    def save_data(self, data: Dict[str, Any], filename: str) -> bool:
        """
        Save data to file.
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        filepath = self.data_dir / filename
        
        try:
            # Ensure the file has .json extension
            if not filepath.suffix:
                filepath = filepath.with_suffix('.json')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logging.info(f"Data saved to {filepath}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving data to {filepath}: {e}")
            return False
    
    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from file.
        
        Args:
            filename: Name of the file
            
        Returns:
            Loaded data or None if error
        """
        filepath = self.data_dir / filename
        
        # Try with .json extension if not present
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        try:
            if not filepath.exists():
                logging.warning(f"File not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logging.info(f"Data loaded from {filepath}")
            return data
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error loading {filepath}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading data from {filepath}: {e}")
            return None
    
    def delete_data(self, filename: str) -> bool:
        """
        Delete data file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        filepath = self.data_dir / filename
        
        # Try with .json extension if not present
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        try:
            if filepath.exists():
                filepath.unlink()
                logging.info(f"Data file deleted: {filepath}")
                return True
            else:
                logging.warning(f"File not found for deletion: {filepath}")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting file {filepath}: {e}")
            return False
    
    def list_files(self) -> List[str]:
        """
        List all data files.
        
        Returns:
            List of filenames
        """
        try:
            files = [f.name for f in self.data_dir.iterdir() if f.is_file()]
            return sorted(files)
        except Exception as e:
            logging.error(f"Error listing files: {e}")
            return []
    
    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file exists, False otherwise
        """
        filepath = self.data_dir / filename
        
        # Try with .json extension if not present
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        return filepath.exists()
    
    def get_file_size(self, filename: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            filename: Name of the file
            
        Returns:
            File size in bytes or None if error
        """
        filepath = self.data_dir / filename
        
        # Try with .json extension if not present
        if not filepath.suffix:
            filepath = filepath.with_suffix('.json')
        
        try:
            if filepath.exists():
                return filepath.stat().st_size
            return None
        except Exception as e:
            logging.error(f"Error getting file size for {filepath}: {e}")
            return None
