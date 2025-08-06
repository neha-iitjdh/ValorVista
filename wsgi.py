"""
WSGI Entry Point for Production Deployment
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import ProductionConfig

# Create application with production config
application = create_app(ProductionConfig())

if __name__ == "__main__":
    application.run()
