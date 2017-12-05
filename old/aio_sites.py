import asyncio
import datetime
import re
from urllib.parse import urlsplit
import pdb

import aiohttp
from bs4 import BeautifulSoup
from peewee import fn

from models import Influencer, MajesticUrl, Keyword, objects, mysql
import async_timeout
from urllib.parse import urlparse
import sys
from helper_functions import *

proxy_gateway = 'http://108.59.14.208:13080'

headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
	}

keywords = []
keyword_iterator = None

async def scrape1PageGoogle(query, keyword, start=0, count=10):
	params = {
		'q': query,
		'ie': 'utf-8',
		'oe': 'utf-8',
		'filter': '0',
	}

	if start > 0:
		params['start'] = start

	params['num'] = str(count)

	url = 'https://www.google.com/search'

	async with aiohttp.ClientSession() as session:
		with async_timeout.timeout(10):
			while True:
				try:
					async with session.get(url, params=params, headers=headers, proxy=proxy_gateway) as r:
						txt = await r.text()
						soup = BeautifulSoup(txt, 'html.parser')
						# pdb.set_trace()
						if 'https://www.google.com/search' in str(soup.title): continue
						sites = sitesFromGoogle(soup, keyword)
						return sites
				except Exception as err:
					if '404' in str(err):
						print('got 404 for ', url)
						continue # try again
					elif 'unknown url type' in str(err):
						break # end trying
					else:
						traceback.print_exc()
						continue


async def worker():
	while True:
		try:
			keyword = next(keyword_iterator)
		except StopIteration:
			return

		print('Finding blogs for keyword %s' % (keyword,))

		query = '%s blog' % (keyword)

		for i in range(0, 1000, 100):
			try:
				sites = await scrape1PageGoogle(query, keyword, start=i, count=100)

				if not sites:
					continue

				for site in sites:
					list_of_sites = await objects.execute(Influencer.select(fn.COUNT(Influencer.id)).where(Influencer.websiteurl.contains(site['mainUrl'])))

					count = list_of_sites._rows[0][0]

					if count == 0:
						await objects.create(Influencer, websiteurl=site['mainUrl'], blogurl=site['blogUrl'], websitetitle=site['title'], websitedescription=site['desc'], facebook=site['fb'], linkedin=site['li'], twitter=site['tw'], pinterest=site['pin'], youtube=site['yt'], instagram=site['insta'], googleplus=site['gplus'], pagecontact=site['contactUrl'], pageabout=site['aboutUrl'], phone=site['phone'], email=site['email'], keywordusedtofind=site['keywordUsedToFind'], firstcollected=datetime.datetime.utcnow())

			except Exception as ex:
				print(ex)
				continue

		await objects.execute(Keyword.update(lastscraped=datetime.datetime.utcnow()).where(Keyword.keyword == keyword))


		#print(links)


async def main(workers):
	mysql.set_allow_sync(False)
	await asyncio.gather(*tuple([worker() for _ in range(workers)]))
	await mysql.close_async()


if __name__ == '__main__':
	for model in [Keyword, Influencer]:
		model.create_table(fail_silently=True)

	dbkws = Keyword.select().where(Keyword.lastscraped == None)
	for kw in dbkws:
		keywords.append(kw.keyword)

	keyword_iterator = iter(keywords)

	loop = asyncio.get_event_loop()

	worker_count = 1

	if len(sys.argv) > 1:
		try:
			worker_count = int(sys.argv[1])
		except ValueError:
			print('Invalid worker count')
			exit(1)

	loop.run_until_complete(main(worker_count))
	loop.close()
