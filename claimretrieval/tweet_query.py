
from utils import preprocess_text


def construct_query(tweet_string):
    """
    :param tweet_string: string of tweet text
    :return: dictionary of term: frequencies
    """
    # Pre-process
    cleaned_text = preprocess_text.clean_str(tweet_string)
    words = cleaned_text.split(' ')  # Split words
    frequencies = {word: len([w for w in words if w == word]) for word in words}

    return frequencies

