'''
Description of main data structures used in Yelp Crawler.

'Review' describes the business review by given HtmlElement:
- reviewer_name: str
- reviewer_location (if provided): str
- review_date: str

'Business' describes the business object by given HtmlElement
- business_name: str
- business_rating: float
- number_of_reviews: int
- business_yelp_url: str
- business_website: str
- reviews: list = []

Example:
    >>> from YelpCrawler.structures import Business
    >>> import lxml
    >>> ...
    >>> sample
    <!DOCTYPE html>
    <html>
    <body>

    <p>Sample business</p>

    <p><b>0 reviews</b></p>

    </body>
    </html>
    >>> el = lxml.html.fromstring(sample).xpath('.//body')
    >>> business_body = Business(el)
    >>> business_body.number_of_reviews = './/p/b/text()'
    >>> business_body
    0
    >>> isinstance(business_body, int)
    True
'''
import json, re
from datetime import datetime
from lxml import html
from lxml.html import HtmlElement

domain = 'https://www.yelp.com'
date_format = '%m/%d/%Y'
get_digits = lambda x: re.findall('[0-9.]+',x[0])
get_href = lambda name: domain+name[0].split('?')[0] if name[0].startswith('/') else None
def is_serializable(obj):
    try:
        json.dumps(obj)
        return True
    except (TypeError, OverflowError):
        return False


class DataStructure(object):
    def __init__(self, el: HtmlElement):
        self._html_element = el
        pass

    @property
    def html_element(self):
        return self._html_element

    def __str__(self):
        serializable_objects = lambda o: {k.strip('_'):v for k, v in o.__dict__.items() if is_serializable(v)}
        return json.dumps(self, default=serializable_objects, indent=2)

    def __iter__(self):
        for k, v in self.__dict__.items():
            if is_serializable(v):
                yield (k.strip('_'), v)

    def _search(self, xpath):
        res = self.html_element.xpath(xpath)
        if len(res)==0:
            raise KeyError(f'The value {xpath} is missing from {html.tostring(self.html_element)}')
        else:
            return res

    def _search_re(self, xpath):
        res = self.html_element.xpath(xpath, namespaces={
        're': 'http://exslt.org/regular-expressions'})
        if len(res)==0:
            raise KeyError(f'The value {xpath} is missing from {html.tostring(self.html_element)}')
        else:
            return res

    def _is_valid(self):
        for k, v in self.__dict__.items():
            if is_serializable(v):
                if v==None:
                    return False
        return True

class Review(DataStructure):
    def __init__(self, el: HtmlElement):
        super(Review, self).__init__(el)
        self._reviewer_name: str = None
        self._reviewer_location: str = None
        self._review_date: str = None

    @property
    def reviewer_name(self):
        return self._reviewer_name

    @reviewer_name.setter
    def reviewer_name(self, xpath: str):
        name = self._search(xpath)
        self._reviewer_name = name[0] #if isinstance(name[0], str) else None

    @property
    def reviewer_location(self):
        return self._reviewer_location

    @reviewer_location.setter
    def reviewer_location(self, xpath: str):
        try:
            name = self._search(xpath)
            self._reviewer_location = name[0]  # if isinstance(name[0], str) else None
        except KeyError:
            self._reviewer_location = None

    @property
    def review_date(self):
        return self._review_date

    @review_date.setter
    def review_date(self, xpath: str):
        name = self._search(xpath)
        date = datetime.strptime(name[0], date_format)
        self._review_date = str(date.date())

class Business(DataStructure):
    """
    Business object
    """
    def __init__(self, el: HtmlElement):
        super(Business, self).__init__(el)
        self._business_name: str = None
        self._business_rating: float = None
        self._number_of_reviews: int = None
        self._business_yelp_url: str = None
        self._business_website: str = None
        self.reviews: list = []

    @property
    def business_name(self):
        return self._business_name

    @business_name.setter
    def business_name(self, xpath: str):
        name = self._search(xpath)
        self._business_name = name[0] #if isinstance(name[0], str) else None

    @property
    def business_rating(self):
        return self._business_rating

    @business_rating.setter
    def business_rating(self, pattern: re.Pattern):
        try:
            name = self._search_re(pattern)
            val = float(''.join(re.findall('[0-9.]+', name[0])))
        except KeyError:
            val = None
        self._business_rating = val

    @property
    def number_of_reviews(self):
        return self._number_of_reviews

    @number_of_reviews.setter
    def number_of_reviews(self, xpath: str):
        try:
            name = self._search(xpath)
            val = int(''.join(re.findall('[0-9]+', name[0])))
        except KeyError:
            val = 0
        self._number_of_reviews = val

    @property
    def business_yelp_url(self):
        return self._business_yelp_url

    @business_yelp_url.setter
    def business_yelp_url(self, xpath: str):
        name = self._search(xpath)
        href = name[0].split('?')[0] if name[0].startswith('/') else None
        self._business_yelp_url = domain+href #if isinstance(href, str) else None

    @property
    def business_website(self):
        return self._business_website

    @business_website.setter
    def business_website(self, candidates: list):
        if len(candidates)>0:
            name = candidates[0]
        else:
            name = None
        self._business_website = name #if isinstance(name, str) else None




