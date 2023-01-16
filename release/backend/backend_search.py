import math
from collections import Counter, defaultdict

from backend.common_func import tokenize , read_posting_list
from backend.backend_search_title import get_wiki_tuple_list_for_search_title_query_binary_mode


def get_dict_of_tf_per_term(terms, search_body_index):
    dict_return = Counter()
    for term in terms:
        if term in search_body_index.df:
            for doc_id, score_tf in read_posting_list(search_body_index, term, "fishing-engine-search-body"):
                dict_return.setdefault(doc_id, {})[term] = score_tf
    return dict_return


def get_query_tf_per_term(query):
    dict_return = Counter()
    for term in query:
        dict_return[term] += 1
    k3 = 0.5
    vals = {}
    for term in dict_return:
        vals[term] = ((k3 + 1) * dict_return[term]) / (k3 + dict_return[term])
    return dict_return


def calc_idf(term, search_body_index):
    # if the term in the doc
    df_n = 0
    if term in search_body_index.df:
        df_n = search_body_index.df[term]
    return math.log(search_body_index.n + 1 / (df_n))


def get_BM_25_resutls_Counter(terms, avgdl, search_body_index):
    relevent_doc_and_tf = get_dict_of_tf_per_term(terms, search_body_index)
    query_k3_section_val = get_query_tf_per_term(terms)
    docs = list(relevent_doc_and_tf.keys())
    dict_return = Counter()
    b = 0.75
    k1 = 1
    for doc in docs:
        score = 0.0
        B = (1 - b + (b * (search_body_index.doc_len[doc] / avgdl)))
        for term in terms:
            tf_origin = 1
            section_1 = 1
            section_2 = 1
            if term in relevent_doc_and_tf[doc]:
                tf_origin = relevent_doc_and_tf[doc][term]
                section_1 = ((k1 + 1) * tf_origin) / ((B * k1) + tf_origin)
                section_2 = calc_idf(term, search_body_index)
            section_3 = query_k3_section_val[term]
            score += section_1 * section_2 * section_3

        dict_return[doc] = score
    return dict_return.most_common(100)


def cosine_similarity(query: str, index_body) -> list:
    """

    Args:
        query: string that represent the query like : "best marvel movie"
        index_body: InverterIndex of index_body

    Returns:
         list: list of tuples (wiki_id, sum_score)

    """
    #     first we will calculate the similarities of each document and save in a dictionary
    sim_doc_dictionary = defaultdict(float)
    list_of_tokens = query
    counter_terms_q = Counter()
    for i in list_of_tokens:
        counter_terms_q[i] += 1
    q_len = len(list_of_tokens)
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
        posting_list_per_term = read_posting_list(index_body, term_q, "fishing-engine-search-body")
        for doc_id, freq in posting_list_per_term:
            try:
                tf = freq / index_body.doc_len[doc_id]
                tf_q = counter_terms_q[term_q] / q_len
                idf = math.log10(index_body.n / index_body.df[term_q])
                tf_idf_doc = tf * idf
                tf_idf_que = tf_q * idf
                sim_doc_dictionary[doc_id] += tf_idf_que * tf_idf_doc
            except ZeroDivisionError:
                continue
    for doc in sim_doc_dictionary:
        if (doc in index_body.idf_norm):
            normalize_num = index_body.idf_norm[doc]
            try:
                sim_doc_dictionary[doc] = sim_doc_dictionary[doc] * (1 / norm_fator_query) * (1 / normalize_num)
            except ZeroDivisionError:
                continue
    sorted_dictionary = sorted(dict(sim_doc_dictionary).items(), key=lambda x: x[1], reverse=True)[:100]
    return sorted_dictionary


def merge_results(title_scores, body_scores, title_weight=0.5, text_weight=0.5, N=100):
    dict_top_n = {}
    query_id = "query_id"
    scores = {}
    # if query_id in title_scores and query_id in body_scores:
    for doc, score in title_scores[query_id]:
        scores[doc] = title_weight * score
    for doc, score in body_scores[query_id]:
        if doc in scores:
            scores[doc] += (text_weight * score)
        else:
            scores[doc] = text_weight * score
    dict_top_n[query_id] = sorted([(doc_id, score) for doc_id, score in scores.items()], key=lambda x: x[1],
                                  reverse=True)[:N]

    return dict_top_n


def get_wiki_tuple_list_for_search_query(query: str, index_body, index_title, index_anchor, page_rank, avgdl,n=100) -> list:
    """
    # todo add the method that we used in the func
        Func that search in _______
    Args:
        page_rank: dict that represent the page_rank of each doc
        index_anchor: inverter index of anchor
        index_title:  inverter index of title
        index_body:  inverter index of body
        bm25_dict:
        query: string that represent the query like : "best marvel movie"
        n: size of the return list
    Returns:
        list: list of tuples (wiki_id, wiki_title) , the size of list is n.
    """
    terms = tokenize(query)
    # if the query after tokenze is len one then we want more weight to the title serach
    if len(terms) == 1:
        w1 = 0.9
        w2 = 0.1
        binary_title = get_wiki_tuple_list_for_search_title_query_binary_mode(query, index_title)
        max_val_title = binary_title[0][1]
        binary_title = [(pair[0], pair[1] / max_val_title) for pair in binary_title]
        binary_title_dict = {"query_id": binary_title}
        cosim_body = cosine_similarity(terms, index_body)
        cosim_body_dict = {"query_id": cosim_body}
        merge = merge_results(binary_title_dict, cosim_body_dict, w1, w2)
        return [(pair[0], index_title.title[pair[0]]) for pair in merge["query_id"]][:20]

    if len(terms) >= 2:
        w1 = 0.3
        w2 = 0.7
        binary_title = get_wiki_tuple_list_for_search_title_query_binary_mode(query, index_title)
        max_val_title = binary_title[0][1]
        binary_title = [(pair[0], pair[1] / max_val_title) for pair in binary_title]
        cosim_body = cosine_similarity(terms, index_body)
        binary_title_dict = {"query_id": binary_title}
        cosim_body_dict = {"query_id": cosim_body}
        merge = merge_results(binary_title_dict, cosim_body_dict, w1, w2)
        return [(pair[0], index_title.title[pair[0]]) for pair in merge["query_id"]][:20]

