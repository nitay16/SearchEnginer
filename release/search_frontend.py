from flask import Flask, request, jsonify
from backend import backend_search, backend_search_body, backend_search_title, backend_search_anchor, \
    backend_get_pagerank, backend_get_pageview
from backend.common_func import read_pkl_file_form_bucket
import numpy as np
from collections import Counter, defaultdict


class MyFlaskApp(Flask):
    def run(self, host=None, port=None, debug=None, **options):
        super(MyFlaskApp, self).run(host=host, port=port, debug=debug, **options)


app = MyFlaskApp(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Global for indexing
page_view_index = read_pkl_file_form_bucket("pageview/pageviews-202108-user", 'bucket_itamar')
page_rank_index = read_pkl_file_form_bucket("pagerank/page_rank", 'bucket_itamar')
search_title_index = read_pkl_file_form_bucket("postings_gcp/index_title", 'bucket_itamar_title')
search_body_index = read_pkl_file_form_bucket("postings_gcp/index_body", 'bucket_itamar_body')
search_body_index.doc_len = read_pkl_file_form_bucket("dict_help/doc_len", 'bucket_itamar_body')
search_anchor_index = read_pkl_file_form_bucket("postings_gcp/index_anchor", 'bucket_itamar_anchor')
avgdl = np.sum(list(search_body_index.doc_len.values())) / len(list(search_body_index.doc_len.values()))
search_body_index.idf_norm = read_pkl_file_form_bucket("dict_help/dict_norm_list", 'bucket_itamar_body')

# union of dictionaries
dic_union_norm=defaultdict(float)
for i in search_body_index.idf_norm:
    for key in i:
        dic_union_norm[key]=i[key][1]

search_body_index.idf_norm = dic_union_norm

@app.route("/search")
def search():
    """ Returns up to a 100 of your best search results for the query. This is
        the place to put forward your best search engine, and you are free to
        implement the retrieval whoever you'd like within the bound of the
        project requirements (efficiency, quality, etc.). That means it is up to
        you to decide on whether to use stemming, remove stopwords, use
        PageRank, query expansion, etc.

        To issue a query navigate to a URL like:
         http://YOUR_SERVER_DOMAIN/search?query=hello+world
        where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of up to 100 search results, ordered from best to worst where each
        element is a tuple (wiki_id, title).
    """
    query = request.args.get('query', '')
    if len(query) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = (backend_search.get_wiki_tuple_list_for_search_query(query, search_body_index, search_title_index,
                                                                   search_anchor_index, page_rank_index, avgdl, 100))
    app.logger.info("The results of the query: " + query + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


@app.route("/search_body")
def search_body():
    """ Returns up to a 100 search results for the query using TFIDF AND COSINE
        SIMILARITY OF THE BODY OF ARTICLES ONLY. DO NOT use stemming. DO USE the
        staff-provided tokenizer from Assignment 3 (GCP part) to do the
        tokenization and remove stopwords.

        To issue a query navigate to a URL like:
         http://YOUR_SERVER_DOMAIN/search_body?query=hello+world
        where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of up to 100 search results, ordered from best to worst where each
        element is a tuple (wiki_id, title).
    """
    query = request.args.get('query', '')
    if len(query) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = (backend_search_body.get_wiki_tuple_list_for_search_body_query(query, search_body_index, search_title_index, 100))
    app.logger.info("The results of the query: " + query + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


@app.route("/search_title")
def search_title():
    """ Returns ALL (not just top 100) search results that contain A QUERY WORD
        IN THE TITLE of articles, ordered in descending order of the NUMBER OF
        QUERY WORDS that appear in the title. For example, a document with a
        title that matches two of the query words will be ranked before a
        document with a title that matches only one query term.

        Test this by navigating to the a URL like:
         http://YOUR_SERVER_DOMAIN/search_title?query=hello+world
        where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of ALL (not just top 100) search results, ordered from best to
        worst where each element is a tuple (wiki_id, title).
    """
    query = request.args.get('query', '')
    if len(query) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = backend_search_title.get_wiki_tuple_list_for_search_title_query(query, search_title_index)
    app.logger.info("The results of the query: " + query + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


@app.route("/search_anchor")
def search_anchor():
    """ Returns ALL (not just top 100) search results that contain A QUERY WORD
        IN THE ANCHOR TEXT of articles, ordered in descending order of the
        NUMBER OF QUERY WORDS that appear in anchor text linking to the page.
        For example, a document with a anchor text that matches two of the
        query words will be ranked before a document with anchor text that
        matches only one query term.

        Test this by navigating to the a URL like:
         http://YOUR_SERVER_DOMAIN/search_anchor?query=hello+world
        where YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of ALL (not just top 100) search results, ordered from best to
        worst where each element is a tuple (wiki_id, title).
    """
    query = request.args.get('query', '')
    if len(query) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = backend_search_anchor.get_wiki_tuple_list_for_search_anchor_query(query, search_anchor_index)
    app.logger.info("The results of the query: " + query + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


@app.route("/get_pagerank", methods=['POST'])
def get_pagerank():
    """ Returns PageRank values for a list of provided wiki article IDs.
        Test this by issuing a POST request to a URL like:
          http://YOUR_SERVER_DOMAIN/get_pagerank
        with a json payload of the list of article ids. In python do:
          import requests
          requests.post('http://YOUR_SERVER_DOMAIN/get_pagerank', json=[1,5,8])
        As before YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of floats:
          list of PageRank scores that correspond to the provided article IDs.
    """
    wiki_ids = request.get_json()
    if len(wiki_ids) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = backend_get_pagerank.get_pagerank_of_wiki_pages(wiki_ids, page_rank_index)
    app.logger.info("The results of the wiki_ids: " + str(wiki_ids) + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


@app.route("/get_pageview", methods=['POST'])
def get_pageview():
    """ Returns the number of page views that each of the provide wiki articles
        had in August 2021.

        Test this by issuing a POST request to a URL like:
          http://YOUR_SERVER_DOMAIN/get_pageview
        with a json payload of the list of article ids. In python do:
          import requests
          requests.post('http://YOUR_SERVER_DOMAIN/get_pageview', json=[1,5,8])
        As before YOUR_SERVER_DOMAIN is something like XXXX-XX-XX-XX-XX.ngrok.io
        if you're using ngrok on Colab or your external IP on GCP.
    Returns:
    --------
        list of ints:
          list of page view numbers from August 2021 that correspond to the
          provided list article IDs.
    """
    wiki_ids = request.get_json()
    if len(wiki_ids) == 0:
        app.logger.info("The input was empty")
        return jsonify([])
    results = backend_get_pageview.get_pagerank_of_wiki_pages(wiki_ids, page_view_index)
    app.logger.info("The results of the wiki_ids: " + str(wiki_ids) + " , the 10 results are: " + str(results[:10]))
    return jsonify(results)


if __name__ == '__main__':
    # run the Flask RESTful API, make the server publicly available (host='0.0.0.0') on port 8080
    app.run(host='0.0.0.0', port=8080, debug=True)
