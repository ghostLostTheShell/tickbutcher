
from importlib.metadata import version, PackageNotFoundError

try:
    # __package__ is the name of the current package, e.g., "tick_butcher"
    # This name must match the name defined in pyproject.toml's [tool.poetry] section
    __version__ = version(__package__)
except PackageNotFoundError:
    # This is a fallback for when the package is not installed, e.g., when running tests
    # directly from the source directory without installation.
    __version__ = "0.0.0-dev"
    
if __name__ == "__main__":
    print(f"Current package version: {__version__}")  