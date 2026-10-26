from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user
from starlette import status

from config.db_conf import get_db
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user",tags=["users"])

# Keep the plural API paths and accept the singular paths used by the frontend.

@router.post("/register", include_in_schema=False)
async def register(user_date : UserRequest, db : AsyncSession = Depends(get_db)):
    exiting_username =await users.get_user_by_username(db, user_date.username)
    if exiting_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="该用户已存在")

    user = await users.create_user(db, user_date)

    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data)



@router.post("/login", include_in_schema=False)
async def login(user_date : UserRequest, db : AsyncSession = Depends(get_db)):
    user =await users.authenticate_user(db, user_date.username, user_date.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="账号或密码错误")

    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))

    return success_response(message="登录成功", data=response_data)



@router.get("/info", include_in_schema=False)
async def get_user_info(user : User = Depends(get_current_user)):

    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))


@router.put("/update", include_in_schema=False)
async def update_user_info(user_date : UserUpdateRequest,
                           user : User = Depends(get_current_user),
                           db : AsyncSession = Depends(get_db)):

    user = await users.update_user(db, user.username, user_date)


    return success_response(message="更新数据成功",data=UserInfoResponse.model_validate(user))



@router.put("/password", include_in_schema=False)
async def update_password(password_date : UserChangePasswordRequest,
                          user : User = Depends(get_current_user),
                          db : AsyncSession = Depends(get_db)):

    res_change_pwd = await users.change_password(db, user, password_date.old_password, password_date.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="旧密码错误")

    return success_response(message="修改密码成功")
