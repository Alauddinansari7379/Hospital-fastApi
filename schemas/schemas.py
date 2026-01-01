from pydantic import BaseModel, EmailStr
from datetime import date

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    dob: date
    mobile: str
    address: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str



class MessageCreate(BaseModel):
    from_number: str
    body: str

class MessageResponse(BaseModel):
    id: int
    from_number: str
    body: str
    is_read: bool
    date: str

    class Config:
        from_attributes = True
