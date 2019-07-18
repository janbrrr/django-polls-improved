from .base import *


try:
    from .development import *  # remove development.py to enable production settings
except ImportError:
    from .production import *
