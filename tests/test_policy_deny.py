
from backend.policy import load_policy, check_allowed
from pathlib import Path

def test_policy_deny():
    p = Path('policy/policy.yaml')
    pol = load_policy(p)
    ok, why = check_allowed(pol, 'os.py', 'system')
    assert ok is False
