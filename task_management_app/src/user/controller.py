from fastapi import HTTPException, status, Request
from src.user.dtos import UserSchema, LoginSchema, RefreshSchema
from sqlalchemy.orm import Session
from src.user.models import UserModel
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime, timedelta
import jwt 
from jwt.exceptions import InvalidTokenError
from src.utils.mail import send_email

password_hash = PasswordHash.recommended()
def get_password_hash(password):
    return password_hash.hash(password)
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id):
    exp_time = datetime.now() + timedelta(minutes=settings.EXP_TIME)
    return jwt.encode({"_id":user_id, "type":"access", "exp":exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)

def create_refresh_token(user_id):
    exp_time = datetime.now() + timedelta(days=settings.REFRESH_EXP_TIME)
    return jwt.encode({"_id":user_id, "type":"refresh", "exp":exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)

async def register(body:UserSchema,db:Session):
    is_user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists!!")
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered!!")
    hash_password = get_password_hash(body.password)
    new_user = UserModel(
        name = body.name,
        username = body.username,
        hash_password = hash_password,
        email = body.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    try:
        res = await send_email([new_user.email])
        print(res)
    except Exception as e:
        # Registration must succeed even if the confirmation email fails to send.
        print(f"Failed to send registration email to {new_user.email}: {e}")
    return new_user

def login(body:LoginSchema, db:Session):
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You enter wrong username!!")
    if not verify_password(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You enter wrong password!!")
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return {"access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}

def refresh_token(body:RefreshSchema, db:Session):
    try:
        data = jwt.decode(body.refresh_token, settings.SECRET_KEY, settings.ALGORITHM)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token!!")
        user_id = data.get("_id")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized!!")
        access_token = create_access_token(user.id)
        return {"access_token":access_token, "token_type":"bearer"}
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token!!")

def is_authenticated(request:Request, db:Session):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized!!")
        token = token.split(" ")[-1]
        data = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        user_id = data.get("_id")
        # exp_time = int(data.get("exp"))
        # current_time = datetime.now().timestamp()
        # if current_time > exp_time:
            # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized!!")
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized!!")
        return user
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are unauthorized!!")
