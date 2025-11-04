
class Advisor:
    def suggest_from_exception(self, tb: str) -> str:
        if "ImportError" in tb: return "Missing dependency – try installing the module indicated."
        if "TypeError" in tb: return "Argument mismatch – check function signature and JSON inputs."
        if "FileNotFoundError" in tb: return "Check file paths and permissions."
        return "Review the traceback; try Dry-Run first to validate the plan."
ADVISOR = Advisor()
