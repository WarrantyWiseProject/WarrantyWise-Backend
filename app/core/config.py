from functools import lru_cache
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mongo_uri: str = Field(..., validation_alias="MONGO_URI")
    mongo_db_name: str = Field("warrantywise", validation_alias="MONGO_DB_NAME")
    frontend_url: str = Field(..., validation_alias="FRONTEND_URL")
    jwt_secret_key: SecretStr = Field(..., validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    google_drive_folder_link: str | None = Field(None, validation_alias="GOOGLE_DRIVE_FOLDER_LINK")
    google_drive_credentials_json: SecretStr | None = Field(None, validation_alias="GOOGLE_DRIVE_CREDENTIALS_JSON")
    google_drive_credentials_file: str | None = Field(None, validation_alias="GOOGLE_DRIVE_CREDENTIALS_FILE")
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]

    @field_validator("access_token_expire_minutes")
    @classmethod
    def positive_expiry(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
        return value

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
