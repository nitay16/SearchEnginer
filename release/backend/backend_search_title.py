from collections import Counter
from backend.common_func import tokenize, read_posting_list


def get_wiki_tuple_list_for_search_title_query(query: str, index_title) -> list:
    """
        Func that search the query in the title of wiki's pages
    Args:
        query: string that represent the query like : "best marvel movie"
        index_title:InverterIndex of the title

    Returns:
        list: list of tuples order [(wiki_id_1, wiki_title_1), ..., (wiki_id_n, wiki_title_n)]
    """
    query_list = tokenize(query)
    counter_score = Counter() # -> key[wiki_id] - value = socre -> Counter().most_common() -> [wiki_id_1 , .. ,wiki_id_n]
    for token in query_list:
        for doc_id, score_tf in read_posting_list(index_title, token, 'fishing-engine-search-title'):
            counter_score[(doc_id, index_title.title[doc_id])] += score_tf
    return [key[0] for key in counter_score.most_common()]


def get_wiki_tuple_list_for_search_title_query_binary_mode(query: str, index_title) -> list:
    """
      func that check for relevent doc how mach of the terms in query return
    Args:
        query: string that represent the query like : "best marvel movie"
        index_title:InverterIndex of the title

    Returns:
        list: list of tuples  (wiki_id , score)
    """
    query_list = tokenize(query)
    counter_score = Counter() # -> key[wiki_id] - value = socre -> Counter().most_common() -> [wiki_id_1 , .. ,wiki_id_n]
    for token in query_list:
            if token in index_title.df:
                for each_pair in read_posting_list(index_title, token, 'fishing-engine-search-title'):
                    counter_score[each_pair[0]] += 1
    return counter_score.most_common(100)


