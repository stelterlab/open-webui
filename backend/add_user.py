#!/usr/bin/env python3
"""Add a user to the Open WebUI local database.

Usage:
    python add_user.py --email USER@EXAMPLE.COM --name "Full Name" \
        --password SECRET [--role user|--role admin] [--username handle]

The password is hashed with bcrypt before storage. The first user is
promoted to admin automatically (same logic as the signup route).
"""

import argparse
import sys
import uuid
from pathlib import Path

# Ensure the backend package is importable.
# The script lives next to this file; the backend code is in backend/.
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from open_webui.models.users import Users
from open_webui.models.auths import Auth
from open_webui.internal.db import ScopedSession, Base, get_db_context
from open_webui.utils.auth import get_password_hash

# Initialise tables if they don't exist yet.
Base.metadata.create_all(bind=ScopedSession.get_bind())


def main() -> None:
    parser = argparse.ArgumentParser(description="Add a user to the Open WebUI database.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--name", required=True, help="Display name")
    parser.add_argument("--password", required=True, help="User password")
    parser.add_argument("--role", default="pending", choices=["admin", "user", "pending"], help="User role")
    parser.add_argument("--username", default=None, help="Username (optional, separate from email)")
    args = parser.parse_args()

    db = ScopedSession()
    try:
        # Auto-promote first user to admin (mirrors the signup route).
        if not Users.has_users(db=db):
            args.role = "admin"

        # Check for existing email (case-insensitive).
        existing = Users.get_user_by_email(args.email, db=db)
        if existing:
            print(f"ERROR: A user with email '{args.email}' already exists (id={existing.id}).")
            sys.exit(1)

        user_id = str(uuid.uuid4())
        now = int(__import__("time").time())

        # Create User record.
        from open_webui.models.users import User, UserModel

        user = UserModel(
            id=user_id,
            email=args.email.lower(),
            name=args.name,
            role=args.role,
            profile_image_url="/user.png",
            username=args.username,
            last_active_at=now,
            created_at=now,
            updated_at=now,
        )
        user_obj = User(**user.model_dump())
        db.add(user_obj)

        # Create Auth record with bcrypt-hashed password.
        hashed_pw = get_password_hash(args.password)
        auth = Auth(
            id=user_id,
            email=args.email.lower(),
            password=hashed_pw,
            active=True,
        )
        db.add(auth)

        db.commit()
        print(f"User created: {args.name} <{args.email}>  role={args.role}  id={user_id}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
