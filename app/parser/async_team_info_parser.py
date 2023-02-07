import asyncio
import warnings
import aiohttp
import asyncpg
from bs4 import BeautifulSoup
from app.config import settings
from app.parser.data.headers import HEADERS

warnings.filterwarnings("ignore", category=DeprecationWarning)


async def get_page_data(session: aiohttp.ClientSession, URL: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(URL, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        f_table = soup.find_all('table')
        s_table = f_table.find('table')
        table_rows = table.find_all('tr')
        print(table_rows)
        trs = table_rows.find_all('td')
        team = {
            'team': table_rows[0].text,
            'link': table_rows[1].text,
            'summary': table_rows[2].text,
            'contact_person': table_rows[4].text,
            'nickname': table_rows[5].text,
            'metro_station': table_rows[8].text,
            # 'time': f'{table_rows[9].text}-{table_rows[10].text}',
        }
        print(table_rows)
        async with connection_pool.acquire() as connection:
            await connection.fetch(
                'insert into public.team_info(team, link, summary, contact_person, nickname, metro_station) '
                'values ($1, $2, $3, $4, $5, $6) on conflict (team) do update set team = excluded.team',
                team['team'], team['link'], team['summary'], team['contact_person'], team['nickname'],
                team['metro_station']
            )


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table IF NOT EXISTS team_info (team text primary key, link text, summary text, contact_person text, '
            'nickname text, metro_station text,'
            'foreign key (team) references team_stat (team));'
        )
        row = await connection.fetch('select team_link from team_stat')
    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in row:
            print(link[0])
            tasks.append(
                get_page_data(session, f'{link[0]}', connection_pool, HEADERS))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())