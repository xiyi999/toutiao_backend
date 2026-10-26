#整合 根据token查询用户，返回用户
from fastapi import Header, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import users

async def get_current_user(
        authorization : str = Header(...,alias="Authorization"),
        db : AsyncSession = Depends(get_db)
):
    # Accept the standard Bearer scheme and the raw token used by the frontend.
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
    elif len(parts) == 1:
        token = parts[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或者令牌已失效",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
