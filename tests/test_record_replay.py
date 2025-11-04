
from backend.record_replay import record, replay
from pathlib import Path
def test_record_replay(tmp_path):
    store = tmp_path
    tenant='t'; mod='m.py'; fn='f'; args=[1]; kwargs={'k':2}
    record(store, tenant, mod, fn, args, kwargs, {'ok':True,'result':3})
    hit = replay(store, tenant, mod, fn, args, kwargs)
    assert hit and hit.get('result')==3
