#!/usr/bin/env python3
"""Initialize database for marketing agent system."""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database.models import Base
from src.core.database.session import engine


def init_database():
    """Initialize database tables."""
    print("Creating database tables...")

    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")

        # Verify table creation
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\nCreated {len(tables)} tables:")
        for table in sorted(tables):
            print(f"  - {table}")

    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()