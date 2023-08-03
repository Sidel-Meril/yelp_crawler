'''
Yelp Crawler that gathers all business by defined category_name and location

Usage:

>>> from YelpCrawler.api import Crawler
... import asyncio
>>> crawl_obj = Crawler(
                 max_pages = None,
                 max_reviews = 5,
                 max_business = None,
                 logger_fn = 'api.log',
                 limit_attempts = 5,
                 output_fn = 'output.json')
>>> asyncio.run(crawl_obj.run())
'''

import json
import urllib.parse
from lxml import html
from YelpCrawler.structures import Business, Review
from YelpCrawler.structures import get_digits, get_href
import logging
import aiohttp
import asyncio
import time

class Crawler():
    def __init__(self,
                 max_pages = None,
                 max_reviews = 5,
                 max_business = None,
                 logger_fn = 'api.log',
                 limit_attempts = 5,
                 output_fn = 'output.json'):
        self.max_pages = max_pages
        self.max_reviews=max_reviews
        self.max_business = max_business
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=logger_fn,
                            filemode='w')
        self.logger = logging.getLogger()
        self.businesses = dict()
        self.limit_attempts = limit_attempts
        self.output_fn = output_fn
        self._cache = dict()
        self.tasks = []

    def _async_retry(func, retries=3, exceptions=(ConnectionError,), backoff=2):
        async def wrapper(*args, **kwargs):
            delay = 1
            for _ in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    msg = f"Caught exception: {e}. Retrying..."
                    print(msg)
                    await asyncio.sleep(delay)
                    delay *= backoff
            raise RuntimeError(f"Reached maximum retries ({retries}) for {func.__name__}")

        return wrapper


    @_async_retry
    async def fetch_url(self, url):
        if not self._cache.get(url, False):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status==200:
                        msg = f'Crawler requested to {url}'
                        self.logger.info(msg)
                        self._cache[url] = await r.text()
                        return self._cache[url]
                    elif r.status==503:
                        msg = f'Access denied to {url}. Code 503'
                        self.logger.error(msg)
                        raise ConnectionError(msg)
                    else:
                        msg = f'Request to {url} failed with code {r.status}'
                        self.logger.error(msg)
                        raise ConnectionError(msg)
        else:
            return self._cache[url]

    def get_search_url(self,
                        desc='Contractors',
                        loc='San Francisco, CA',
                        page=0):
        api_url = 'https://www.yelp.com/search?{query}'
        api_query = {
            'find_desc': desc,
            'find_loc': loc,
            'start': page * 10,
        }
        return api_url.format(query=urllib.parse.urlencode(api_query, quote_via=urllib.parse.quote_plus))

    async def get_total_pages(self,
                        desc='Contractors',
                        loc='San Francisco, CA'):
        url = self.get_search_url(
                        desc=desc,
                        loc=loc)
        res = await self.fetch_url(url)
        page = html.fromstring(res)
        total_pages = get_digits(page.xpath('//div[contains(@class, "pagination_")]/div[2]/span/text()'))[-1]
        self._cache[url]=res
        return int(total_pages)

    async def generate_searches(self,
                    desc='Contractors',
                    loc='San Francisco, CA'):
        if not self.max_pages:
            total_pages = await self.get_total_pages(
                        desc=desc,
                        loc=loc)
        else:
            total_pages = self.max_pages
        msg = f'Estimated count of pages for {desc} in {loc}: {total_pages}'
        self.logger.info(msg)
        for page in range(total_pages):
            yield self.get_search_url(
                        desc=desc,
                        loc=loc,
                        page=page)

    async def fetch_searches(self, *args, **kwargs):
        urls = self.generate_searches(*args, **kwargs)
        self.tasks = []
        _urls = []
        async for url in urls:
            self.tasks.append(self.fetch_url(url))
            _urls.append(url)
        await asyncio.gather(*self.tasks)
        return _urls

    def generate_review_queue(self, _urls: list):
        self.tasks = []
        for url in _urls:
            search_html = self._cache.get(url, None)
            if search_html!=None:
                page = html.fromstring(search_html)
                businesses = page.xpath('//div[contains(@class, "mainAttributes")]')
                if self.max_business:
                    businesses = businesses[:self.max_business]
                for business in businesses:
                    business_url = business.xpath('.//div[1]/div/div/div/h3/span/a/@href')
                    business_url = get_href(business_url)
                    self.logger.info(f'Extracted business Yelp URL {business_url}')
                    self.tasks.append(self.fetch_url(business_url))

    def generate_business_obj_queue(self, _urls: list):
        for url in _urls:
            search_html = self._cache.get(url, None)
            if search_html != None:
                page = html.fromstring(search_html)
                businesses = page.xpath('//div[contains(@class, "mainAttributes")]')[:self.max_business]
                if self.max_business:
                    businesses = businesses[:self.max_business]
                for business in businesses:
                    business_body = self.fetch_business(business)
                    yield business_body

    def fetch_business(self, business: html.HtmlElement):
        business_body = Business(business)
        business_body.business_name = './/div[1]/div/div/div/h3/span/a/text()'
        business_body.business_yelp_url = './/div[1]/div/div/div/h3/span/a/@href'
        business_body.business_rating = './/span[re:match(text(),"\d.\d")]/text()'
        business_body.number_of_reviews = './/span[contains(text(),"review")]/text()'
        return business_body

    async def fetch_details(self, *args, **kwargs):
        res = await self.fetch_searches(*args, **kwargs)
        self.generate_review_queue(res)
        await asyncio.gather(*self.tasks)
        for business in self.generate_business_obj_queue(res):
            business_body = self.fetch_reviews(business)
            print(business_body)
            yield business_body

    def fetch_reviews(self, business_body: Business):
        page = html.fromstring(self._cache[business_body.business_yelp_url])
        business_body.business_website = page.xpath('//a[contains(@href, "biz_redir")]/text()')
        reviews = page.xpath('//ul[contains(@class, "undefined list")]/li/div')
        reviews = list(filter(lambda x: b"user-passport-info" in html.tostring(x), reviews))
        if self.max_reviews:
            reviews = reviews[:self.max_reviews]

        for review in reviews:
            review_body = Review(review)
            review_body.reviewer_name = './/div[contains(@class, "user-passport-info")]/span/a/text()'
            review_body.reviewer_location = './/div[contains(@class, "user-passport-info")]/div/div/span/text()'
            review_body.review_date = './/div[2]/div/div[2]/span/text()'
            business_body.reviews.append(dict(review_body))
        # print(business_body)
        return business_body

    async def run(self,
            category_name: str ='Contractors',
            location: str ='San Francisco, CA', *args, **kwargs):
        res = []
        _start = time.time()
        async for business_body in self.fetch_details(desc=category_name, loc=location):
            res.append(dict(business_body))

        with open(self.output_fn, 'w', encoding='utf-8') as f:
            f.write(json.dumps(res, indent=2))
        _end = time.time()

        print('Report'.center(20, '-'))
        print('Gathered: ', len(res))
        print('Time (s): ', round(_end-_start, 3))

        msg = f'Crawler finished. Gathered {len(res)} for {round(_end-_start, 3)} s.'
        self.logger.info(msg)

if __name__=='__main__':
    crwl = Crawler(max_reviews=5, max_pages=1, output_fn='sample.json')
    asyncio.run(crwl.run())
