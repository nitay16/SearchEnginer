from collections import Counter
from backend.common_func import tokenize, read_posting_list


def get_wiki_tuple_list_for_search_anchor_query(query: str, index_anchor) -> list:
    """
        Func that search the query in the anchors of wiki's pages
    Args:
        index_anchor:InverterIndex of the anchor
        query: string that represent the query like : "best marvel movie"
    Returns:
        list: list of tuples (wiki_id, wiki_title)
    """
    query_list = tokenize(query)
    counter_score = Counter() # -> key[wiki_id] - value = socre -> Counter().most_common() -> [wiki_id_1 , .. ,wiki_id_n]
    for token in query_list:
        for doc_id, score_tf in read_posting_list(index_anchor, token, 'fishing-engine-search-anchor'):
            counter_score[(doc_id, index_anchor.title[doc_id])] += score_tf
    return [key[0] for key in counter_score.most_common()]


def get_wiki_tuple_list_for_search_anchor_query_binary_mode(query: str, index_anchor) -> list:
    """
      func that check for relevent doc how mach of the terms in query return
    Args:
        query: string that represent the query like : "best marvel movie"
        index_anchor:InverterIndex of the anchor

    Returns:
        list: list of tuples (wiki_id, score)
    """
    query_list = tokenize(query)
    counter_score = Counter() # -> key[wiki_id] - value = socre -> Counter().most_common() -> [wiki_id_1 , .. ,wiki_id_n]
    for token in query_list:
            if token in index_anchor.df:
                for each_pair in read_posting_list(index_anchor, token, 'fishing-engine-search-anchor'):
                    counter_score[each_pair[0]] += 1
    return counter_score.most_common(100)
