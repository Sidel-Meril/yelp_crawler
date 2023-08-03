# Yelp crawler

Yelp crawler is well-optimized crawler utility that scraps all the businesses from Yelp website.

```
-------Report-------
Gathered:  239
Time (s):  22.167
```

Each business object consists from:
+ Business name
+ Business rating
+ Number of reviews
+ Business yelp url
+ Business website
+ List of first 5 reviews, for each review:
  - Reviewer name
  - Reviewer location
  - Review date

## Requirements

Yelp crawler requires [Python 3.9](https://www.python.org/downloads/release/python-395/)

Main packages:
- aiohttp==3.8.5
- lxml==4.9.3
- urllib3==2.0.4

For tests additionally the next packages is required:
- requests==2.31.0
- httpretty==1.1.4

## Installation

1. Download project

Git installation

```bash
sudo apt install git-all
```

Cloning of repo
```bash
git clone -b main https://github.com/sidelmeril/yelp_crawler.git
```

Move to cloned repo
```bash
cd yelp_crawler
```

2. Install requirements
```bash
pyhton3 -m pip install -r requirements.txt --ignore-installed
```
or try *(Linux)*
```bash
cat requirements.txt | xargs -n 1 python3 -m pip install
```

## Usage

The generic syntax of Yelp crawler:
```bash
python run.py [SCRAPER-ARGUMENTS] [SCRAPER-OPTIONS] [GLOBAL-OPTIONS...]
```

```python run.py --help``` provide details on the options and arguments:

+ ```-cn``` or ```--category_name```: The name of the search category (type: string, default: None).
+ ```-l``` or ```--location```: The location of the search (type: string, default: None).
+ ```-o``` or ```--output_fn```: The filename (in JSON format) to store the parsed results (type: string, default: 'output.json').
+ ```-mp``` or ```--max_pages```: The maximum number of pages to scrape (type: integer, default: None).
+ ```-mb``` or ```--max_business```: The maximum number of businesses to scrape (type: integer, default: None).
+ ```-mr``` or ```--max_reviews```: The maximum number of reviews to scrape for each business (type: integer, default: 5).

**Example**
```bash
python run.py -cn 'Contractors' -l 'San Francisco, CA' -o 'output.json'
```

The example output is [provided](/output.json)

**Note:** If any error occurred, you can check [api.log](/_api.log) for
additional explanation. The most common problem is the 503 Access Denied 
code.

## License

Lorem Ipsum