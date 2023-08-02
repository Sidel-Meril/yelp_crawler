import asyncio
from  YelpCrawler.api import Crawler

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description="a yelp crawler that scraps all the businesses from Yelp website")
    parser.add_argument("-cn", "--category_name", type=str, default=None, help="Name of search category")
    parser.add_argument("-l", "--location", type=str, default=None, help="Location of search")
    parser.add_argument("-o", "--output_fn", type=str, default='output.json', help="Filename (.json) of parsed results")
    parser.add_argument("-mp", "--max_pages", type=int, default=None, help="Filename (.json) of parsed results")
    parser.add_argument("-mb", "--max_business", type=int, default=None, help="Filename (.json) of parsed results")
    parser.add_argument("-mr", "--max_reviews", type=int, default=5, help="Filename (.json) of parsed results")

    args = parser.parse_args()

    crwl = Crawler(output_fn=args.output_fn)
    asyncio.run(crwl.run(category_name=args.category_name, location=args.location))
