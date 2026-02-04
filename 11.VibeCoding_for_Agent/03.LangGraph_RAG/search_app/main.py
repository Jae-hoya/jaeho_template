"""Main CLI for hybrid search"""

import sys
import io
from .database import Database
from .hybrid_search import HybridSearch

# Fix Korean encoding issue on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    """Run hybrid search from command line"""
    if len(sys.argv) < 2:
        print("Usage: uv run python -m search_app.main <search_query>")
        print('Example: uv run python -m search_app.main "의사 전용 대출"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        with Database() as db:
            search = HybridSearch(db)
            results = search.search(query, limit=10)
            search.print_results(results)

    except Exception as e:
        print(f"\nError during search: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
