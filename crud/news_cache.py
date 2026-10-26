from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import get_cached_categories, set_cache_categories, get_cached_news_list, set_cached_news_list
from models.news import Category, News


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    # 1. 先查缓存（缓存全量分类，再按请求分页）
    cached = await get_cached_categories()
    if cached is None:
        # 缓存未命中时查询并缓存完整分类列表，避免只缓存首个请求的分页。
        stmt = select(Category).order_by(Category.sort_order, Category.id)
        result = await db.execute(stmt)
        categories = result.scalars().all()
        cached = jsonable_encoder(categories)
        await set_cache_categories(cached)

    return cached[skip: skip + limit]


async def get_news_list(db : AsyncSession,category_id : int, skip: int = 0, limit: int = 100):
    page = skip // limit + 1
    cached_list = await get_cached_news_list(category_id, page, limit)
    if cached_list is not None:
        return [News(**item) for item in cached_list]

    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc(), News.id.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    news_list = res.scalars().all()

    # 缓存完整字段，确保缓存命中时仍满足 NewsResponse 的响应模型。
    news_data = jsonable_encoder(news_list)
    await set_cached_news_list(category_id, page, limit, news_data)

    return news_list

async def get_news_count(db : AsyncSession, category_id : int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    res = await db.execute(stmt)
    return res.scalar_one()


async def get_news_detail(db : AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def increase_news_views(db : AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount>0


async def relate_news(db : AsyncSession, news_id: int, category_id: int, limit: int = 5):
    stmt = select(News).where(News.id != news_id,News.category_id == category_id).order_by(News.views.desc(),News.publish_time.desc()).limit(limit)
    res = await db.execute(stmt)
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publish_time": news_detail.publish_time,
        "category_id": news_detail.category_id,
        "views": news_detail.views,
    } for news_detail in res.scalars().all()]
