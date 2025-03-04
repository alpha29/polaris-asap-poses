from importlib.metadata import version
from pathlib import Path

__version__ = version(__package__)

module_root = Path(__file__).parent
