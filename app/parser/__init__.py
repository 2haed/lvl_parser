import asyncio

import aioschedule as schedule
from async_schedule_parser import main as schedule_main
from async_team_stat_parser import main as team_stat_main
from async_team_info_parser import main as team_info_main
from async_team_members_parser import main as team_members_main


async def start_parsing(interval: int = 3600):
    await team_stat_main()
    await schedule_main()
    await team_info_main()
    await team_members_main()
    await asyncio.sleep(interval)

# schedule.every().day.at("09:00").do(start_parsing)