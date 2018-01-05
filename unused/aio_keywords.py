import asyncio
import datetime
import re
from urllib.parse import urlsplit
import aiohttp
from bs4 import BeautifulSoup
from peewee import fn
from models import Website, Keyword, MajesticUrl, objects, mysql
import async_timeout
from urllib.parse import urlparse
import sys

proxy_gateway = 'http://108.59.14.208:13080'

# GLOBALS
ALL_URLS = []
ALL_URLS_ITERATOR = None

async def getKeywords(url):
	# in url, out keywords
	keywordsArray = []
	params = {
		'ie': 'utf-8',
		'oe': 'utf-8',
		'filter': '0',
	}
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
	}
	url = 'https://www.similarsites.com/site/' + url

	async with aiohttp.ClientSession() as session:
		with async_timeout.timeout(30):
					async with session.get(url, params=params, headers=headers, proxy=proxy_gateway) as r:
						txt = await r.text()
						soup = BeautifulSoup(txt, 'html.parser')
						site_keywords = soup.findAll('span',{'class':'badge thin'})
						if site_keywords:
							for keyword in site_keywords:
								keywordsArray.append(keyword.text)
						return keywordsArray

async def worker():
	while True:
		try:
			url = next(ALL_URLS_ITERATOR)
		except StopIteration:
			return

		print('Finding keywords for url %s' % (url,))
		await objects.execute(MajesticUrl.update(lastscraped=datetime.datetime.utcnow()).where(MajesticUrl.websiteurl == url))

		try:
			keywords_array = await getKeywords(url)
			if not keywords_array:
				continue

			for keyword in keywords_array:
				try:
					res = await objects.execute(
							Keyword.select(fn.COUNT(Keyword.id).alias('keyword_count')).where(Keyword.keyword.contains(keyword)))

					if res[0].keyword_count == 0:
						await objects.create(Keyword, keyword=keyword)
				except: # catching codec errors
					continue

		except Exception as ex:
			print(ex)
			pass
		continue

async def main(workers):
	mysql.set_allow_sync(False)
	await asyncio.gather(*tuple([worker() for _ in range(workers)]))
	await mysql.close_async()


if __name__ == '__main__':
	for model in [MajesticUrl, Keyword]:
		model.create_table(fail_silently=True)

	majestic_urls = MajesticUrl.select().where(MajesticUrl.lastscraped == None).limit(100000)
	for majestic_url in majestic_urls:
		ALL_URLS.append(majestic_url.websiteurl)

	ALL_URLS_ITERATOR = iter(ALL_URLS)

	loop = asyncio.get_event_loop()

	worker_count = 25

	if len(sys.argv) > 1:
		try:
			worker_count = int(sys.argv[1])
		except ValueError:
			print('Invalid worker count')
			exit(1)

	loop.run_until_complete(main(worker_count))
	loop.close()
