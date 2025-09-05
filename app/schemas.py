from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str

class ProjectCreate(BaseModel):
    name: str
    description: str
    owner_id: int

class ProjectUpdate(BaseModel):
    name: str
    description: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int

class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    content_type: str
    project_id: int
    uploaded_by: int
    uploaded_at: datetime

class DocumentMetadata(BaseModel):
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime