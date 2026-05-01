# agents/__init__.py
# Ensure all subpackages are importable.

try:
    from . import (
        colleges,
        council,
        governance,
        improvement,
        interfaces,
        pipeline,
        services,
    )
except ImportError:
    pass
