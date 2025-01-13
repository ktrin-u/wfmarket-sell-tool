"""
Basic program that generates bottom N order prices of the specified items
"""
import asyncio
import logging
from wfmarkettool import WFMarketTool


logging.basicConfig(filename="app.log", level=logging.WARNING, format="%(asctime)s %(levelname)s %(funcName)s: %(message)s")


async def main() -> None:
    # items = ["overextended", "narrow_minded", "catalyzing_shields", "blind_rage"]
    tool = WFMarketTool()

    # for item in items:
    #     query = asyncio.create_task(tool.get_floor_prices(item))
    await asyncio.gather(
        tool.get_floor_prices("overextended"),
        tool.get_floor_prices("narrow_minded"),
        tool.get_floor_prices("catalyzing_shields"),
        tool.get_floor_prices("blind_rage"),
        tool.get_floor_prices("galvanized_chamber"),
        tool.get_floor_prices("galvanized_aptitude"),
        tool.get_floor_prices("galvanized_scope"),
        tool.get_floor_prices("galvanized_hell"),
        tool.get_floor_prices("galvanized_savvy"),
        tool.get_floor_prices("galvanized_acceleration"),
        tool.get_floor_prices("galvanized_diffusion"),
        tool.get_floor_prices("galvanized_shot"),
        tool.get_floor_prices("galvanized_crosshairs")
    )

    await tool.close()

if __name__ == "__main__":
    main_task = asyncio.run(main())
