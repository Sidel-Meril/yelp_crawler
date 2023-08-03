import unittest
import requests
import httpretty
from lxml import html

test_sample = 'https://www.yelp.com/biz/prosper-construction-san-francisco'

class GetBusinessTest(unittest.TestCase):
    def test_get_business_page(self):
        r = requests.get(test_sample)
        self.assertNotEqual(r.status_code, 503, f"Access denied to {test_sample}")
        self.assertEqual(r.status_code, 200, f"Business isn't available at {test_sample}")
        httpretty.enable(allow_net_connect=True, verbose=True)
        httpretty.register_uri(httpretty.GET, test_sample, status=200, body=r.text)

class ReviewsTest(unittest.TestCase):
    def setUp(self) -> None:
        r = requests.get(test_sample)
        self.page = html.fromstring(r.text)

    def test_get_reviews_list(self):
        _rev_xpath = '//ul[contains(@class, "undefined list")]/li/div'
        reviews = self.page.xpath(_rev_xpath)
        self.assertFalse(len(reviews)==0, f"HtmlElements of reviews can't be reached by {_rev_xpath}")

    def test_get_website(self):
        _webs_xpath='//a[contains(@href, "biz_redir")]'
        business_website = self.page.xpath('//a[contains(@href, "biz_redir")]')
        self.assertFalse(len(business_website) == 0, f"HtmlElement of business website can't be reached by {_webs_xpath}")

class GetReviewTest(unittest.TestCase):
    def setUp(self) -> None:
        r = requests.get(test_sample)
        page = html.fromstring(r.text)
        _rev_xpath = '//ul[contains(@class, "undefined list")]/li/div'
        reviews = page.xpath(_rev_xpath)
        self._rev_htmlel = reviews[0]


    def test_get_reviewer_name(self):
        settings = {
            'Reviewer name': ['.//div[contains(@class, "user-passport-info")]','.//span','.//a'],
        }

        for case_name, xpaths in settings.items():
            res = [self._rev_htmlel]
            for xpath in xpaths:
                _prev = res[0]
                res = res[0].xpath(xpath)
                self.assertFalse(len(res) == 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}. "
                                                f"\n Element code:\n{html.tostring(_prev)}")

    def test_get_reviewer_location(self):
        settings = {
            'Reviewer location': ['.//div[contains(@class, "user-passport-info")]','.//div','.//div','.//span'],
        }

        for case_name, xpaths in settings.items():
            res = [self._rev_htmlel]
            for xpath in xpaths:
                _prev = res[0]
                res = res[0].xpath(xpath)
                self.assertFalse(len(res) == 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}. "
                                                f"\n Element code:\n{html.tostring(_prev)}")

    def test_get_review_date(self):
        settings = {
            'Review date': ['.//div[2]/div/div[2]/span/text()'],

        }

        for case_name, xpaths in settings.items():
            res = [self._rev_htmlel]
            for xpath in xpaths:
                _prev=res[0]
                res = res[0].xpath(xpath)
                self.assertFalse(len(res) == 0, f"{case_name} can't be reached by {xpath} in sequence {xpaths}. "
                                                f"\n Element code:\n{html.tostring(_prev)}")

def create_test_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(GetBusinessTest))
    test_suite.addTest(unittest.makeSuite(ReviewsTest))
    test_suite.addTest(unittest.makeSuite(GetReviewTest))

    return test_suite

if __name__ == "__main__":
    suite = create_test_suite()
    runner = unittest.TextTestRunner()
    result = runner.run(suite)