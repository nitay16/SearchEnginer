from common_func import tokenize


def get_wiki_tuple_list_of_search_title_query(query: str) -> list:
    """
        Func that search the query in the title of wiki's pages
    Args:
        query: string that represent the query like : "best marvel movie"

    Returns:
        list: list of tuples (wiki_id, wiki_title)
    """
    query_list = tokenize(query)
    return []
