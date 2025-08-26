"""CI check: ensure OpenAPI docs are not exposed when ENV=prod and ALLOW_PUBLIC_DOCS!=1

This script sets ENV=prod and ALLOW_PUBLIC_DOCS=0 and imports the FastAPI app from
`src.app.main` and asserts that `app.openapi_url` is None. Exit code 0 on success.
"""
import os
import sys

os.environ["ENV"] = "prod"
os.environ["ALLOW_PUBLIC_DOCS"] = "0"

try:
    # Ensure service-template root is on sys.path so `src` can be imported
    from pathlib import Path
    ROOT = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(ROOT))

    # Import the app object
    from src.app.main import app
except Exception as e:
    print("ERROR importing app:", e)
    sys.exit(2)

openapi = getattr(app, "openapi_url", None)
print("openapi_url:", openapi)
if openapi is not None:
    print("Docs appear to be enabled when ENV=prod. Failing check.")
    sys.exit(1)

print("Docs are disabled for ENV=prod. OK.")
sys.exit(0)
