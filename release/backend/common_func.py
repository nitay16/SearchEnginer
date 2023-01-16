import pickle
from contextlib import closing
import google.cloud.storage as storage
import re
from functools import lru_cache
import backend.inverted_index_gcp


# environment vars
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')

TUPLE_SIZE = 6


@lru_cache(maxsize=2)
def re_word():
    return re.compile(r"""[\#\@\w](['\-]?\w){,24}""", re.UNICODE)


def tokenize(text):
    english_stopwords = frozenset(stopwords.words('english'))
    corpus_stopwords = ["category", "references", "also", "external", "links",
                        "may", "first", "see", "history", "people", "one", "two",
                        "part", "thumb", "including", "second", "following",
                        "many", "however", "would", "became"]

    all_stopwords = english_stopwords.union(corpus_stopwords)
    return [term_token for term_token in [token.group() for token in re_word().finditer(text.lower())] if term_token not in all_stopwords]


def read_pkl_file_form_bucket(file_name, name_bucket):
    """
        func that read pkl file from the bucket
    Args:
        name_bucket: name of the bucket
        file_name: the name of the pkl file + dir : pagerank\page_rank

    Returns:
            dict
    """
    # access to the bucket
    bucket = storage.Client().get_bucket(name_bucket)
    blob = bucket.get_blob(f'{file_name}.pkl')
    if blob:
      with blob.open("rb") as pkl_file:
          return pickle.load(pkl_file)


def read_posting_list(inverted, w, bucket_name):
    try:
      with closing(backend.inverted_index_gcp.MultiFileReader()) as reader:
        locs = inverted.posting_locs[w]
        b = reader.read(bucket_name, locs, inverted.df[w] * TUPLE_SIZE)
        posting_list = []
        for i in range(inverted.df[w]):
          doc_id = int.from_bytes(b[i*TUPLE_SIZE:i*TUPLE_SIZE+4], 'big')
          tf = int.from_bytes(b[i*TUPLE_SIZE+4:(i+1)*TUPLE_SIZE], 'big')
          posting_list.append((doc_id, tf))
        return posting_list
    except:
        return []
