HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36',
    'Cookie': 'qrator_msid=1671003029.243.yazXMXT5pW9WgDQh-017db4795lsm9j57vegcbmcr3iod2oi7'
}
MOBILE_USER_AGENTS = [
    'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) '
    'Version/4.0 Mobile Safari/534.30',
    'Mozilla/5.0 (Linux; Android 11; Pixel 3a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile '
    'Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/59.0.3071.125 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 7.0; SM-A310F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/55.0.2883.91 Mobile Safari/537.36 OPR/42.7.2246.114996',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) '
    'OPiOS/10.2.0.93022 Mobile/11D257 Safari/9537.53',
    'Mozilla/5.0 (Linux; Android 5.1.1; SM-N750K Build/LMY47X; ko-kr) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/42.0.2311.135 Mobile Safari/537.36 Puffin/6.0.8.15804AP',
    'Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.99 Mobile '
    'Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.99 Mobile '
    'Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.99 Mobile '
    'Safari/537.36',
    'Mozilla/5.0 (iPod; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
    'CriOS/102.0.5005.87 Mobile/15E148 Safari/604.1',
]

statuses = {x for x in range(100, 600)}
statuses.remove(200)
statuses.remove(429)