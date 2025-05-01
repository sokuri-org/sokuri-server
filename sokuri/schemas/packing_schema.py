from pydantic import BaseModel


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
    bag: list[int]
    items: list[ReqItem]

class Req(BaseModel):
    items: list[ReqItem]

class ResItem(BaseModel):
    itemName: str
    itemIndex: int
    itemScale: list[float]
    position: list[float]
    rotationType: int


class result(BaseModel):
    boxSize: tuple[str, tuple[int, int, int]]
    itemList: list[ResItem]


class Res(BaseModel):
    result: list[result]
