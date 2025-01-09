"""
Basic program that generates bottom N order prices of the specified items
"""
import warnings
import asyncio
import aiohttp
import logging
from required_types import T, Order, Status, WFMarketResponse


ENDPOINT = "https://api.warframe.market/v1"  # warframe.market api endpoint
TIMEOUT: int = 3  # https request timeout
REQUEST_LIMIT: int = 3  # wfmarket ToS states a max of 3 requests per second
request_counter: int = 0  # keeps track of number of requests made during the current second

logging.basicConfig(filename="app.log", level=logging.INFO)
warnings.simplefilter("always", RuntimeWarning)  # always show RuntimeWarnings


class WFMarketTool:
    """
    Class for the WF Market sell tool
    """
    def __init__(self):
        self._session = aiohttp.ClientSession()
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger(__name__)

        self._request_timer = asyncio.create_task(self._request_timer_update())

    def __del__(self):
        self._request_timer.cancel()

    async def _request_timer_update(self) -> None:
        global request_counter
        while True:
            async with self._lock:
                request_counter = 0
                self._logger.info('request counter refreshed')
            await asyncio.sleep(1)

    async def check_request_time_valid(self) -> bool:
        global REQUEST_LIMIT, request_counter

        async with self._lock:  # need to lock this part to ensure that request_counter is consistent
            if request_counter >= REQUEST_LIMIT:
                return False

            request_counter += 1
            self._logger.info("new request made")
            return True

    async def get_item_orders(self, item_name: str) -> WFMarketResponse:
        self._logger.info(f"attempting to acquire {item_name}")
        if not (await self.check_request_time_valid()):
            self._logger.info("request_limit reached, trying again in 0.5s")
            await asyncio.sleep(0.5)
            return await self.get_item_orders(item_name)

        async with self._session.get(
            url=f"{ENDPOINT}/items/{item_name.lower()}/orders",
        ) as result:
            match result.status:
                case 200:
                    logging.info(f"successfully acquired {item_name}")
                    return await result.json()
                case _:
                    logging.info(f"expected http status 200, got http code {result.status}")
                    logging.info(f"failed to acquire {item_name}")
                    warnings.warn(f"unable to acquire {item_name}")
                    return {}

    async def get_item_prices(self, item_name: str) -> list[Order]:
        """Get the order details of item_name as a json"""
        result = await self.get_item_orders(item_name)
        payload = result.get("payload")
        if payload is not None:
            orders: list[Order] = payload.get("orders")
            return orders

        warnings.warn("unable to get orders from payload None")
        return list()

    async def filter_sell_orders(self, orders: list[Order]) -> list[Order]:
        """
        Removes all non-sell orders in the order list
        """
        if type(orders) is not list:
            raise TypeError("argument is expected to be of type list")

        def filter_func(order: Order) -> bool:
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

        def remove_non_in_game(order: Order) -> bool:
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

    async def get_plat_prices(self, sell_orders: list[Order], sort_descending: bool = False) -> list[int]:
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

    async def get_floor_prices(self, item_name: str, order_count: int = 5) -> str:
        resulting_orders = await self.get_item_prices(item_name)
        sell_orders = await self.filter_sell_orders(resulting_orders)
        plat_prices = await self.get_plat_prices(sell_orders)
        ret = f"{item_name} bottom {order_count} floor prices are: {plat_prices[:order_count]}"
        print(ret)
        return ret

    async def close(self):
        await self._session.close()


async def main():
    # items = ["overextended", "narrow_minded", "catalyzing_shields", "blind_rage"]
    tool = WFMarketTool()

    # for item in items:
    #     query = asyncio.create_task(tool.get_floor_prices(item))
    queries = asyncio.gather(
        tool.get_floor_prices("overextended"),
        tool.get_floor_prices("narrow_minded"),
        tool.get_floor_prices("catalyzing_shields"),
        tool.get_floor_prices("blind_rage"),
    )

    # await tool.close()

if __name__ == "__main__":
    main_task = asyncio.run(main())
