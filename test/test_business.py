import unittest
import requests, urllib.parse
import httpretty
from lxml import html

sample_search_fn = 'business_mock.html'

class ApiTest(unittest.TestCase):
    def test_get_api_page(self):
        desc = 'Contractors'
        loc = 'San Francisco, CA'
        api_url = 'https://www.yelp.com/search?{query}'
        api_query = {
            'find_desc': desc,
            'find_loc': loc,
        }
        api_point = api_url.format(query=urllib.parse.urlencode(api_query, quote_via=urllib.parse.quote))

        r = requests.get(api_point)
        self.assertNotEqual(r.status_code, 503, f"Access denied to {api_point}")
        self.assertEqual(r.status_code, 200, f"API search point isn't available at {api_point}")
        httpretty.enable(allow_net_connect=True, verbose=True)
        httpretty.register_uri(httpretty.GET, api_point, status=200, body=r.text)

class SearchTest(unittest.TestCase):
    def setUp(self):
        desc = 'Contractors'
        loc = 'San Francisco, CA'
        api_url = 'https://www.yelp.com/search?{query}'
        api_query = {
            'find_desc': desc,
            'find_loc': loc,
        }
        api_point = api_url.format(query=urllib.parse.urlencode(api_query, quote_via=urllib.parse.quote))
        r = requests.get(api_point)
        self.page = html.fromstring(r.text)

    def test_get_business_list(self):
        _bus_xpath = '//div[contains(@class, "mainAttributes")]'
        businesses = self.page.xpath(_bus_xpath)
        self.assertFalse(len(businesses)==0, f"HtmlElements of businesses can't be reached by {_bus_xpath}")

class BusinessTest(unittest.TestCase):
    def setUp(self):
        desc = 'Contractors'
        loc = 'San Francisco, CA'
        api_url = 'https://www.yelp.com/search?{query}'
        api_query = {
            'find_desc': desc,
            'find_loc': loc,
        }
        api_point = api_url.format(query=urllib.parse.urlencode(api_query, quote_via=urllib.parse.quote))
        r = requests.get(api_point)
        self.page = html.fromstring(r.text)
        _bus_xpath = '//div[contains(@class, "mainAttributes")]'
        businesses = self.page.xpath(_bus_xpath)
        self._bus_htmlel = businesses[0]

    def test_get_business_name(self):
        settings = {
            'Business name': ['.//div[1]', './/div','.//div', './/div', './/h3', './/span', './/a'],

        }

        for case_name, xpaths in settings.items():
            res = [self._bus_htmlel]
            for xpath in xpaths:
                res = res[0].xpath(xpath)
                self.assertNotEqual(len(res), 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}")

    def test_get_business_url(self):
        settings = {
            'Business YelpCrawler URL': ['.//div[1]', './/div', './/div', './/div', './/h3', './/span', './/a'],

        }

        for case_name, xpaths in settings.items():
            res = [self._bus_htmlel]
            for xpath in xpaths:
                res = res[0].xpath(xpath)
                self.assertNotEqual(len(res), 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}")

    def test_get_business_number_of_reviews(self):
        settings = {
            'Business number of reviews': ['.//span[contains(text(),"review")]'],

        }

        for case_name, xpaths in settings.items():
            res = [self._bus_htmlel]
            for xpath in xpaths:
                res = res[0].xpath(xpath)
                self.assertNotEqual(len(res), 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}")

    def test_get_rating(self):
        settings = {
            'Business rating': ['.//span[re:match(text(),"\d.\d")]'],
        }

        for case_name, xpaths in settings.items():
            res = [self._bus_htmlel]
            for xpath in xpaths:
                res = res[0].xpath(xpath, namespaces={
                        're': 'http://exslt.org/regular-expressions'})
                self.assertNotEqual(len(res), 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}")


def create_test_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(ApiTest))
    test_suite.addTest(unittest.makeSuite(SearchTest))
    test_suite.addTest(unittest.makeSuite(BusinessTest))

    return test_suite

if __name__ == "__main__":
    suite = create_test_suite()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)