import asyncio
import warnings

import asyncpg

from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def main():


    print(row)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
