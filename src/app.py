"""
Basic program that generates bottom N order prices of the specified items
"""
from pprint import pprint
import json
import requests

ENDPOINT = "https://api.warframe.market/v1"  # warframe.market api endpoint
TIMEOUT = 3  # https request timeout


def get_item_prices(item_name: str) -> list[object]:
    """Get the order details of item_name as a json"""
    with requests.get(
        url=f"{ENDPOINT}/items/{item_name.lower()}/orders",
        timeout=TIMEOUT
    ) as result:
        match result.status_code:
            case 200:
                payload = json.loads(result.text).get("payload")
                orders = payload.get("orders")
                return orders

            case _:
                raise ValueError(f"expected http status 200, got http status {result.status_code}")


if __name__ == "__main__":
    resulting_orders = get_item_prices("malignant_force")
    pprint(f"return type: {type(resulting_orders)}")
    pprint(f"order count: {len(resulting_orders)}")
