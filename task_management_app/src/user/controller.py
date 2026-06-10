from fastapi import HTTPException, status, Request
from src.user.dtos import UserSchema, LoginSchema
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

async def register(body:UserSchema,db:Session):
    is_user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
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
    res=await send_email([new_user.email])
    print(res)
    return new_user

def login(body:LoginSchema, db:Session):
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You enter wrong username!!")
    if not verify_password(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You enter wrong password!!")
    exp_time = datetime.now() + timedelta(minutes=settings.EXP_TIME)
    # exp_time = datetime.now() + timedelta(seconds=30)
    token = jwt.encode({"_id":user.id, "exp":exp_time.timestamp()}, settings.SECRET_KEY, settings.ALGORITHM)
    return {"token":token}

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
