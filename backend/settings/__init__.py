import os

env = os.environ.get("ENV", "dev").lower()

if env == "prod":
    from .prod import *
elif env == "staging":
    from .staging import *
else:
    from .dev import *