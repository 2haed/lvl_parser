import asyncio
import time

import aioschedule
from app.parser.data.headers import HEADERS
from async_schedule_parser import main as schedule_main
from async_team_stat_parser import main as team_stat_main
from async_team_members_parser import main as team_members_main


async def start_parsing():
    await team_stat_main()
    await schedule_main()
    await team_members_main()


if __name__ == '__main__':
    aioschedule.every(1).hours.do(start_parsing)
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(aioschedule.run_pending())
        time.sleep(0.1)
