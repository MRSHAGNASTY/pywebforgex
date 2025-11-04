from . import register

@register("uppercase")
def uppercase(text: str) -> str:
    return text.upper()
