"""
Basic program that generates bottom N order prices of the specified items
"""
import asyncio
import logging
from wfmarkettool import WFMarketTool


logging.basicConfig(filename="app.log", level=logging.WARNING, format="%(asctime)s %(levelname)s %(funcName)s: %(message)s")


async def main() -> None:
    items = [
        "overextended",
        "narrow_minded",
        "catalyzing_shields",
        "blind_rage",
        "galvanized_chamber",
        "galvanized_aptitude",
        "galvanized_chamber",
        "galvanized_aptitude",
        "galvanized_scope",
        "galvanized_hell",
        "galvanized_savvy",
        "galvanized_acceleration",
        "galvanized_diffusion"
        "galvanized_shot",
        "galvanized_crosshairs"
    ]
    tool = WFMarketTool()

    await tool.get_multiple_floor_prices(items)

    await tool.close()

if __name__ == "__main__":
    main_task = asyncio.run(main())
