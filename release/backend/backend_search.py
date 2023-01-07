from common_func import tokenize


def get_wiki_tuple_list_for_search_query(query: str, n: int=100) -> list:
    """
    # todo add the method that we used in the func
        Func that search in _______
    Args:
        query: string that represent the query like : "best marvel movie"
        n: size of the return list
    Returns:
        list: list of tuples (wiki_id, wiki_title) , the size of list is n.
    """
    query_list = tokenize(query)
    return []
