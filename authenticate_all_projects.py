"""
Re-authenticate all YouTube API projects with the full 'youtube' scope.
Run this whenever the OAuth scope changes (e.g. adding read/delete permissions).

Usage:
  python3 authenticate_all_projects.py

The script will:
  1. Decode client secrets from YOUTUBE_CLIENT_SECRET_N_B64 env vars (or local files)
  2. Open your browser once per project to approve OAuth
  3. Save token_N.json files locally
  4. Print the 'railway variables set' commands to update Railway
"""

import base64
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ── Must match the scope in all_platforms_youtube.py ─────────────────────────
SCOPES = ["https://www.googleapis.com/auth/youtube"]

BASE_DIR = Path(__file__).parent


def _get_secret_file(n: int) -> Path | None:
    """Return a path to client_secret_N.json, decoding from env var if needed."""
    local = BASE_DIR / f"client_secret_{n}.json"
    if local.exists():
        return local

    b64 = os.getenv(f"YOUTUBE_CLIENT_SECRET_{n}_B64")
    if b64:
        local.write_bytes(base64.b64decode(b64))
        print(f"  ✓ client_secret_{n}.json decoded from env var")
        return local

    return None


def _token_has_full_scope(token_file: Path) -> bool:
    """Return True if an existing token already has the full youtube scope."""
    try:
        import json
        data = json.loads(token_file.read_text(encoding="utf-8"))
        scopes = data.get("scopes", [])
        return "https://www.googleapis.com/auth/youtube" in scopes
    except Exception:
        return False


def authenticate_project(n: int) -> bool:
    secret_file = _get_secret_file(n)
    if not secret_file:
        print(f"  ✗ No client_secret_{n}.json and no YOUTUBE_CLIENT_SECRET_{n}_B64 env var — skipping")
        return False

    token_file = BASE_DIR / f"token_{n}.json"

    # Skip if already has full scope
    if token_file.exists() and _token_has_full_scope(token_file):
        print(f"  ✓ Project {n} already has full scope — skipping")
        return True

    # Delete old token — it was issued for the wrong scope
    if token_file.exists():
        token_file.unlink()
        print(f"  🗑  Removed old token_{n}.json (wrong scope)")

    print(f"  → Opening browser for Project {n} — log in with your YouTube channel account")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"  ✓ token_{n}.json saved")
        return True
    except Exception as e:
        print(f"  ✗ Auth failed for project {n}: {e}")
        return False


def main():
    print("=" * 60)
    print("  YouTube Re-Authentication (scope: youtube full access)")
    print("=" * 60)
    print()

    # Discover which project numbers exist
    project_nums = []
    for i in range(1, 20):
        has_file = (BASE_DIR / f"client_secret_{i}.json").exists()
        has_env  = bool(os.getenv(f"YOUTUBE_CLIENT_SECRET_{i}_B64"))
        if has_file or has_env:
            project_nums.append(i)
        elif i > 5 and not project_nums:
            break
        elif i > max(project_nums or [0]) + 2:
            break

    if not project_nums:
        print("✗ No client secrets found.")
        print()
        print("Either:")
        print("  • Place client_secret_1.json, client_secret_2.json, etc. in this folder")
        print("  • Or set YOUTUBE_CLIENT_SECRET_1_B64 etc. as environment variables")
        print("    (copy the values from Railway dashboard → Variables)")
        sys.exit(1)

    print(f"Found {len(project_nums)} project(s): {project_nums}")
    print()
    print("Starting authentication — a browser window will open for each project that needs it...")
    print()

    results = {}
    for n in project_nums:
        print(f"\n── Project {n} ──────────────────────────────────────")
        results[n] = authenticate_project(n)

    # ── Summary + Railway commands ────────────────────────────────────────
    print()
    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    ok = [n for n, v in results.items() if v]
    fail = [n for n, v in results.items() if not v]

    if ok:
        print(f"✓ Authenticated: projects {ok}")
        print()
        print("Run these commands to update Railway (copy-paste each line):")
        print()
        for n in ok:
            token_file = BASE_DIR / f"token_{n}.json"
            if token_file.exists():
                token_json = token_file.read_text(encoding="utf-8").replace("'", "'\\''")
                print(f"railway variables set YOUTUBE_TOKEN_{n}_JSON='{token_json}'")
                print()

    if fail:
        print(f"✗ Failed: projects {fail}")

    if not fail:
        print("All done! After setting the Railway variables, redeploy the service.")


if __name__ == "__main__":
    main()
