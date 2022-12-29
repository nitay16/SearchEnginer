

def get_pagerank_of_wiki_pages(wiki_ids: list[int], page_view_dict) -> list:
    """
        Func that calculate for each wiki id the PageView number
    Args:
        page_view_dict: Counter() that contain the wiki id and the pageview
        wiki_ids: list[int] represent the id of each wiki id page

    Returns: list of PageView number correspond to the provided wiki id

    """
    return [page_view_dict[wi_id] for wi_id in wiki_ids]

