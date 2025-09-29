from typing import Optional
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    quantity: int

# Pydantic schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    is_superuser: Optional[bool] = False

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True