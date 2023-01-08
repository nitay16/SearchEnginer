import numpy as np

from common_func import tokenize
from common_func import read_posting_list

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



def cosine_similarity(query: str, index_body)->list:
    """

    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body

    Returns:
         list: list of tuples (wiki_id, sum_score)

    """
#     first we will calculate the similarities of each document and save in a dictionary
    sim_doc_dictionary={}
    # todo maybe we need to add the name of the bucket
    for term_q in query:
        posting_list_per_term= read_posting_list(index_body,term_q)
        for doc_id, freq in posting_list_per_term:
            tf= freq/index_body.DL[doc_id]
            idf= np.log10(index_body._n/index_body.df[term_q])
            calc_sim= tf*idf
            sim_doc_dictionary[doc_id]+=calc_sim


