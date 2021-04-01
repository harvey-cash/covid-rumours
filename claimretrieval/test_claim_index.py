import unittest
from claimretrieval.claim_index import *


class MyTestCase(unittest.TestCase):

    def test_category_index(self):
        index = category_index("Virus origin and properties", "./TestRumourCSV.csv")
        expected = {
            "covid": {0: 1, 1: 1},
            "wuhan": {0: 1},
            "china": {0: 1},
            "reported": {1: 1},
            "2019": {1: 1}
        }
        self.assertEqual(expected, index)

    def test_parse_claims(self):
        claims = parse_claims("./TestRumourCSV.csv")
        expected = [
            {"doc_id": 0, "content": "covid wuhan china", "category": "Virus origin and properties"},
            {"doc_id": 1, "content": "covid reported 2019", "category": "Virus origin and properties"}
        ]
        self.assertEqual(expected, claims)

    def test_count_words(self):
        claim = {"doc_id": 100, "content": "a", "category": "other"}
        word_count = count_words(claim)
        expected = {100: {"a": 1}}
        self.assertEqual(expected, word_count)

    def test_unique_words(self):
        words = unique_words([
            {100: {"a": 1}},
            {101: {"a": 2, "b": 1, "c": 1}},
            {102: {"c": 1, "a": 1, "d": 1}}
        ])
        expected = {"a", "b", "c", "d"}
        self.assertEqual(expected, words)

    def test_claim_word_frequencies(self):
        claim_words = [{100: {"bar": 1, "foo": 1}}, {101: {"foo": 2, "bar": 3}}]
        word_freqs = claim_word_frequencies(claim_words, "foo")  # Dictionary of {doc_id: frequency} for given word
        expected = {100: 1, 101: 2}
        self.assertEqual(expected, word_freqs)


if __name__ == '__main__':
    unittest.main()
