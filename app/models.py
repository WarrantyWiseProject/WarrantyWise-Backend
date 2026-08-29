from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic

class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=128)

class ItemBase(BaseModel):
    item_name: str = Field(min_length=1, max_length=200)
    date_purchased: str
    warranty_date: str
    photo_url: str | None = None

    @field_validator("date_purchased", "warranty_date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        for pattern in ("%d-%m-%Y", "%d-%m-%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, pattern).strftime("%d-%m-%Y")
            except ValueError:
                continue
        raise ValueError("Date must use DD-MM-YYYY or YYYY-MM-DD format")

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    item_name: str | None = Field(None, min_length=1, max_length=200)
    date_purchased: str | None = None
    warranty_date: str | None = None
    photo_url: str | None = None

    @field_validator("date_purchased", "warranty_date")
    @classmethod
    def validate_date(cls, value: str | None) -> str | None:
        return ItemBase.validate_date(value) if value is not None else None

class ItemPublic(ItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    photo: bool
