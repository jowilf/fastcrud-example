from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from app.dependencies import get_templates, repository_manager
from app.graphql.schema import graphql_app
from app.internal.repository_manager import RepositoryManager

GraphQLRouter = APIRouter(prefix="/graphql", include_in_schema=False)


@GraphQLRouter.get("")
async def graphiql(
    request: Request, templates: Jinja2Templates = Depends(get_templates)
):
    return templates.TemplateResponse("graphql/graphiql.html", dict(request=request))


@GraphQLRouter.post("")
async def graphql(
    request: Request, repository: RepositoryManager = Depends(repository_manager)
):
    request.state.repository = repository
    return await graphql_app.graphql_http_server(request=request)
