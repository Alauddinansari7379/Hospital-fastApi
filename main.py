from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import hashlib

from database import SessionLocal, engine, Base
from models import User, Message
from schemas import (
    SignupRequest,
    LoginRequest,
    MessageCreate,
    MessageResponse
)


# ✅ CREATE APP ONLY ONCE
app = FastAPI(title="Hospital API")

# ✅ CREATE TABLES ON STARTUP
Base.metadata.create_all(bind=engine)

# ✅ DATABASE DEPENDENCY (ONLY ONCE)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ PASSWORD HASH
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# 🔹 AUTH APIs
# ======================

@app.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == request.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=request.name,
        email=request.email,
        dob=request.dob,
        mobile=request.mobile,
        address=request.address,
        password=hash_password(request.password)
    )

    db.add(new_user)
    db.commit()

    return {"success": True, "message": "User registered successfully"}

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == request.email,
        User.password == hash_password(request.password)
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "mobile": user.mobile
        }
    }

# ======================
# 🔹 MESSAGE APIs
# ======================

@app.post("/messages", response_model=MessageResponse)
def create_message(request: MessageCreate, db: Session = Depends(get_db)):
    msg = Message(
        from_number=request.from_number,
        body=request.body
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@app.get("/messages", response_model=List[MessageResponse])
def get_messages(db: Session = Depends(get_db)):
    return db.query(Message).order_by(Message.date.desc()).all()

@app.put("/messages/{message_id}/read")
def mark_as_read(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()

    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    msg.is_read = True
    db.commit()
    return {"success": True}
