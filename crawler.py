import base64
import os.path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException


STARTING_POINTS = [
    'http://zqktlwi4fecvo6ri.onion/',
    'http://torlinkbgs6aabns.onion/',
    'http://dirnxxdraygbifgc.onion/',
]
KNOWN_URLS = set(STARTING_POINTS)
HTML_CONTENT = dict()
CACHE_DIR = os.path.realpath(os.path.join(__file__, '..', 'cache'))


def get_html(url):
    print(' :: HEAD {url}'.format(url=url))

    head = requests.head(url)

    if head.headers.get('content-type').startswith('text/html'):
        print(' :: GET {url}'.format(url=url))
        return requests.get(url).text
    else:
        print(' :: not html')


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


def save(url, content):
    filename = base64.b32encode(url.encode('utf-8')).decode('utf-8')

    with open(os.path.join(CACHE_DIR, filename), 'w') as cache_file:
        cache_file.write(content)


def load():
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

        print('loaded {0}'.format(url))


def crawl():
    load()

    while True:
        difference = KNOWN_URLS.difference(HTML_CONTENT)
        if not difference:
            print('no unseen urls')
            break

        for url in difference:
            try:
                html = get_html(url)
            except RequestException:
                continue

            HTML_CONTENT[url] = html or ''
            save(url, html)

            if html is None:
                continue

            soup = BeautifulSoup(html)

            record_link_urls(url, soup)


if __name__ == "__main__":
    crawl()
