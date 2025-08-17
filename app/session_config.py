from dataclasses import dataclass
from litestar.middleware.session.base import BaseBackendConfig
from litestar.middleware.session.server_side import ServerSideSessionBackend
from litestar.enums import ScopeType
from typing import Optional, Any


@dataclass
class CustomSessionConfig(BaseBackendConfig[ServerSideSessionBackend]):
    _backend_class = ServerSideSessionBackend

    key: str = "session"
    max_age: int = 3600
    scopes = {ScopeType.HTTP, ScopeType.WEBSOCKET}
    path: str = "/"
    domain: str | None = None
    secure: bool = False
    httponly: bool = True
    samesite: str = "lax"
    exclude: str | list[str] | None = None
    exclude_opt_key: str = "exclude_session"
    session_id_bytes: int = 16  # Added required attribute for session ID length
    renew_on_access: bool = False

    def get_store_from_app(self, app) -> Optional[Any]:
        return app.stores.get("session")
