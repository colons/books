import os.path
import uuid

from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

from common import KNOWN_URLS, HTML_CONTENT, CACHE_DIR, record_link_urls


def get_html(url):
    print(' :: HEAD {url}'.format(url=url))

    head = requests.head(url)

    if head.headers.get('content-type', '').startswith('text/html'):
        print(' :: GET {url}'.format(url=url))
        return requests.get(url).text
    else:
        print(' :: not html')


def save(url, content):
    filename = str(uuid.uuid4())

    with open(os.path.join(CACHE_DIR, filename), 'w') as cache_file:
        cache_file.write(url + '\n\n' + content)


def crawl():
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
            save(url, html or '')

            if html is None:
                continue

            soup = BeautifulSoup(html)

            record_link_urls(url, soup)


if __name__ == "__main__":
    crawl()
