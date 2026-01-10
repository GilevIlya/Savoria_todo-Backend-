from pydantic import BaseModel, Field, EmailStr

class RegisterSchema(BaseModel):
    firstname: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-zА-Яа-яЁё]+$')
    lastname: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-zА-Яа-яЁё]+$')
    username: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-zА-Яа-яЁё0-9_]+$')
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-z0-9]+$')

class LoginSchema(BaseModel):
    agree: bool
    username: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-zА-Яа-яЁё0-9_]+$')
    password: str = Field(min_length=1, max_length=50, pattern=r'^[A-Za-z0-9]+$')