# app/main.py
from litestar import Litestar
from litestar.di import Provide
from litestar.config.cors import CORSConfig
from litestar.config.compression import CompressionConfig

from app.auth.routes import *
from app.db import get_db_session

# 1. Konfigurácia CORS
cors_config = CORSConfig(
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True
)

# 2. Vytvorenie aplikácie bez session middleware
app = Litestar(
    route_handlers=[
        homepage,
        register_user,
        login_user,
        register_page,
        login_page,
        logout_user,
        dashboard_page,
    ],
    dependencies={"db_session": Provide(get_db_session)},
    cors_config=cors_config,
    compression_config=CompressionConfig(backend="gzip", minimum_size=500),
    debug=False
)