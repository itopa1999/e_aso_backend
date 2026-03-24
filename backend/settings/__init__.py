from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env before any settings import
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Now read ENV and import the appropriate settings
env = os.environ.get("ENV", "dev").lower()

if env == "prod":
    from .prod import *
elif env == "staging":
    from .staging import *
else:
    from .dev import *