import asyncio
import copy
import time

import aiohttp
import asyncpg
import psycopg2 as psycopg2
import requests
from bs4 import BeautifulSoup
from config import settings
import psycopg2.extras
from app.data.contsants import HEADERS


# for page_num in range(1379, 1401):
async def get_page_data(session: aiohttp.ClientSession, URL: str, connection_pool: asyncpg.Pool, headers: dict):
    async with session.get(URL, headers=headers) as response:
        # page = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(await response.text(), 'html.parser')
        row = soup.find_all('td', class_='normaltext')
        all_teams = []
        if 250 < len(row) < 400:
            for i in range(14, 150, 14):
                if row[i + 1].text != 'Команда':
                    team = {
                        'team': row[i + 1].text,
                        'team_link': f"http://www.volleymsk.ru{row[i + 1].find('a').get('href')}" if row[i + 1].find(
                            'a') is not None else None,
                        'victories': row[i + 2].text,
                        'max_victories': row[i + 3].text,
                        'points': row[i + 4].text,
                        'handicap': row[i + 5].text,
                        'three_zero_three_one': row[i + 6].text,
                        'three_two': row[i + 7].text,
                        'two_three': row[i + 8].text,
                        'one_three_zero_three': row[i + 9].text,
                        'match_points': row[i + 10].text,
                        'match_ratio': row[i + 11].text,
                        'balls': row[i + 12].text,
                        'balls_ratio': row[i + 13].text,
                    }
                    all_teams.append(team)
            async with connection_pool.acquire() as connection:
                await connection.fetch(
                    'insert into lvl.teams(team, team_link, victories, max_victories, points, handicap, '
                    'three_zero_three_one, three_two, one_three_zero_three, match_points, match_ratio, balls, '
                    'balls_ratio) values ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) on conflict (team) '
                    'do update set team = excluded.team', team['team'], team['team_link'], team['victories'],
                    team['max_victories'], team['points'], team['handicap'], team['three_zero_three_one'],
                    team['three_two'], team['one_three_zero_three'], team['match_points'], team['match_ratio'],
                    team['balls'], team['balls_ratio']
                )
        # psycopg2.extras.execute_batch(cursor, """
        # INSERT INTO lvl.teams values (
        #  %(team)s,
        #  %(team_link)s,
        #  %(victories)s,
        #  %(max_victories)s,
        #  %(points)s,
        #  %(handicap)s,
        #  %(three_zero_three_one)s,
        #  %(three_two)s,
        #  %(one_three_zero_three)s,
        #  %(match_points)s,
        #  %(match_ratio)s,
        #  %(balls)s,
        #  %(balls_ratio)s) on conflict (team) do update set team = excluded.team;
        #     """, all_teams)
        # connection.commit()


async def main():
    connection_pool = await asyncpg.create_pool(
        host=settings.database.host,
        database=settings.database.database,
        user=settings.database.user,
        password=settings.database.password
    )
    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table IF NOT EXISTS lvl.teams (team text primary key, team_link text unique , victories int, '
            'max_victories int, points int, handicap text, three_zero_three_one int, three_two int, '
            'one_three_zero_three '
            'int, match_points text, '
            'match_ratio text, balls text, balls_ratio text);')
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_num in range(1379, 1401):
            URL = f'http://www.volleymsk.ru/liga/teams/?page={page_num}'
            # new_headers = copy.deepcopy(HEADERS)
            # new_headers['user-agent'] = MOBILE_USER_AGENT[page_num]
            tasks.append(asyncio.create_task(await get_page_data(session, URL, connection_pool, HEADERS)))
        await asyncio.gather(*tasks)
    # asyncio.run(score_parser())


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(time.time() - start)
