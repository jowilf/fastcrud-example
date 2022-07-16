from pydantic import BaseModel, BaseSettings


class AppContactInfo(BaseModel):
    name = "Jocelin Hounon"
    email = "hounonj@gmail.com"


class AppInfo(BaseModel):
    title = "Netflix clone"
    description = "Video Streaming services"
    version = "0.0.1.dev"
    server = "http://localhost:8000"
    contact: AppContactInfo = AppContactInfo()


class DBConfig(BaseModel):
    username: str = "adminer"
    password: str = "adminer"
    host: str = "localhost"
    port: str = "3306"
    name: str = "fastcrud"

    def url(self):
        return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class JWTConfig(BaseModel):
    secret: str = "abcdefghijklmn"
    algorithm: str = "HS256"
    token_ttl: int = 3600
    refresh_token_ttl: int = 3600 * 24 * 30 * 3


class AppConfig(BaseSettings):
    env = "dev"
    app: AppInfo = AppInfo()
    db: DBConfig = DBConfig()
    jwt: JWTConfig = JWTConfig()

    class Config:
        env_nested_delimiter = "."


config = AppConfig()
