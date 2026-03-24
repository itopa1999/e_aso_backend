# backend/settings/__init__.py
from pathlib import Path
from dotenv import load_dotenv
import os

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env **first**, before reading ENV
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Now read ENV
env = os.environ.get("ENV", "dev").lower()

if env == "prod":
    from .prod import *
elif env == "staging":
    from .staging import *
else:
    from .dev import *