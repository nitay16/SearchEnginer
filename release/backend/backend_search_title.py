from collections import Counter
from common_func import tokenize, read_posting_list


def get_wiki_tuple_list_of_search_title_query(query: str, index_title) -> list:
    """
        Func that search the query in the title of wiki's pages
    Args:
        query: string that represent the query like : "best marvel movie"

    Returns:
        list: list of tuples order [(wiki_id_1, wiki_title_1), ..., (wiki_id_n, wiki_title_n)]
    """
    query_list = tokenize(query)
    counter_score = Counter() # -> key[wiki_id] - value = socre -> Counter().most_common() -> [wiki_id_1 , .. ,wiki_id_n]
    for token in query_list:
        for doc_id, score_tf in read_posting_list(index_title, token):
            counter_score[(doc_id, index_title.title[doc_id])] += score_tf
    return [key[0] for key in counter_score.most_common()]

