import asyncio
import warnings

import asyncpg

from config import settings

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def main():
    conn = await asyncpg.connect(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    row = await conn.fetch('select * from public.teams where team = $1', 'ОСНОВА')
    conn.close()
    print(row)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
