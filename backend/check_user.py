#!/usr/bin/env python3
"""Check if a user with a given email exists in the Open WebUI database.

Usage:
    python check_user.py --email USER@EXAMPLE.COM

Exit code 0 means the user exists (with details printed).
Exit code 1 means the user was not found.
"""

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from open_webui.models.users import Users


def main() -> None:
    parser = argparse.ArgumentParser(description="Check if a user exists by email.")
    parser.add_argument("--email", required=True, help="Email address to look up")
    args = parser.parse_args()

    user = Users.get_user_by_email(args.email)
    if user:
        print(f"User found:  id={user.id}")
        print(f"            email={user.email}")
        print(f"           name={user.name}")
        print(f"          role={user.role}")
        print(f"     username={user.username or '(none)'}")
        sys.exit(0)
    else:
        print(f"User not found: {args.email}")
        sys.exit(1)


if __name__ == "__main__":
    main()
