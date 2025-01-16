"""
Collection of Types and Protocols to ensure static typing
"""
from typing import TypedDict, Required, TypeVar
from enum import StrEnum, auto

T = TypeVar("T")
Platinum = int  # type alias for clarity


class Status(StrEnum):
    """
    An enum that contains all the possible values for the Warframe Market status
    """
    INGAME = auto()
    ONLINE = auto()
    OFFLINE = auto()


class OrderType(StrEnum):
    """
    An enum that contains all possible values for the Warframe Market order type
    """
    BUY = auto()
    SELL = auto()


class User(TypedDict):
    """
    A class that defines the contents of the User object for the Warframe Market response
    """
    reputation: int
    locale: str
    avatar: str
    ingame_name: str
    last_seen: str
    id: str
    region: str
    status: Status


class Order(TypedDict, total=False):
    """
    A class that defines the contents of the Order object for the Warframe Market response
    """
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
    """
    A class that defines the contents of the payload object for the Warframe Market response
    """
    orders: list[Order]


class WFMarketResponse(TypedDict, total=False):
    """
    A class that defines the contents of the Warframe Market response
    """
    payload: Payload
