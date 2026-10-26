import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from starlette import status

from models.users import DEFAULT_USER_AVATAR, DEFAULT_USER_BIO, User, UserToken
from schemas.users import UserRequest, UserUpdateRequest
from utils import security


async def get_user_by_username(db : AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db : AsyncSession, user_data : UserRequest):
    hashed_password = security.get_pwd_context(user_data.password)
    user = User(
        username=user_data.username,
        password=hashed_password,
        avatar=DEFAULT_USER_AVATAR,
        bio=DEFAULT_USER_BIO,
    )
    db.add(user)
    # Flush assigns the auto-increment ID and sends the insert. The dependency
    # owns the transaction and commits after the request succeeds.
    await db.flush()
    await db.refresh(user)
    return user


async def create_token(db : AsyncSession, user_id : int):
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=7)
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    res = await db.execute(stmt)
    user_token = res.scalar_one_or_none()

    if user_token :
        user_token.token = token
        user_token.expires_at = expires_at
    else :
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)

    db.add(user_token)
    await db.flush()

    return token


async def authenticate_user(db : AsyncSession, username: str, password: str):

    user = await get_user_by_username(db, username)

    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None

    return user


async def get_user_by_token(db : AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    res = result.scalar_one_or_none()

    if not res or res.expires_at < datetime.now():
        return None

    ret = select(User).where(User.id == res.user_id)

    result = await db.execute(ret)

    return result.scalar_one_or_none()


#更新用户信息
async def update_user(db : AsyncSession,username : str, user_data : UserUpdateRequest):
    stmt = update(User).where(User.username==username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ))
    result = await db.execute(stmt)
    await db.flush()

    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    updated_user =await get_user_by_username(db, username)
    return updated_user


#修改密码
async def change_password(db : AsyncSession, user : User, old_password : str, new_password : str):
    if not security.verify_password(old_password, user.password):
        return False

    user.password = security.get_pwd_context(new_password)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return True
