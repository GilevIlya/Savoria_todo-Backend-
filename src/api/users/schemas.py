from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserUpdateSchema(BaseModel):
    firstname: Optional[str] = Field(
        default=None, min_length=1, max_length=50, pattern=r"^[A-Za-zА-Яа-яЁё]+$"
    )
    lastname: Optional[str] = Field(
        default=None, min_length=1, max_length=50, pattern=r"^[A-Za-zА-Яа-яЁё]+$"
    )
    email: Optional[EmailStr] = Field(default=None, max_length=100)
    username: Optional[str] = Field(
        default=None, min_length=1, max_length=50, pattern=r"^[A-Za-zА-Яа-яЁё0-9_]+$"
    )

    model_config = ConfigDict(extra="forbid")
