import math

RETURN_COUNT = 10


class Retriever:
    """
    This class is responsible for retrieving a shortlist of the most relevant claims for a given tweet
    Category should be filtered and bag of words index / query must be constructed prior to using this class
    Class should be constructed once and then "shortlist" called for each tweet
    """

    def __init__(self, index):
        """
        :param index: dictionary of word keys and {doc_id: frequency} dictionary values
        """
        self.index = index
        self.total_claims = count_claims(index)
        self.weighted_index = weight_index(index, self.total_claims)  # Pre-process index

    def shortlist(self, query):
        """
        :param query: dictionary of word keys and integer frequency values
        :param self
            index: dictionary of word keys and dictionaries of {doc_id: frequency} values
        :return: array of document indices deemed relevant (in descending order)
        """
        # Prune the query to only include terms found in the index
        pruned_query = prune_query(query, self.index)

        # Adjust frequencies depending on weighting scheme
        weighted_query = weight_query(pruned_query, self.index, self.total_claims)

        # Calculate cosine document-query similarity for all documents
        doc_similarities = cosine_similarity(weighted_query, self.weighted_index)

        descending_similarities = sort_dict(doc_similarities, descending=True)
        descending_docs = [doc for (doc, sim) in descending_similarities]

        # Not doing PRF, simply return (limited) list of descending docs
        return descending_docs[0:RETURN_COUNT + 1]


def count_claims(index):
    """
    :param index: dictionary of word keys and {doc_id: frequency} dictionary values
    :return: the number of unique doc IDs in the index
    """
    docs = {}
    count = 0
    for doc_dict in index.values():
        for doc_id in doc_dict.keys():
            if doc_id not in docs:
                docs[doc_id] = 1
                count += 1
    return count


def weight_query(query, index, doc_count):
    """
    :param query: dictionary of word keys and integer frequency values
    :param index: dictionary of word keys and {doc_id: frequency} dictionary values
    :param doc_count: Number of docs in the index
    :return: a modified query using the given weighting scheme
    """
    # Use TF.IDF weighting. Loop works out slightly faster here
    weighted_query = {}
    for word, frequency in query.items():
        # Find number of docs that contain term
        docs_with_term = index_frequency(word, index)
        weighted_query[word] = tf_idf(frequency, doc_count, docs_with_term)

    return weighted_query


def weight_index(index, doc_count):
    """
    :param index: dictionary of word keys and {doc_id: frequency} dictionary values
    :param doc_count: Number of docs in the index
    :return: a modified index using TFIDF
    """
    weighted_index = {}

    # Apply weighting for each term, for each document
    # Loops here are more readable than nested dictionary comprehensions
    for word, doc_dict in index.items():
        docs_with_term = index_frequency(word, index)

        # Add word to new index
        weighted_index[word] = {}

        for doc_id, frequency in doc_dict.items():
            weighted_index[word][doc_id] = tf_idf(frequency, doc_count, docs_with_term)

    return weighted_index


def tf_idf(term_frequency, doc_count, docs_with_term):
    """ tf * log(|D| / df) """
    inverse_d_frequency = math.log(doc_count / docs_with_term)
    return term_frequency * inverse_d_frequency


def index_frequency(word, index):
    """ In how many documents does a word appear? """
    count = 0
    if word in index:
        count += len(index[word].keys())
    return count


def prune_query(query, index):
    """ :return: query that contains only the terms found in the index """
    return {word: frequency for word, frequency in query.items() if word in index}


def sort_dict(dictionary, descending=True):
    """
    :param dictionary: of format {key: numerical value}
    :param descending: sort direction
    :return: sorted list of (key, value) tuples
    """
    return sorted(list(dictionary.items()), key=lambda pair: pair[1], reverse=descending)


def cosine_similarity(query, index):
    """ :return: dictionary of {doc_id: cosine similarity} """
    # Prune down to only docs that have words in common with query
    pruned_docs = prune_docs(query, index)
    # sqrt(sum of squares) size for each doc
    doc_sizes = size_of_docs(index)

    doc_similarities = {}
    # For each document
    for doc_id in pruned_docs:
        # Find the sum of q_f * d_f for each frequency f in the set of terms
        sum_of_products = 0
        for word, q_frequency in query.items():
            # If product will be zero, skip
            if word not in index:
                continue
            elif doc_id not in index[word]:
                continue
            # Otherwise, calculate and add to sum
            else:
                d_frequency = index[word][doc_id]
                sum_of_products += q_frequency * d_frequency

        # We omit query_size as it doesn't affect ranking order
        similarity = sum_of_products / doc_sizes[doc_id]
        doc_similarities[doc_id] = similarity

    return doc_similarities


def prune_docs(query, index):
    """ :return: set of unique doc_ids that share words with the query"""
    list_of_lists = [list(index[word].keys()) for word in query.keys() if word in index]
    flattened_list = [val for sublist in list_of_lists for val in sublist]
    return set(flattened_list)


def size_of_docs(index):
    """ :return: dictionary of {doc_id: size} for all docs in index """
    sums_of_squares = {}

    # Find frequency for each term in the query, for each doc
    for word in index:
        for doc_id, frequency in index[word].items():
            if doc_id not in sums_of_squares:
                sums_of_squares[doc_id] = frequency * frequency
            else:
                sums_of_squares[doc_id] += frequency * frequency

    return {doc_id: math.sqrt(sum_squares) for doc_id, sum_squares in sums_of_squares.items()}
