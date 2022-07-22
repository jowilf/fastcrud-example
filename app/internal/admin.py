from typing import Dict, Optional

from common.admin import Admin as BaseAdmin
from fastapi import Depends, Query, Request
from fastapi.responses import RedirectResponse

from app.admin.author import AuthorAdmin
from app.admin.author_profile import AuthorProfileAdmin
from app.admin.category import CategoryAdmin
from app.admin.manager import ManagerAdmin
from app.admin.movie import MovieAdmin
from app.admin.movie_preview import MoviePreviewAdmin
from app.admin.user import UserAdmin
from app.config import config
from app.dependencies import repository_manager
from app.internal.base_models import BaseAdminModel
from app.internal.repository_manager import RepositoryManager
from app.models.user import User
from app.services.auth import authorize


class Admin(BaseAdmin):
    def datasource(self, request: Request, model: BaseAdminModel) -> str:
        return request.url_for(model.datasource())

    def admin_url(self, request: Request) -> str:
        return request.url_for("admin")

    def file_url(self, request: Request, path: str) -> str:
        return f"{request.base_url}medias/{path}"

    def admin_url_for(
        self,
        request: Request,
        model: BaseAdminModel,
        action: str = "list",
        pk=None,
    ) -> str:
        url = self.admin_url(request)
        url += f"?model={model.identity()}&action={action}"
        if action in ["show", "edit"]:
            url += f"&id={pk}"
        return url

    def ajax_headers(self, request: Request) -> Dict[str, str]:
        return {"Authorization": request.headers.get("Authorization")}

    async def render(
        self,
        request: Request,
        model: Optional[str] = Query(None),
        action: Optional[str] = Query(None),
        id: Optional[str] = Query(None),
        rm: RepositoryManager = Depends(repository_manager),
        user: User = Depends(authorize()),
    ):
        request.state.rm = rm
        if model is None:
            return RedirectResponse(
                request.url.include_query_params(model=self.models[0].identity())
            )
        if action is None:
            return RedirectResponse(request.url.include_query_params(action="list"))
        return await super().render_dashboard(
            request=request, model_identity=model, action=action, pk=id
        )


admin = Admin(config.app.title)
admin.register(MovieAdmin())
admin.register(UserAdmin())
admin.register(MoviePreviewAdmin())
admin.register(CategoryAdmin())
admin.register(AuthorAdmin())
admin.register(AuthorProfileAdmin())
admin.register(ManagerAdmin())
