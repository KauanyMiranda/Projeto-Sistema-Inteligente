from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.handlers import add_exception_handlers
from app.schemas.common import APIResponse
from app.schemas.system import RootData
from app.utils.response import success_response


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )
    add_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", response_model=APIResponse[RootData], tags=["System"])
    def root() -> APIResponse[RootData]:
        data = RootData(
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            api_prefix=settings.API_V1_PREFIX,
        )
        return success_response(message="API pronta para uso.", data=data)

    return app


app = create_application()

