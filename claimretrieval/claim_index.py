"""
Methods for constructing an index of word: {doc_id: frequency} structure
"""


def category_index(category, file_path="../RumourDatabase.csv"):
    """
    :param file_path: path to CSV file of claims
    :param category: category to filter to
    :return: an index of word keys and {doc_id: frequency} dictionary values
    """
    # Read CSV lines
    claims = parse_claims(file_path)  # List of {doc_id, content, category}

    # Filter for category
    claims = [claim for claim in claims if claim.category == category]

    # For each claim, count word frequencies
    claim_words = [count_words(claim) for claim in claims]  # List of {doc_id: {word: frequency}}

    # Collect set of all words
    words = unique_words(claim_words)  # Set of unique words

    # For each word, collect frequency of each doc
    index = {}
    for word in words:
        index[word] = claim_word_frequencies(claim_words, word)  # Dictionary of {doc_id: frequency} for given word

    return index


def parse_claims(file_path):
    """ Return list of {doc_id, content, category} dictionaries """
    return []


def count_words(claim):
    """
    :param claim: dictionary of {doc_id, content, category}
    :return: dictionary of {doc_id: {word: frequency}}
    """
    return {}


def unique_words(claim_words):
    """
    :param claim_words: list of {doc_id: {word: frequency}}
    :return: set of unique words
    """
    return set()


def claim_word_frequencies(claim_words, word):
    """
    :param claim_words: list of {doc_id: {word: frequency}}
    :param word: string
    :return: Dictionary of {doc_id: frequency} for given word
    """
    return {}
