"""
FastAPI program to allow modular front-end
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_models import FloorPriceResult
from wfmarkettool import WFMarketTool

logging.basicConfig(filename="fastapi_main.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(funcName)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global wftool
    wftool = WFMarketTool(logger)
    await wftool.initialize()
    yield
    # Shutdown
    if wftool:
        await wftool.close()  # clean up


app = FastAPI(lifespan=lifespan)
wftool: WFMarketTool | None = None


@app.get("/wfmarkettool/item_floor_prices/{item_name}")
async def get_floor_prices(item_name: str = "", order_count: int = 5) -> FloorPriceResult:
    """
    Get the floor prices of multiple items in warframe.market
    """
    ret = []
    if wftool:
        ret = await wftool.get_floor_prices(item_name, order_count)
    else:
        raise Exception("WFtool not initialized")
    return ret
