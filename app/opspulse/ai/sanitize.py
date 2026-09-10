import re

_SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key id
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*\S+"),
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(api[_-]?key|token|secret|bearer)\s*[:=]\s*\S+"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT-looking
    re.compile(r"postgresql(\+\w+)?://[^\s]+"),  # DB connection strings with creds
]

_REDACTED = "[REDACTED]"


def sanitize_text(text: str, max_chars: int) -> str:
    """Strip likely secrets/credentials and enforce a hard size bound.

    This is defense-in-depth for the AI Incident Assistant input path:
    the assistant must never receive credentials, tokens, or unbounded logs.
    """
    if not text:
        return ""

    cleaned = text
    for pattern in _SECRET_PATTERNS:
        cleaned = pattern.sub(_REDACTED, cleaned)

    return cleaned[:max_chars]
