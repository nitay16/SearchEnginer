import math
from collections import defaultdict, Counter

import numpy as np

from backend.common_func import tokenize
from backend.common_func import read_posting_list

def get_wiki_tuple_list_for_search_body_query(query: str, index_body, n: int=100) -> list:
    """
        Func that search the query in the body of wiki's pages
    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body
        n: size of the return list
    Returns:
        list: list of tuples (wiki_id, wiki_title) , the size of list is n.
    """
    query_list = tokenize(query)

    return []



def cosine_similarity(query: str, index_body)->defaultdict:
    """
    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body
    Returns:
         list: list of tuples (wiki_id, sum_score)
    """
#     first we will calculate the similarities of each document and save in a dictionary
    sim_doc_dictionary = defaultdict(float)
    tokens= tokenize(query)
    counter_words= Counter(tokens)
    # todo maybe we need to add the name of the bucket
    for term_q in tokens:
        posting_list_per_term= read_posting_list(index_body,term_q, "bucket_itamar_body")
        for doc_id, freq in posting_list_per_term:
            sim_doc_dictionary[doc_id] += counter_words[term_q]*freq
    for doc in sim_doc_dictionary:
        sim_doc_dictionary[doc]=sim_doc_dictionary[doc]*(1/index_body.doc_len[doc])*(1/len(query))

            # tf= freq/index_body.DL[doc_id]
            # idf= np.log10(index_body._n/index_body.df[term_q])
            # calc_sim= tf*idf
            # sim_doc_dictionary[doc_id]+=calc_sim
    return sim_doc_dictionary


def bm_25(query:str, index_body, b=0.75, k=0.5)->defaultdict:
    """
    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body
    Returns:
        dictionary of bm25 scores
    """
    tokens = tokenize(query)
    dict_scores= defaultdict(float)
    dict_idf= calc_idf(index_body,tokens)
    bm_25=0.0
    sum=0
    for doc_id in index_body.doc_len:
        sum+=index_body.doc_len[doc_id]
    avgdl= sum/index_body.n
    for token in tokens:
        posting_list_per_term = read_posting_list(index_body, token, "bucket_itamar_body")
        try:
            for doc_id,freq in posting_list_per_term:
                numerator = dict_idf[token] * freq * (k + 1)
                denominator = freq + k * (1 - 0.75 + b * index_body.doc_len[doc_id] / avgdl)
                dict_scores[doc_id] += numerator / denominator
        except:
            continue
    return dict_scores



def calc_idf(inverted_body, list_of_tokens):
    """
    This function calculate the idf values according to the BM25 idf formula for each term in the query.
    Parameters:
    -----------
    query: list of token representing the query. For example: ['look', 'blue', 'sky']
    Returns:
    -----------
    idf: dictionary of idf scores. As follows:
                                                key: term
                                                value: bm25 idf score
    """
    idf = {}
    for term in list_of_tokens:
        if term in inverted_body.df.keys():
            n_ti = inverted_body.df[term]
            idf[term] = math.log(1 + (inverted_body.n - n_ti + 0.5) / (n_ti + 0.5))
        else:
            pass
    return idf

def _score(inverted_body, query, doc_id,avgdl):
    """
    This function calculate the bm25 score for given query and document.
    Parameters:
    -----------
    query: list of token representing the query. For example: ['look', 'blue', 'sky']
    doc_id: integer, document id.
    Returns:
    -----------
    score: float, bm25 score.
    """
    score = 0.0
    doc_len = inverted_body.doc_len[str(doc_id)]
    for term in query:
        if term in inverted_body.term_total.keys():
            # todo ask itamar
            term_frequencies = dict(inverted_body.pls[inverted_body.words.index(term)])
            if doc_id in term_frequencies.keys():
                freq = term_frequencies[doc_id]
                numerator = inverted_body.idf[term] * freq * (0.5+ 1)
                denominator = freq + 0.5 * (1 - 0.75 + 0.75 * doc_len / avgdl)
                score += (numerator / denominator)
    return score
