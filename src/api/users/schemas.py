from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserUpdateSchema(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    model_config = ConfigDict(extra='forbid')