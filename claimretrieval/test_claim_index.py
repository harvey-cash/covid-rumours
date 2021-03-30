import unittest
from claimretrieval.claim_index import *


class MyTestCase(unittest.TestCase):

    def test_parse_claims(self):
        claims = parse_claims("./TestRumourCSV.csv")
        expected = []
        self.assertEqual(expected, claims)

    def test_count_words(self):
        claim = {"doc_id": 100, "content": "a", "category": "other"}
        word_count = count_words(claim)
        expected = {100: {"a": 1}}
        self.assertEqual(expected, word_count)

    def test_unique_words(self):
        words = unique_words([])
        expected = set()
        self.assertEqual(expected, words)

    def test_claim_word_frequencies(self):
        claim_words = []
        word_freqs = claim_word_frequencies(claim_words, "foo")  # Dictionary of {doc_id: frequency} for given word
        expected = {"foo": {100: 1}}
        self.assertEqual(expected, word_freqs)


if __name__ == '__main__':
    unittest.main()
