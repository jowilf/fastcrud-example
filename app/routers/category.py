from typing import List, Optional, Set

from common.types import FileInfo
from fastapi import (APIRouter, Depends, File, HTTPException, Path, Query,
                     Request, Response, UploadFile)
from pydantic import Json
from starlette.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                              HTTP_404_NOT_FOUND)

from app.dependencies import repository_manager
from app.filters.category import (CategoryFilter, CategoryOrderBy,
                                  HasCategoryFilter)
from app.filters.movie import MovieFilter, MovieOrderBy
from app.internal.filters import PaginationQuery
from app.internal.repository_manager import RepositoryManager
from app.internal.response import PaginatedData
from app.models.category import (Category, CategoryIn, CategoryInBase,
                                 CategoryOut, CategoryOutWithoutRelations,
                                 CategoryPatchBody, category_in_form)
from app.models.movie import Movie, MovieInBase, MovieOutWithoutRelations
from app.models.user import User
from app.services.auth import authorize

router = APIRouter(prefix="/api/categories", tags=["categories-controller"])


@router.get(
    "",
    name="categories:list",
    response_model=PaginatedData[CategoryOut],
    summary="Query all Category records",
)
async def list_all(
    request: Request,
    response: Response,
    where: Optional[Json] = Query(None),
    order_by: CategoryOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    total = repository.category.find_all(
        pagination, CategoryFilter.from_query(request), order_by, True
    )
    items = repository.category.find_all(
        pagination, CategoryFilter.from_query(request), order_by
    )
    return PaginatedData(
        items=[CategoryOut.from_orm(item) for item in items], total=total
    )


@router.get(
    "/{id}",
    name="categories:get",
    response_model=CategoryOut,
    summary="Get Category by id",
)
async def get_by_id(
    id: int = Path(...),
    exclude: Set[str] = Query({}),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.category.find_by_id(id)


@router.post(
    "",
    name="categories:create",
    response_model=CategoryOut,
    status_code=HTTP_201_CREATED,
    summary="Create new Category",
)
async def create_new(
    category_in: CategoryIn = Depends(category_in_form),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.category.create(category_in)


@router.put(
    "/{id}",
    name="categories:update",
    response_model=CategoryOut,
    summary="Update Category by id",
)
async def update(
    category_in: CategoryIn = Depends(category_in_form),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.category.update(id, category_in)


@router.patch(
    "/{id}",
    name="categories:patch",
    response_model=CategoryOut,
    summary="Partial Update Category by id",
)
async def patch_update(
    category_in: CategoryPatchBody,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    return repository.category.patch(id, category_in)


@router.put(
    "/{id}/image",
    name="categories:image:update",
    response_model=CategoryOut,
    summary="Update Category image by id",
)
async def update_image(
    image: Optional[UploadFile] = File(None),
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.image = FileInfo(content=image)
    return repository.save(category)


@router.delete(
    "/{id}/image",
    name="categories:image:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete Category image",
)
async def delete_image(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.image = None
    repository.save(category)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.delete(
    "",
    name="categories:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete Category by id",
)
async def delete_category(
    request: Request,
    where: Optional[Json] = Query(None),
    repository: RepositoryManager = Depends(repository_manager),
):
    repository.category.delete(CategoryFilter.from_query(request))
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/parent",
    name="categories:parent:get",
    response_model=CategoryOutWithoutRelations,
    summary="Get linked parent(Category)",
)
async def get_parent(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    if category.parent is None:
        raise HTTPException(HTTP_404_NOT_FOUND)
    return category.parent


@router.put(
    "/{id}/parent/{parent_id}",
    name="categories:parent:put",
    response_model=CategoryOutWithoutRelations,
    summary="Linked with parent(Category) by id",
)
async def link_parent(
    id: int = Path(...),
    parent_id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.parent_id = repository.category.find_by_id(parent_id).id
    return repository.save(category).parent


@router.delete(
    "/{id}/parent",
    name="categories:parent:delete",
    status_code=HTTP_204_NO_CONTENT,
    summary="Delete linked parent(Category)",
)
async def delete_parent(
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.parent = None
    repository.save(category)
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get(
    "/{id}/movies",
    name="categories:movies:get",
    response_model=PaginatedData[MovieOutWithoutRelations],
    summary="Get linked movies(Movie)",
)
async def get_movies(
    request: Request,
    id: int = Path(...),
    where: Optional[Json] = Query(None),
    order_by: MovieOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
    user: User = Depends(authorize(["movie:view"])),
):
    where = MovieFilter.from_query(request)
    if where is None:
        where = MovieFilter()
    where.category = HasCategoryFilter(id=id)
    total = repository.movie.find_all(pagination, where, order_by, count=True)
    items = repository.movie.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[MovieOutWithoutRelations.from_orm(item) for item in items], total=total
    )


@router.post(
    "/{id}/movies",
    name="categories:movies:add",
    response_model=MovieOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add movies(Movie)",
)
async def add_movies(
    movie_in: MovieInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    new_movie = Movie(**movie_in.dict())
    category.movies.append(new_movie)
    return repository.save(new_movie)


@router.put(
    "/{id}/movies",
    name="categories:movies:put",
    response_model=List[MovieOutWithoutRelations],
    summary="Set movies(Movie) by ids",
)
async def set_existing_movies(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.movies = repository.movie.find_by_ids(ids)
    repository.save(category)
    return repository.movie.find_by_ids(ids)


@router.get(
    "/{id}/childs",
    name="categories:childs:get",
    response_model=PaginatedData[CategoryOutWithoutRelations],
    summary="Get linked childs(Category)",
)
async def get_childs(
    request: Request,
    id: int = Path(...),
    where: Optional[Json] = Query(None),
    order_by: CategoryOrderBy = Depends(),
    pagination: PaginationQuery = Depends(),
    repository: RepositoryManager = Depends(repository_manager),
):
    where = CategoryFilter.from_query(request)
    if where is None:
        where = CategoryFilter()
    where.parent = HasCategoryFilter(id=id)
    total = repository.category.find_all(pagination, where, order_by, count=True)
    items = repository.category.find_all(pagination, where, order_by)
    return PaginatedData(
        items=[CategoryOutWithoutRelations.from_orm(item) for item in items],
        total=total,
    )


@router.post(
    "/{id}/childs",
    name="categories:childs:add",
    response_model=CategoryOutWithoutRelations,
    status_code=HTTP_201_CREATED,
    summary="Add childs(Category)",
)
async def add_childs(
    category_in: CategoryInBase,
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    new_category = Category(**category_in.dict())
    category.childs.append(new_category)
    return repository.save(new_category)


@router.put(
    "/{id}/childs",
    name="categories:childs:put",
    response_model=List[CategoryOutWithoutRelations],
    summary="Set childs(Category) by ids",
)
async def set_existing_childs(
    ids: List[int],
    id: int = Path(...),
    repository: RepositoryManager = Depends(repository_manager),
):
    category = repository.category.find_by_id(id)
    category.childs = repository.category.find_by_ids(ids)
    repository.save(category)
    return repository.category.find_by_ids(ids)
