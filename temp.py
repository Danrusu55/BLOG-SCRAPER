from helper_functions import *
from models import Influencer

proxy_gateway = 'http://108.59.14.208:13080'

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
}

url = 'https://www.google.com/search'

query = 'blog dog training'

params = {
    'q': query,
    'ie': 'utf-8',
    'oe': 'utf-8',
    'filter': '0',
    'num': '100'
}

while True:
    r = requests.get(url, proxies=proxy_gateway, params=params, headers=headers)

    soup = BeautifulSoup(r.content)

    print(soup.title)
