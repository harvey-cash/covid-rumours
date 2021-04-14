"""
Methods for constructing an index of word: {doc_id: frequency} structure
"""
import pandas as pd
from utils import preprocess_text


def category_index(category, file_path="../RumourDatabase.csv"):
    """
    :param file_path: path to CSV file of claims
    :param category: category to filter to
    :return: an index of word keys and {doc_id: frequency} dictionary values
    """
    # Read CSV lines
    claims = parse_claims(file_path)  # List of {doc_id, content, category}

    # Filter for category
    claims = [claim for claim in claims if claim['category'] == category]

    # Remove stop-words, punctuation, etc.
    claims = [clean_preprocess(claim) for claim in claims]

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
    df = pd.read_csv(file_path)
    df.dropna(axis='columns', how='all', inplace=True)  # Drop any columns that are all N/A
    df.dropna(axis='index', how='any', inplace=True)  # Drop any rows that have at least one N/A
    return [{"doc_id": int(row['Index']), "content": row['Claim'], "category": row['Category']} for i, row in df.iterrows()]


def clean_preprocess(claim):
    """ Clean string of punctuation, stop words, etc.
    :param claim: dictionary of {doc_id, content, category}
    """
    claim['content'] = preprocess_text.clean_all(claim['content'])
    return claim


def count_words(claim):
    """
    :param claim: dictionary of {doc_id, content, category}
    :return: dictionary of {doc_id: {word: frequency}}
    """
    words = claim['content'].split(' ')  # Split words
    frequencies = {word: len([w for w in words if w == word]) for word in words}
    return {claim['doc_id']: frequencies}


def unique_words(claim_words):
    """
    :param claim_words: list of {doc_id: {word: frequency}}
    :return: set of unique words
    """
    words = set()
    for claim_dict in claim_words:
        words_dict = list(claim_dict.values())[0]
        words = words.union(words_dict.keys())
    return words


def claim_word_frequencies(claim_words, word):
    """
    :param claim_words: list of {doc_id: {word: frequency}}
    :param word: string
    :return: Dictionary of {doc_id: frequency} for given word
    """
    word_freqs = {}
    for claim in claim_words:
        doc_id = list(claim.keys())[0]
        frequency = list(claim.values())[0].get(word, 0)

        if frequency > 0:
            word_freqs[doc_id] = frequency

    return word_freqs
