import re
from functools import lru_cache


@lru_cache(max_size=2)
def re_word():
    return re.compile(r"""[\#\@\w](['\-]?\w){,24}""", re.UNICODE)


def tokenize(text):
    return [token.group() for token in re_word().finditer(text.lower())]
