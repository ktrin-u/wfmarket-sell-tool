"""
Collection of Types and Protocols to ensure static typing
"""
from typing import TypeVar, TypedDict, Required
from enum import StrEnum, auto


T = TypeVar("T")
K = TypeVar("K")
Platinum = int


class Status(StrEnum):
    INGAME = auto()
    ONLINE = auto()
    OFFLINE = auto()


class OrderType(StrEnum):
    BUY = auto()
    SELL = auto()


class User(TypedDict):
    reputation: int
    locale: str
    avatar: str
    ingame_name: str
    last_seen: str
    id: str
    region: str
    status: Status


class Order(TypedDict, total=False):
    creation_date: str
    visible: bool
    quantity: int
    user: User
    last_update: str
    platinum: int
    order_type: OrderType
    platform: str
    id: Required[str]
    mod_rank: str
    region: str


class Payload(TypedDict):
    orders: list[Order]


class WFMarketResponse(TypedDict, total=False):
    payload: Payload
