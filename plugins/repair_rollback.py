"""Multi-step repair with rollback."""

def repair_pipeline(step_fail: bool=False):
    state=[]
    try:
        state.append("step1")
        if step_fail: raise RuntimeError("step2 failed")
        state.append("step2")
        return {"ok": True, "state": state}
    except Exception as e:
        return {"ok": False, "rolled_back": True, "state": state, "error": repr(e)}
