from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    code: int
    msg: str
    data: list[CategoryResponse]


class NewsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    content: str
    image: str | None
    author: str | None
    category_id: int
    views: int
    publish_time: datetime
    created_at: datetime
    updated_at: datetime


class NewsListData(BaseModel):
    list: list[NewsResponse]
    total: int
    has_more: bool


class NewsListResponse(BaseModel):
    code: int
    msg: str
    data: NewsListData
