from fastapi import HTTPException


from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud import news
from schemas.news import CategoryListResponse, NewsListResponse
from crud import news_cache


router = APIRouter(prefix="/api/news",tags=["news"])

@router.get("/categories", response_model=CategoryListResponse)
async def categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    category = await news_cache.get_categories(db, skip, limit)
    return {
        "code": 200,
        "msg": "获取新闻分类成功",
        "data": category
    }


@router.get("/list", response_model=NewsListResponse)
async def list(
        category_id: int = Query(..., alias="CategoryID", ge=1),
        page: int = Query(1, alias="Page", ge=1),
        page_size: int = Query(10, alias="PageSize", ge=1, le=100),
        db : AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    news_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    news_total = await news.get_news_count(db, category_id)
    has_more = offset + len(news_list) < news_total
    return {
        "code": 200,
        "msg": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": news_total,
            "has_more": has_more,
        }
    }


@router.get("/detail")
async def details(news_id: int = Query(...,alias="id"), db: AsyncSession = Depends(get_db)):

    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    relate_List = await news.relate_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "msg":"获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publish_time":news_detail.publish_time,
            "category_id":news_detail.category_id,
            "views":news_detail.views,
            "relatedNews":relate_List
        }
    }