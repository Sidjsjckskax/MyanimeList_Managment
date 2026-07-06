from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AnimeClean(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mal_id: int = Field(gt=0)
    title: str = Field(min_length=1)
    title_english: Optional[str] = None
    title_japanese: Optional[str] = None
    type_: Optional[str] = None
    source_: Optional[str] = None
    episodes: Optional[int] = Field(default=None, ge=0)
    status_: Optional[str] = None
    airing: Optional[bool] = None
    aired_from: Optional[date] = None
    aired_to: Optional[date] = None
    duration: Optional[str] = None
    rating: Optional[str] = None
    score: Optional[float] = Field(default=None, ge=0, le=10)
    scored_by: Optional[int] = Field(default=None, ge=0)
    rank_: Optional[int] = Field(default=None, ge=0)
    popularity: Optional[int] = Field(default=None, ge=0)
    members: Optional[int] = Field(default=None, ge=0)
    favorites: Optional[int] = Field(default=None, ge=0)
    synopsis: Optional[str] = None
    year_: Optional[int] = Field(default=None, ge=1900, le=2100)
    season: Optional[str] = None
    studios: Optional[str] = None
    genres: Optional[str] = None
    themes: Optional[str] = None
    demographics: Optional[str] = None