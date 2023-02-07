import psycopg2 as psycopg2
import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.parser.data.headers import HEADERS

connection = psycopg2.connect(
    host=settings.database.host,
    database=settings.database.database,
    user=settings.database.user,
    password=settings.database.password
)

URL = 'http://www.volleymsk.ru/ap/members.php?id=7548'
page = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(page.content, 'html.parser')
table = soup.find('table')
table_rows = table.find_all('td')
for i in table_rows:
    print(i.text.strip())
    if 'ДЛВЛ 2022-2023' in i.text:
        break
