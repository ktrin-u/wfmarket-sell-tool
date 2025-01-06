"""
Basic program that generates bottom N order prices of the specified items
"""
from pprint import pprint
from typing import TypeVar
from enum import auto, StrEnum
import json
import requests
import warnings
import time


T = TypeVar("T")
K = TypeVar("K")
warnings.simplefilter("always", RuntimeWarning)  # always show RuntimeWarnings

ENDPOINT = "https://api.warframe.market/v1"  # warframe.market api endpoint
TIMEOUT = 3  # https request timeout


class Status(StrEnum):
    INGAME = auto()  # type: ignore
    ONLINE = auto()  # type: ignore
    OFFLINE = auto()  # type: ignore


def get_item_prices(item_name: str) -> list[dict[str, object]]:
    """Get the order details of item_name as a json"""
    with requests.get(
        url=f"{ENDPOINT}/items/{item_name.lower()}/orders",
        timeout=TIMEOUT
    ) as result:
        match result.status_code:
            case 200:
                payload = json.loads(result.text).get("payload")
                if type(payload) is dict:
                    orders = payload.get("orders")  # type: ignore
                    if orders is None:
                        raise Exception("no orders found")
                    return orders  # type: ignore

                raise Exception("unexpected payload received from json loads")

            case _:
                raise ValueError(f"expected http status 200, got http status {result.status_code}")


def filter_sell_orders(orders: list[dict[str, T]]) -> list[dict[str, T]]:
    """
    Removes all non-sell orders in the order list
    """
    if type(orders) is not list:
        raise TypeError("argument is expected to be of type list")

    def filter_func(order: dict[str, T]) -> bool:
        order_type = order.get("order_type")
        if order_type is not None:
            match order_type:
                case "sell":
                    return remove_non_in_game(order)
                case "buy":
                    return False
                case _:
                    warnings.warn(f"unsupported order type \"{order_type}\" found")
                    return False
        warnings.warn(f"order with id {order["id"]} is invalid", RuntimeWarning, )
        return False

    def remove_non_in_game(order: dict[str, T]) -> bool:
        user = order.get("user")
        if user is not None:
            status = user.get("status")  # type: ignore
            if status is not None:
                match status:
                    case Status.INGAME.value:
                        return True
                    case Status.ONLINE.value:
                        return False
                    case Status.OFFLINE.value:
                        return False
                    case _:  # type: ignore
                        warnings.warn(f"unsupported status type found in order id {order["id"]}")
                        return False
        raise Exception(f"order {order["id"]} has no user key")

    return list(filter(filter_func, orders))


def get_plat_prices(sell_orders: list[dict[str, T]], sort_descending: bool = False) -> list[int]:
    """
    Gets all the platinum prices from the a list of sell orders
    """
    if type(sell_orders) is not list:
        raise TypeError("argument is expected to be of type list")

    prices: list[int] = []
    for order in sell_orders:
        plat = order.get("platinum")
        if type(plat) is int:
            prices.append(plat)
            continue
        warnings.warn(f"order {order["id"]} has no platinum key", RuntimeWarning)

    if sort_descending:
        prices.sort(reverse=True)
        return prices

    prices.sort()
    return prices


def get_floor_prices(item_name: str, order_count: int = 5) -> str:
    resulting_orders = get_item_prices(item_name)
    sell_orders = filter_sell_orders(resulting_orders)
    plat_prices = get_plat_prices(sell_orders)
    return f"{item_name} bottom {order_count} floor prices are: {plat_prices[:order_count]}"


if __name__ == "__main__":
    for item in ["overextended", "narrow_minded", "catalyzing_shields", "blind_rage"]:
        pprint(get_floor_prices(item))
        time.sleep(1)
