import math
from collections import defaultdict, Counter

from backend.common_func import tokenize
from backend.common_func import read_posting_list

def get_wiki_tuple_list_for_search_body_query(query: str, index_body,index_title, n: int=100) -> list:
    """
        Func that search the query in the body of wiki's pages
    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body
        n: size of the return list
    Returns:
        list: list of tuples (wiki_id, wiki_title) , the size of list is n.
    """

    #     first we will calculate the similarities of each document and save in a dictionary
    sim_doc_dictionary = defaultdict(float)
    list_of_tokens = tokenize(query)
    q_len = len(list_of_tokens)
    counter_terms_q = Counter()
    for i in list_of_tokens:
        counter_terms_q[i] += 1

    dict_tf_idf_query = defaultdict(float)
    for term in list_of_tokens:
        try:
            tf_q = counter_terms_q[term] / q_len
            idf = math.log10(index_body.n / index_body.df[term])
            tf_idf_query = tf_q * idf
            dict_tf_idf_query[term] = tf_idf_query
        except:
            continue
    squer_idf_query = 0
    for term in dict_tf_idf_query:
        squer_idf_query += (dict_tf_idf_query[term]) ** 2
    norm_fator_query = math.sqrt(squer_idf_query)
    for term_q in list_of_tokens:
        posting_list_per_term = read_posting_list(index_body, term_q, 'fishing-engine-search-body')
        for doc_id, freq in posting_list_per_term:
            try:
                tf = freq / index_body.doc_len[doc_id]
                tf_q = counter_terms_q[term_q] / q_len
                idf = math.log10(index_body.n / index_body.df[term_q])
                tf_idf_doc = tf * idf
                tf_idf_que = tf_q * idf
                sim_doc_dictionary[(doc_id, index_title.title[doc_id])] += tf_idf_que * tf_idf_doc
            except ZeroDivisionError:
                continue
    for doc, title in sim_doc_dictionary:
        if (doc in index_body.idf_norm):
            normalize_num = index_body.idf_norm[doc]
            try:
                sim_doc_dictionary[(doc, title)] = sim_doc_dictionary[(doc, title)] * (1 / norm_fator_query) * (
                            1 / normalize_num)

            except ZeroDivisionError:
                continue
    sorted_dictionary = sorted(dict(sim_doc_dictionary).keys(), key=lambda x: sim_doc_dictionary[x], reverse=True)[:100]
    return sorted_dictionary



