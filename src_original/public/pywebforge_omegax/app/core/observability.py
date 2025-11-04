import json, time, threading, collections
_metrics = collections.Counter()
_hist = collections.defaultdict(list)
_lock = threading.Lock()
def jlog(event:str, **fields):
    rec = {"ts": time.time(), "event": event, **fields}
    print(json.dumps(rec, ensure_ascii=False))
def metric(name:str, value:float=1.0):
    with _lock: _metrics[name] += value
def observe_duration(name:str, ms:int):
    with _lock:
        _hist[name].append(ms)
        if len(_hist[name]) > 1000: _hist[name] = _hist[name][-1000:]
def snapshot():
    with _lock:
        avg = {k: (sum(v)/len(v) if v else 0.0) for k,v in _hist.items()}
        return {"metrics": dict(_metrics), "avg_ms": avg, "hist_count": {k:len(v) for k,v in _hist.items()}}
