from html import escape

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    if isinstance(content, str):
        return escape(content)
    elif isinstance(content, list):
        return [sanitize_html(item) for item in content]
    else:
        return content 