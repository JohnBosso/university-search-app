def usd(value):
    """Format value as USD."""
    if value is None:
        return value
    else:
        return f"${float(value):,.2f}"

def percentage(value):
    """Format value as USD."""
    if value is None:
        return value
    else:
        return f"{float(value)*100:.2f}%"

def number(value):
    """Format value as number."""
    if value is None:
        return value
    else:
        return f"{value:,}"
