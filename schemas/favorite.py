from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    is_favorite : bool = Field(..., alias="isFavorite")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", gt=0)

    model_config = ConfigDict(populate_by_name=True)

class FavoriteListRequest(BaseModel):
    page: int = Field(1, alias="page")
    page_size: int = Field(10, alias="pageSize", le=100)


class FavoriteNewsItemBase(NewsItemBase):
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time : datetime = Field(..., alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemBase]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
