import psycopg2 as psycopg2
import requests
import pandas as pd
from bs4 import BeautifulSoup

from config import settings
from app.data.contsants import HEADERS

connection = psycopg2.connect(
    host=settings.database.host,
    database=settings.database.database,
    user=settings.database.user,
    password=settings.database.password
)

URL = 'http://www.volleymsk.ru/ap/rasp.php?id=1379'
page = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table', id='rasp')
insert_query = 'insert into schedule (date_time, host, guest, location) values'
with connection.cursor() as cursor:
    counter = 0
    cursor.execute(
        'create table IF NOT EXISTS schedule (date_time timestamp, host text, '
        'guest text, location text);')
    for tr in table.find_all('tr')[1:]:
        counter += 1
        row = tr.find_all('td')
        date_time = '-'.join(row[0].text.split()[1].replace(',', '').split('-')[::-1])
        match = {
            'date_time': f'{"-".join(row[0].text.split()[1].replace(",", "").split("-")[::-1])} {row[0].text.split()[2]}',
            'host': row[1].text,
            'guest': row[2].text,
            'location': row[3].text,
        }
        print(match)
        insert_query += f" ('{match['date_time']}', '{match['host']}', '{match['guest']}', '{match['location']}'),"
    insert_query = insert_query[:-1]
    print(counter)
    # insert_query += ' on conflict (date_time) do nothing;'
    cursor.execute(insert_query)
    connection.commit()
