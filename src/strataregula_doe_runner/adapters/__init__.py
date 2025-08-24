"""
実行アダプター
"""

from .base import BaseAdapter
from .shell import ShellAdapter
from .dummy import DummyAdapter

# simroute アダプターは extras 依存のため動的インポート
try:
    from .simroute import SimrouteAdapter
    _SIMROUTE_AVAILABLE = True
except ImportError:
    SimrouteAdapter = None
    _SIMROUTE_AVAILABLE = False

__all__ = [
    "BaseAdapter",
    "ShellAdapter", 
    "DummyAdapter",
]

if _SIMROUTE_AVAILABLE:
    __all__.append("SimrouteAdapter")