"""
Collection of FastAPI models
"""

from pydantic import BaseModel


class FloorPriceResult(BaseModel):
    item_name: str
    prices: list[int]
