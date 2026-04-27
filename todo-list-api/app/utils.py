from datetime import datetime, UTC

from pydantic import ValidationError


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


def format_validation_error(e: ValidationError) -> str:
    messages = []
    for error in e.errors(include_url=False,include_context=False,include_input=False):
        error[]
        field = ".".join(str(loc) for loc in error["loc"])
        msg = error["msg"]
        messages.append(f"{field}: {msg}")
    return "\n".join(messages)
