from lib2to3.pgen2 import token
from turtle import title
from typing import Optional
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime

# define the data model with name and data type

class CreateUser(BaseModel):
    
    email: EmailStr
    password: str
    
class UserInfo(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    id: Optional[str] = None

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserInfo

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    # this is the vote direction where the value less than 1 
    dir: conint(le=1) 