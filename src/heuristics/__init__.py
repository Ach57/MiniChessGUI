# ---- Marks this directory as a package and can handle imports or initialization

'''
 ----------------------------------------------------------------------------------
|    heuristics/__init__.py                                                        |
|    This file marks the 'pieces' directory as a package and simplifies imports.   |
 ----------------------------------------------------------------------------------
'''
from .heuristics import (e0, e1, e2)

HEURISTIC_MAP = {f.__name__: f for f in (e0, e1, e2)}

__all__ = ["e0", "e1", "e2", "HEURISTIC_MAP"]