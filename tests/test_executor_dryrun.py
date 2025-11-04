from backend.executor import call_function
from pathlib import Path

def test_dryrun(tmp_path):
    p = tmp_path/'m.py'; p.write_text('def a(x):\n    return x+1')
    r = call_function(p,'a',[1],{},dry_run=True)
    assert r['ok'] and r['dry_run']
