from twitter import Twitter, OAuth

from secrets import auth
from markov import markov, OUTPUT_BLACKLIST


api = Twitter(auth=OAuth(*auth))


if __name__ == '__main__':
    while True:
        string = markov()
        if (
            len(string) < 140 and
            string not in OUTPUT_BLACKLIST
        ):
            api.statuses.update(status=string)
            break
