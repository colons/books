import re
from random import choice

from bs4 import BeautifulSoup
from textblob import TextBlob

from common import HTML_CONTENT


SENTENCE_TAGS = [
    'div',
    'p',
]

BLACKLIST = [
    '<',
    '>',
    '=',
    '@',
    'http:',
    'https:',
    '.onion',
    '/',
    '192.',
]

CHAIN_LENGTH = 4

SENTENCES = set()
NGRAMS = set()
ENDINGS = []


def get_sentences(html):
    sentences = set()

    for tag in SENTENCE_TAGS:
        for element in BeautifulSoup(html).find_all(tag):
            if any([element.find_all(tag) for tag in SENTENCE_TAGS]):
                # this element contains many elements that might contain sentences
                # so we will ignore it and come back to its children later
                continue

            spacey_text = element.text
            text = re.sub(r'[\r\t\n ]+', ' ', spacey_text).strip()

            for phrase in BLACKLIST:
                if phrase in text:
                    text = ''
                    break

            if not text:
                continue

            for sentence in TextBlob(text).sentences:
                yield sentence

    
def _build_corpus():
    for url, content in HTML_CONTENT.items():
        for sentence in get_sentences(content):
            SENTENCES.add(sentence)

    for sentence in SENTENCES:
        for ngram in sentence.ngrams(4):
            NGRAMS.add(tuple(ngram._collection))

        ENDINGS.append(tuple(sentence.words[-(CHAIN_LENGTH - 1):]))

_build_corpus()


def markov():
    words = []

    first_sentence = choice([s for s in SENTENCES
                             if len(s.words) >= CHAIN_LENGTH])
    words.extend(first_sentence.words[:CHAIN_LENGTH - 1])

    while True:
        chain = tuple(words[-(CHAIN_LENGTH - 1):])
        choices = []

        for ngram in NGRAMS:
            if tuple(ngram)[:(CHAIN_LENGTH - 1)] == chain:
                choices.append(ngram[-1])

        for ending in ENDINGS:
            if chain == ending:
                choices.append(None)

        new = choice(choices)

        if new is None:
            break
        else:
            words.append(new)

    return ' '.join(words)


if __name__ == '__main__':
    for i in range(30):
        print()
        print(markov())
