"""Database setup and data loading script"""

import sys
from pathlib import Path
from .database import Database
from .data_loader import DataLoader


def main():
    """Initialize database and load data"""
    # Get the path to loan_products.json
    current_dir = Path(__file__).parent.parent
    json_file = current_dir / "loan_products.json"

    if not json_file.exists():
        print(f"Error: {json_file} not found")
        sys.exit(1)

    print("=" * 80)
    print("Hybrid Search - Database Setup")
    print("=" * 80)
    print()

    try:
        with Database() as db:
            # Initialize database
            print("Step 1: Initialize database")
            db.initialize_database(reset=True)
            print()

            # Load data
            print("Step 2: Load data from JSON")
            loader = DataLoader(db)
            loader.load_data(str(json_file))
            print()

            print("=" * 80)
            print("Setup completed successfully!")
            print("=" * 80)
            print()
            print("You can now run searches using:")
            print('  uv run python -m search_app.main "your search query"')

    except Exception as e:
        print(f"\nError during setup: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
