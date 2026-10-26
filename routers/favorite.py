
from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends
from sqlalchemy import null
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import favorite
from models.users import User
from schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest, FavoriteListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite",tags=["favorite"])


@router.get("/check")
async def check_favorite(db : AsyncSession = Depends(get_db),
                         user : User = Depends(get_current_user),
                         news_id : int = Query(..., alias= "newsId")
):
    is_favorited = await favorite.is_news_favorite(db, user.id , news_id)
    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(is_favorite=is_favorited))


@router.post("/add")
async def add_favorite(
        data: FavoriteAddRequest ,
        db : AsyncSession = Depends(get_db),
        user : User = Depends(get_current_user),
):
    result =await favorite.favorite_add(db, user.id, data.news_id)
    return success_response(message="添加收藏成功",data=result)


@router.delete("/remove")
async def remove_favorite(
        news_id: int = Query(..., alias= "newsId"),
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db),
):
    result = await favorite.favorite_delete(db, user.id, news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")

    return success_response(message="用户取消收藏成功",data=result)


@router.get("/list")
async def list_favorite(
        page: int = Query(ge=1, alias= "page"),
        page_size: int = Query(ge=10, alias= "page_size", le=100),
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db),
):

    rows, total = await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time" : favorite_time,
        "favorite_id" : favorite_id,
    }for news, favorite_time, favorite_id in rows
    ]

    has_more = total > page_size*page
    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)

    return success_response(message="用户列表获取成功",data=data)


@router.delete("/clear")
async def clear_favorite(
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db),
):
    num = favorite.remove_all_favorite(db, user.id)

    return success_response(message=f"清除了{num}条收藏")
