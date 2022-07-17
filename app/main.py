from depot.manager import DepotManager
from fastapi import Depends, FastAPI, HTTPException, Path, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import ValidationError
from starlette.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.status import HTTP_404_NOT_FOUND
from starlette.templating import Jinja2Templates

from app.config import config
from app.database import Database
from app.dependencies import get_templates
from app.graphql.router import GraphQLRouter
from app.internal.admin import admin
from app.routers import (auth, author, author_profile, category, manager,
                         movie, movie_preview, user)
from app.storage import configure_storage


def create_app() -> FastAPI:
    db = Database()
    # db.migrate_schema()

    app = FastAPI(
        title=config.app.title,
        description=config.app.description,
        version=config.app.version,
        contact=config.app.contact,
        servers=[dict(url=config.app.server)],
        # openapi_tags=tags_metadata
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    configure_storage()
    app.include_router(GraphQLRouter)
    app.include_router(movie.router)
    app.include_router(user.router)
    app.include_router(movie_preview.router)
    app.include_router(category.router)
    app.include_router(author.router)
    app.include_router(author_profile.router)
    app.include_router(manager.router)
    app.include_router(auth.router)
    app.add_api_route(
        "/admin/login",
        admin.render_login,
        name="admin_login",
        methods=["GET", "POST"],
        include_in_schema=False,
    )
    app.add_api_route(
        "/admin",
        admin.render,
        name="admin",
        methods=["GET", "POST"],
        include_in_schema=False,
    )

    return app


app = create_app()


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(
        "index.html", dict(request=request, config=config)
    )


@app.get("/medias/{storage}/{path}", response_class=FileResponse)
def get_media(storage: str = Path(...), path: str = Path(...)):
    try:
        file = DepotManager.get_file(f"{storage}/{path}")
        return FileResponse(
            file._file_path, media_type=file.content_type, filename=file.filename
        )
    except:
        raise HTTPException(HTTP_404_NOT_FOUND)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logger.exception(exc)
    return await request_validation_exception_handler(
        request, RequestValidationError(exc.raw_errors)
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(exc)
    return JSONResponse(dict(detail="An unknown error occurred."), status_code=500)
