from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    birthday: date
    additional_data: str | None = Field(default=None, max_length=250)


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    birthday: date | None = None
    additional_data: str | None = Field(default=None, max_length=250)


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str | None = None

    model_config = ConfigDict(from_attributes=True)
