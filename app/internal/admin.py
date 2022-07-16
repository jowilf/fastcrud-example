from typing import Optional

from common.admin import Admin as BaseAdmin
from fastapi import Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from jose import JWTError

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
from app.models.auth import LoginBody


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

    async def render_login(
        self,
        request: Request,
        callback_url: Optional[str] = Query(None),
        rm: RepositoryManager = Depends(repository_manager),
    ):
        if request.method == "GET":
            return await super().render_login(request)
        else:
            form = await request.form()
            try:
                token_response = rm.user.login(
                    LoginBody(
                        username=form.get("username"), password=form.get("password")
                    )
                )
                if callback_url is None:
                    callback_url = request.url_for("admin")
                response = RedirectResponse(callback_url)
                response.set_cookie(
                    key="session",
                    value=token_response.access_token,
                    httponly=True,
                )
                return response

            except HTTPException:
                return await super().render_login(
                    request, error="Invalid username or password"
                )

    async def authentication_required(
        self, request: Request, rm: RepositoryManager
    ) -> bool:
        try:
            if "session" in request.cookies:
                user = rm.user.load_from_token(request.cookies.get("session"))
                return user is None
        except JWTError:
            return True
        return True

    async def render(
        self,
        request: Request,
        model: Optional[str] = Query(None),
        action: Optional[str] = Query(None),
        id: Optional[str] = Query(None),
        rm: RepositoryManager = Depends(repository_manager),
    ):
        if await self.authentication_required(request, rm):
            return RedirectResponse(
                request.url_for("admin_login") + f"?callback_url={request.url}"
            )
        if model is None:
            return RedirectResponse(
                request.url.include_query_params(model=self.models[0].identity())
            )
        if action is None:
            return RedirectResponse(request.url.include_query_params(action="list"))
        model = self._find_model_from_identity(model)
        model.rm = rm
        return await super().render_dashboard(
            request=request, model=model, action=action, pk=id
        )


admin = Admin(config.app.title)
admin.register(MovieAdmin())
admin.register(UserAdmin())
admin.register(MoviePreviewAdmin())
admin.register(CategoryAdmin())
admin.register(AuthorAdmin())
admin.register(AuthorProfileAdmin())
admin.register(ManagerAdmin())
