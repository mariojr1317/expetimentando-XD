from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    filename: str = ""
    extension: str = ""
    status: str = "uploaded"
    runner_session_id: str | None = None
    runner_url: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

_sessions: dict[str, Session] = {}

def create_session(filename: str, extension: str) -> Session:
    session = Session(filename=filename, extension=extension)
    _sessions[session.id] = session
    return session

def get_session(session_id: str) -> Session | None:
    return _sessions.get(session_id)
