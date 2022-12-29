

def get_pagerank_of_wiki_pages(wiki_ids: list[int], page_rank_dict) -> list:
    """
        Func that calculate for each wiki id the PageRank score
    Args:
        page_rank_dict: dict that contain the wiki id and the pageview
        wiki_ids: list[int] represent the id of each wiki id page

    Returns: list of PageRank scores correspond to the provided wiki id

    """
    return [page_rank_dict[wi_id] for wi_id in wiki_ids]
