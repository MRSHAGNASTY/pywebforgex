import os, signal, resource
from .settings import CPU_SECS_DEFAULT, MEM_MB_DEFAULT, OPEN_FILES_DEFAULT, MAX_STDOUT_BYTES
def make_preexec(max_cpu_secs=CPU_SECS_DEFAULT, max_mem_mb=MEM_MB_DEFAULT, max_files=OPEN_FILES_DEFAULT):
    mem_bytes = max(64, max_mem_mb) * 1024 * 1024
    def _fn():
        os.setsid()
        try: resource.setrlimit(resource.RLIMIT_CPU, (max_cpu_secs, max_cpu_secs))
        except Exception: pass
        try: resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        except Exception: pass
        try: resource.setrlimit(resource.RLIMIT_NOFILE, (max_files, max_files))
        except Exception: pass
        try: resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except Exception: pass
        try: os.umask(0o077)
        except Exception: pass
    return _fn
def kill_tree(pid:int):
    try:
        pgid = os.getpgid(pid); os.killpg(pgid, signal.SIGKILL)
    except Exception:
        try: os.kill(pid, signal.SIGKILL)
        except Exception: pass
def clamp_output(text:str, max_bytes:int = MAX_STDOUT_BYTES) -> str:
    b = text.encode("utf-8", "ignore")
    if len(b) <= max_bytes: return text
    head = b[:max_bytes]
    return head.decode("utf-8", "ignore") + "\n\n... (truncated)"
