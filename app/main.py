from litestar import Litestar
from litestar.di import Provide
from litestar.config.cors import CORSConfig
from litestar.config.compression import CompressionConfig
from litestar.middleware.session import SessionMiddleware
from app.session_config import CustomSessionConfig
from litestar.stores.memory import MemoryStore
from litestar.plugins.flash import FlashPlugin, FlashConfig
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from pathlib import Path

from app.auth.routes import (
    homepage,
    register_user,
    login_user,
    register_page,
    login_page,
    logout_user,
    dashboard_page,
    create_category,
    add_word,
    change_word_level,
    delete_word,
    category_detail_page,
    edit_category,
    delete_category,
    import_excel_words,
    test_words,
    test_page,
    test_flash,
    words_page
)

from app.db import get_db_session
from on_startup import on_startup

# Konfigurácia CORS
cors_config = CORSConfig(
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_credentials=True
)

# Konfigurácia šablón
template_config = TemplateConfig(
    directory=Path("app/auth/templates"),
    engine=JinjaTemplateEngine
)

# Vytvorenie úložiska pre session
session_store = MemoryStore()

# Custom session config instance
custom_session_config = CustomSessionConfig()

# Flash plugin
flash_plugin = FlashPlugin(config=FlashConfig(template_config=template_config))

from starlette.middleware.base import BaseHTTPMiddleware
import logging

class SessionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Log incoming request cookies
        logging.info(f"Request cookies: {request.cookies}")

        response = await call_next(request)

        # Log response headers for Set-Cookie
        set_cookie = response.headers.get("set-cookie")
        logging.info(f"Response Set-Cookie header: {set_cookie}")

        return response

app = Litestar(
    route_handlers=[
        homepage,
        register_user,
        login_user,
        register_page,
        login_page,
        logout_user,
        dashboard_page,
        create_category,
        add_word,
        change_word_level,
        delete_word,
        category_detail_page,
        edit_category,
        delete_category,
        import_excel_words,
        test_words,
        test_page,
        test_flash,
        words_page
    ],
    dependencies={"db_session": Provide(get_db_session)},
    cors_config=cors_config,
    compression_config=CompressionConfig(backend="gzip", minimum_size=500),
    on_startup=[on_startup],
    debug=True,
    middleware=[SessionLoggingMiddleware, custom_session_config.middleware],
    template_config=template_config,
    stores={"session": session_store},
    plugins=[flash_plugin]
)


