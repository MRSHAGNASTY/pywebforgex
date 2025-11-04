
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ExecuteRequest(BaseModel):
    module: str
    function: str
    target: str = Field(default="repaired")
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str,Any] = Field(default_factory=dict)
    with_ai: bool = False
    mode: str = "live"
    timeout_s: int = 10
    mem_mb: int = 256
    cpu_s: int = 5

class ExecuteResponse(BaseModel):
    ok: bool
    result: Optional[Any] = None
    advice: Optional[str] = None
    dry_run: Optional[bool] = None
    replayed: Optional[bool] = None
    error: Optional[str] = None

def problem(status: int, title: str, detail: str, type_: str="about:blank"):
    return {
        "type": type_,
        "title": title,
        "status": status,
        "detail": detail,
    }
