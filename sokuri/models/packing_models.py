from pydantic import BaseModel
from typing import List, Tuple

class ReqItem(BaseModel):
    itemName: str
    itemIndex: int
    itemScaleX: float
    itemScaleY: float
    itemScaleZ: float
    itemW: float
    itemH: float
    itemD: float
    loadBear: int

class PackingRequest(BaseModel):
    bag: List[int]
    items: List[ReqItem]

class Req(BaseModel):
    items: List[ReqItem]

class ResItem(BaseModel):
    itemName: str
    itemIndex: int
    itemScale: List[float]
    position: List[float]
    rotationType: int


class result(BaseModel):
    boxSize: Tuple[str, Tuple[int, int, int]]
    itemList: List[ResItem]


class Res(BaseModel):
    result: List[result]
