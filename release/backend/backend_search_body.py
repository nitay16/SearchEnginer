from common_func import tokenize


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
