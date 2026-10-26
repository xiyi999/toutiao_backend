from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News


async def get_category(db : AsyncSession, skip: int = 0, limit: int = 100):
    stmt = (
        select(Category)
        .order_by(Category.sort_order, Category.id)
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_news_list(db : AsyncSession,category_id : int, skip: int = 0, limit: int = 100):
    stmt = (
        select(News)
        .where(News.category_id == category_id)
        .order_by(News.publish_time.desc(), News.id.desc())
        .offset(skip)
        .limit(limit)
    )
    res = await db.execute(stmt)
    return res.scalars().all()


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
