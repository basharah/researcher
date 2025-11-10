"""
Create database tables for API Gateway
Run this to create users and api_keys tables
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine
from models import Base

def create_tables():
    """Create all tables defined in models"""
    print("Creating database tables...")
    print("-" * 50)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✓ Tables created successfully:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")
        
        print("-" * 50)
        print("✓ Database initialization complete!")
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_tables()
