from ariadne import (MutationType, QueryType, ScalarType, gql,
                     make_executable_schema)
from ariadne.asgi import GraphQL
from common.types import FileInfo

from app.config import config
from app.graphql.error import format_error
from app.graphql.resolvers.auth import me, register
from app.graphql.resolvers.author import (create_author, delete_authors,
                                          get_authors, get_one_author,
                                          patch_author, update_author)
from app.graphql.resolvers.author_profile import (create_author_profile,
                                                  delete_author_profiles,
                                                  get_author_profiles,
                                                  get_one_author_profile,
                                                  patch_author_profile,
                                                  update_author_profile)
from app.graphql.resolvers.category import (create_category, delete_categories,
                                            get_categories, get_one_category,
                                            patch_category, update_category)
from app.graphql.resolvers.manager import (create_manager, delete_managers,
                                           get_managers, get_one_manager,
                                           patch_manager, update_manager)
from app.graphql.resolvers.movie import (create_movie, delete_movies,
                                         get_movies, get_one_movie,
                                         patch_movie, update_movie)
from app.graphql.resolvers.movie_preview import (create_movie_preview,
                                                 delete_movie_previews,
                                                 get_movie_previews,
                                                 get_one_movie_preview,
                                                 patch_movie_preview,
                                                 update_movie_preview)
from app.graphql.resolvers.user import (delete_users, get_one_user, get_users,
                                        patch_user, update_user)

type_defs = gql(open("./app/graphql/schema.graphql").read())

query = QueryType()
mutation = MutationType()

mutation.set_field("Auth_me", me)
mutation.set_field("Auth_register", register)


query.set_field("Movie", get_movies)
query.set_field("Movie_by_id", get_one_movie)
mutation.set_field("create_Movie", create_movie)
mutation.set_field("update_Movie", update_movie)
mutation.set_field("patch_Movie", patch_movie)
mutation.set_field("delete_Movie", delete_movies)

query.set_field("User", get_users)
query.set_field("User_by_id", get_one_user)
mutation.set_field("update_User", update_user)
mutation.set_field("patch_User", patch_user)
mutation.set_field("delete_User", delete_users)

query.set_field("MoviePreview", get_movie_previews)
query.set_field("MoviePreview_by_id", get_one_movie_preview)
mutation.set_field("create_MoviePreview", create_movie_preview)
mutation.set_field("update_MoviePreview", update_movie_preview)
mutation.set_field("patch_MoviePreview", patch_movie_preview)
mutation.set_field("delete_MoviePreview", delete_movie_previews)

query.set_field("Category", get_categories)
query.set_field("Category_by_id", get_one_category)
mutation.set_field("create_Category", create_category)
mutation.set_field("update_Category", update_category)
mutation.set_field("patch_Category", patch_category)
mutation.set_field("delete_Category", delete_categories)

query.set_field("Author", get_authors)
query.set_field("Author_by_id", get_one_author)
mutation.set_field("create_Author", create_author)
mutation.set_field("update_Author", update_author)
mutation.set_field("patch_Author", patch_author)
mutation.set_field("delete_Author", delete_authors)

query.set_field("AuthorProfile", get_author_profiles)
query.set_field("AuthorProfile_by_id", get_one_author_profile)
mutation.set_field("create_AuthorProfile", create_author_profile)
mutation.set_field("update_AuthorProfile", update_author_profile)
mutation.set_field("patch_AuthorProfile", patch_author_profile)
mutation.set_field("delete_AuthorProfile", delete_author_profiles)

query.set_field("Manager", get_managers)
query.set_field("Manager_by_id", get_one_manager)
mutation.set_field("create_Manager", create_manager)
mutation.set_field("update_Manager", update_manager)
mutation.set_field("patch_Manager", patch_manager)
mutation.set_field("delete_Manager", delete_managers)


upload_scalar = ScalarType("Upload")


@upload_scalar.value_parser
def parse_upload_file(value):
    return FileInfo(content=value)


schema = make_executable_schema(type_defs, query, mutation, upload_scalar)
graphql_app = GraphQL(
    schema, debug=(config.env != "prod"), error_formatter=format_error
)
