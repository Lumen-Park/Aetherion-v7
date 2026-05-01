# agents/__init__.py
# Ensure all subpackages are importable.

try:
    from . import governance
    from . import council
    from . import colleges
    from . import pipeline
    from . import improvement
    from . import interfaces
    from . import services  #
except ImportError:
    pass
