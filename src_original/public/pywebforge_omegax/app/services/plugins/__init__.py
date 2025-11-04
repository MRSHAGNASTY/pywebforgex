from typing import Dict, Callable

REGISTRY: Dict[str, Callable] = {}

def register(name: str):
    def deco(fn: Callable):
        REGISTRY[name] = fn
        return fn
    return deco
