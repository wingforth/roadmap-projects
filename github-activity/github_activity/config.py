"""
Configuration

GITHUB_TOKEN: GitHub access token.
CACHE_DIR: The directory of HTTP request cache.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
CACHE_DIR = Path(__file__).resolve().parent.parent / "data/cache"
