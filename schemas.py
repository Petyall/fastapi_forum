from pydantic import BaseModel
from typing import List
from datetime import datetime

class PostBase(BaseModel):
    title: str
    description: str | None = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    owner_id: int
    date_created: datetime
    date_last_updated: datetime

    class Config:
        orm_mode = True



class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserCreate(UserBase):
    hashed_password: str
    
    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    items: list[Post] = []

    class Config:
        orm_mode = True



class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    owner_id: int
    post_id: int
    date_created: datetime
    date_last_updated: datetime

    class Config:
        orm_mode = True


class PostWithComments(BaseModel):
    post: Post 
    comments: List[Comment]

    class Config:
        orm_mode = True