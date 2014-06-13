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
    '|',
    '=',
    '@',
    'http:',
    'https:',
    '.onion',
    '/',
    '192.',
    '.net',
    '.org',
    '.com',
    'UTC',
    '«',
    '»',
    'www',
]

CHAIN_LENGTH = 3

SENTENCES = set()
NGRAMS = set()
ENDINGS = []

OUTPUT_BLACKLIST = set()

with open('/usr/share/dict/words') as wordlist_file:
    WORDS = {w.strip().lower() for w in wordlist_file.readlines()}


def get_sentences(html):
    for tag in SENTENCE_TAGS:
        for element in BeautifulSoup(html).find_all(tag):
            if any([element.find_all(tag) for tag in SENTENCE_TAGS]):
                # this element contains many elements that might contain
                # sentences so we will ignore it and come back to its children
                # later
                continue

            spacey_text = element.text
            text = re.sub(r'[\r\t\n ]+', ' ', spacey_text).strip()

            for phrase in BLACKLIST:
                if phrase in text:
                    text = ''
                    break

            if not text:
                continue

            OUTPUT_BLACKLIST.add(text)

            try:
                sentences = TextBlob(text).sentences
            except ValueError:
                continue

            for sentence in sentences:
                # decide if this sentences is probably english or not
                native_wordcount = 0

                for word in sentence.words:
                    if word.lower() in WORDS:
                        native_wordcount += 1

                if native_wordcount < len(sentence.words)/2:
                    continue

                # we want to include punctiation in our matching, so textblob's
                # sentences are useless to us
                yield tuple(sentence.raw.split(' '))


def _build_corpus():
    for url, content in HTML_CONTENT.items():
        for sentence in get_sentences(content):
            SENTENCES.add(sentence)

    for sentence in SENTENCES:
        if len(sentence) < CHAIN_LENGTH:
            continue

        for ngram in [tuple(sentence[i:i+CHAIN_LENGTH])
                      for i in range(0, (len(sentence) - CHAIN_LENGTH) + 1)]:
            NGRAMS.add(ngram)

        ENDINGS.append(tuple(sentence[-(CHAIN_LENGTH - 1):]))

_build_corpus()


def eq(a, b):
    """
    Return True if, for our purposes, a tuple of words can be considered equal.
    Case-insensitive, but punctuation-sensitive.
    """

    if len(a) != len(b):
        raise ValueError('tuples of differing length handed to eq():\n'
                         '{0}, {1}'.format(a, b))

    for i in range(len(a)):
        if a[i].lower() != b[i].lower():
            return False

    return True


def markov():
    words = []

    first_sentence = choice([s for s in SENTENCES
                             if len(s) >= CHAIN_LENGTH])
    words.extend(first_sentence[:CHAIN_LENGTH - 1])

    while True:
        chain = tuple(words[-(CHAIN_LENGTH - 1):])
        choices = []

        for ngram in NGRAMS:
            if eq(tuple(ngram)[:(CHAIN_LENGTH - 1)], chain):
                choices.append(ngram[-1])

        for ending in ENDINGS:
            if eq(chain, ending):
                choices.append(None)

        new = choice(choices)

        if new is None:
            break
        else:
            words.append(new)

    return ' '.join(words)


if __name__ == '__main__':
    while True:
        result = markov()

        if result not in OUTPUT_BLACKLIST:
            print(result)
            print()
