from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models import favorite
from models.favorite import Favorite
from models.news import News
from models.users import User


async def is_news_favorite(
        db : AsyncSession,
        user_id : int,
        news_id: int,
):
    query = select(Favorite.id).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def favorite_add(
        db : AsyncSession,
        user_id : int,
        news_id : int
):
    query = select(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(query)
    existing_favorite = result.scalar_one_or_none()
    if existing_favorite is not None:
        return existing_favorite

    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.flush()
    return favorite


#取消收藏
async def favorite_delete(
        db : AsyncSession,
        user_id : int,
        news_id : int
):
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount>0


#获得收藏列表
async def get_favorite_list(
        db : AsyncSession,
        user_id : int,
        page : int = 1,
        page_size: int = 10,
):
     #总量+收藏的新闻列表
     count_query= select(func.count()).where(Favorite.user_id == user_id)
     count_res = await db.execute(count_query)
     total =await count_res.scalar_one()

     #获取收藏列表+连表查询+收藏时间排序+分页
     query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
      .join(Favorite, Favorite.news_id == News.id)
      .where(Favorite.user_id == user_id)
      .order_by(Favorite.created_at.desc())
      .offset((page-1)*page_size)
      .limit(page_size))

     res = await db.commit(query)
     rows = res.all()
     return rows,total


#清除收藏列表
async def remove_all_favorite(
        db : AsyncSession,
        user_id : int
):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    res = await db.execute(query)
    await db.commit()
    return res.rowcount or 0




