import os

env = os.environ.get("ENV", "prod").lower()

if env == "prod":
    from .prod import *
elif env == "staging":
    from .staging import *
else:
    from .dev import *