from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.user.dtos import UserSchema, UserResponseSchema, LoginSchema, RefreshSchema
from src.utils.db import get_db
from src.user import controller
from src.user.models import UserModel
from src.utils.helpers import is_authenticated

user_routes = APIRouter(prefix="/user")

@user_routes.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(body:UserSchema, db:Session=Depends(get_db)):
    return await controller.register(body, db)

@user_routes.post("/login", status_code=status.HTTP_200_OK)
def login(body:LoginSchema, db:Session=Depends(get_db)):
    return controller.login(body, db)

@user_routes.post("/refresh", status_code=status.HTTP_200_OK)
def refresh(body:RefreshSchema, db:Session=Depends(get_db)):
    return controller.refresh_token(body, db)

@user_routes.get("/is_auth", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
def is_auth(user:UserModel=Depends(is_authenticated)):
    return user