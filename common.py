import base64
import os.path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from sys import argv


STARTING_POINTS = argv[1:]
KNOWN_URLS = set(STARTING_POINTS)
HTML_CONTENT = dict()
CACHE_DIR = os.path.realpath(os.path.join(__file__, '..', 'cache'))


def record_link_urls(base_url, soup):
    for element in soup.select('[href]'):
        absolute_url = urljoin(base_url, element['href'])
        parsed_absolute_url = urlparse(absolute_url)

        if (
            parsed_absolute_url.scheme not in ['http', 'https'] or
            parsed_absolute_url.fragment or
            (not parsed_absolute_url.hostname.endswith('.onion'))
        ):
            continue

        KNOWN_URLS.add(absolute_url)



def _load():
    """
    Populate KNOWN_URLS and HTML_CONTENT based on the contents of the cache
    directory.
    """

    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    for filename in os.listdir(CACHE_DIR):
        url = base64.b32decode(filename).decode('utf-8')
        KNOWN_URLS.add(url)

        with open(os.path.join(CACHE_DIR, filename)) as html_file:
            html = html_file.read()
            HTML_CONTENT[url] = html
            record_link_urls(url, BeautifulSoup(html))


_load()
