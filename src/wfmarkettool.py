"""
The class that contains all the functions for the main feature
"""
import asyncio
import aiohttp
import logging
from required_types import Order, Status, WFMarketResponse, Platinum


class WFMarketTool:
    """
    Class for the WF Market sell tool
    """
    def __init__(self):
        self.ENDPOINT = "https://api.warframe.market/v1"  # warframe.market api endpoint
        self.REQUEST_LIMIT: int = 3  # wfmarket ToS states a max of 3 requests per second
        self.request_counter: int = 0  # keeps track of number of requests made during the current second
        self._session = aiohttp.ClientSession()
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger(__name__)
        self._request_timer = asyncio.create_task(self._request_timer_update())

    async def _request_timer_update(self) -> None:
        while True:
            async with self._lock:
                self.request_counter = 0
                self._logger.info('request counter refreshed')
            await asyncio.sleep(1)

    async def check_request_time_valid(self) -> bool:
        async with self._lock:  # need to lock this part to ensure that request_counter is consistent
            if self.request_counter >= self.REQUEST_LIMIT:
                return False

            self.request_counter += 1
            self._logger.info("new request made")
            return True

    async def get_item_orders(self, item_name: str) -> WFMarketResponse:
        self._logger.info(f"attempting to acquire {item_name}")
        if not (await self.check_request_time_valid()):
            self._logger.info("request_limit reached, trying again in 1s")
            await asyncio.sleep(1)
            return await self.get_item_orders(item_name)

        async with self._session.get(
            url=f"{self.ENDPOINT}/items/{item_name.lower()}/orders",
        ) as result:
            match result.status:
                case 200:
                    self._logger.info(f"successfully acquired {item_name}")
                    return await result.json()
                case _:
                    self._logger.info(f"expected http status 200, got http code {result.status}")
                    self._logger.info(f"failed to acquire {item_name}")
                    return {}

    async def get_item_prices(self, item_name: str) -> list[Order]:
        """Get the order details of item_name as a json"""
        result = await self.get_item_orders(item_name)
        payload = result.get("payload")
        if payload is not None:
            orders: list[Order] = payload.get("orders")
            return orders

        logging.warning("unable to get orders from payload None")
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
                        logging.warning(f"unsupported order type \"{order_type}\" found")
                        return False
            logging.warning(f"order with id {order["id"]} is invalid", RuntimeWarning, )
            return False

        def remove_non_in_game(order: Order) -> bool:
            user = order.get("user")
            if user is not None:
                status = user.get("status")
                if status is not None:
                    match status:
                        case Status.INGAME.value:
                            return True
                        case Status.ONLINE.value:
                            return False
                        case Status.OFFLINE.value:
                            return False
                        case _:
                            logging.warning(f"unsupported status type found in order id {order["id"]}")
                            return False
            raise Exception(f"order {order["id"]} has no user key")

        return list(filter(filter_func, orders))

    async def get_plat_prices(self, sell_orders: list[Order], sort_descending: bool = False) -> list[Platinum]:
        """
        Gets all the platinum prices from the a list of sell orders
        """
        if type(sell_orders) is not list:
            raise TypeError("argument is expected to be of type list")

        prices: list[Platinum] = []
        for order in sell_orders:
            plat = order.get("platinum")
            if type(plat) is Platinum:
                prices.append(plat)
                continue
            self._logger.warning(f"order {order["id"]} has no platinum key", RuntimeWarning)

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

    async def close(self) -> None:
        await self._session.close()
        self._request_timer.cancel()

