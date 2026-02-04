import os
import sys


def _ensure_src_on_path() -> None:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(repo_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)


def main() -> None:
    _ensure_src_on_path()
    from seoul_culture_mcp.server import main as server_main

    server_main()


if __name__ == "__main__":
    main()
