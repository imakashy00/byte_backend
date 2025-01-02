from fastapi import status
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, constr
from typing import List, Optional

# Status of task can only be pending, in-progress, completed 
class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


# Schema of user- email and password 
class UserRegister(BaseModel):
    email:EmailStr
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long"
    )


# User schema from database
class UserDatabase(BaseModel):
    id:int
    email:EmailStr
    hashed_password: str
    class Config:
        from_attributes = True

# Schema of Task Default status is pending
class Task(BaseModel):
    title:str
    description:str
    status:Optional[Status] = Status.PENDING
    class Config:
        from_attributes = True

class TasksDatabase(BaseModel):
    id:int
    title:str
    description:str
    status:Status
    class Config:
        from_attributes = True

# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email:str | None = None