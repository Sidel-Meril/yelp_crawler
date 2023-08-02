import requests, urllib.parse
from lxml import html
from YelpCrawler.structures import Business, Review
import cProfile
from io import StringIO
from memory_profiler import profile as memmory_profile

def cpu_profile(func):
    def wrapper(*args, **kwagrs):
        profiler = cProfile.Profile()
        profiler.enable()
        func(*args, **kwagrs)
        profiler.disable()
        profiler.print_stats()
    return wrapper

output = StringIO()

@cpu_profile
@memmory_profile
def test():
    desc='Contractors'
    loc='San Francisco, CA'
    api_url = 'https://www.yelp.com/search?{query}'
    api_query ={
       'find_desc': desc,
       'find_loc': loc,
    }
    r = requests.get(api_url.format(query=urllib.parse.urlencode(api_query, quote_via=urllib.parse.quote)))
    if r.status_code==503:
        raise requests.ConnectionError(f"API point at "
                                       f"{api_url} isn't available")
    page = html.fromstring(r.text)

    businesses = page.xpath('//div[contains(@class, "mainAttributes")]')
    print(r.status_code, len(businesses))

    for business in businesses[:5]:
        business_body = Business(business)
        business_body.business_name = './/div[1]/div/div/div/h3/span/a/text()'
        business_body.business_yelp_url = './/div[1]/div/div/div/h3/span/a/@href'
        business_body.business_rating = './/span[re:match(text(),"\d.\d")]/text()'
        business_body.number_of_reviews = './/span[contains(text(),"review")]/text()'
        r = requests.get(business_body.business_yelp_url)
        if r.status_code==503:
            raise requests.ConnectionError(f"API point at "
                                                              f"{business_body.business_yelp_url} isn't available")
        print(business_body.business_yelp_url)

        page = html.fromstring(r.text)
        business_body.business_website = page.xpath('//a[contains(@href, "biz_redir")]/text()')

        reviews = page.xpath('//ul[contains(@class, "undefined list")]/li/div')
        reviews = list(filter(lambda x: b"user-passport-info" in html.tostring(x), reviews))[:5]

        for review in reviews:
            review_body = Review(review)
            review_body.reviewer_name = './/div[contains(@class, "user-passport-info")]/span/a/text()'
            review_body.reviewer_location = './/div[contains(@class, "user-passport-info")]/div/div/span/text()'
            review_body.review_date = './/div[2]/div/div[2]/span/text()'
            business_body.reviews.append(dict(review_body))
        print(business_body._is_valid(), business_body)

test()