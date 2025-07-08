#!/usr/bin/env python3
"""
Project Cleanup Script for Weather Dashboard

This script cleans up temporary files, cache directories, and other artifacts
that should not be committed to version control.
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_project():
    """Clean up the project directory."""
    project_root = Path(__file__).parent
    
    print("🧹 Starting project cleanup...")
    
    # Directories to clean
    cache_dirs = [
        "__pycache__",
        ".pytest_cache", 
        ".mypy_cache",
        ".coverage",
        "htmlcov",
        ".tox",
        ".nox",
        "build",
        "dist",
        "*.egg-info"
    ]
    
    # Files to clean
    temp_files = [
        "*.pyc",
        "*.pyo", 
        "*.pyd",
        "*.so",
        "*.tmp",
        "*.bak",
        "*.swp",
        "*.swo",
        "*~",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    # Clean cache directories
    for cache_dir in cache_dirs:
        for path in project_root.glob(f"**/{cache_dir}"):
            if path.is_dir():
                print(f"  📁 Removing directory: {path}")
                shutil.rmtree(path, ignore_errors=True)
    
    # Clean temporary files
    for file_pattern in temp_files:
        for path in project_root.glob(f"**/{file_pattern}"):
            if path.is_file():
                print(f"  🗑️  Removing file: {path}")
                path.unlink()
    
    # Clean empty directories
    empty_dirs = ["cache", "exports", "logs"]
    for dirname in empty_dirs:
        dir_path = project_root / dirname
        if dir_path.exists() and not any(dir_path.iterdir()):
            print(f"  📂 Directory {dirname}/ is empty (keeping for structure)")
    
    print("✅ Project cleanup completed!")
    print("\n📋 Project structure after cleanup:")
    
    # Show clean project structure
    show_project_structure(project_root)

def show_project_structure(root_path, max_depth=2):
    """Show the project structure after cleanup."""
    
    exclude_dirs = {'.git', '.venv', '__pycache__', '.pytest_cache', '.mypy_cache'}
    
    def print_tree(path, prefix="", depth=0):
        if depth > max_depth:
            return
            
        items = sorted([p for p in path.iterdir() 
                       if not p.name.startswith('.') or p.name in {'.env.example', '.gitignore'}])
        
        for i, item in enumerate(items):
            if item.name in exclude_dirs:
                continue
                
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and depth < max_depth:
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, depth + 1)
    
    print(f"{root_path.name}/")
    print_tree(root_path)

if __name__ == "__main__":
    cleanup_project()
