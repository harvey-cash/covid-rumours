
from unittest import TestCase
from claimretrieval.retriever import *


class Test(TestCase):

    def test_resolve_query(self):
        retriever = Retriever({})

        # Test empty
        result = retriever.shortlist({})
        self.assertEqual([], result)

        # Test simple
        query = {'a': 1}
        index = {'a': {100: 1, 102: 2}, 'b': {101: 1}}
        expected = [100, 102]
        retriever = Retriever(index)
        result = retriever.shortlist(query)
        self.assertEqual(expected, result)

    def test_prune_docs(self):
        # Test empty
        result = prune_docs({}, {})
        self.assertEqual(set(), result)

        # Test simply
        query = {'a': 1, 'b': 1}
        index = {'a': {100: 1, 102: 2}, 'b': {100: 2, 103: 1}, 'c': {104: 1}}
        expected = {100, 102, 103}
        result = prune_docs(query, index)
        self.assertEqual(expected, result)

    def test_count_claims(self):
        # Test empty
        result = count_claims({})
        self.assertEqual(0, result)

        # Test simple
        index = {'a': {100: 5}, 'b': {100: 0, 101: 2}}
        expected = 2
        result = count_claims(index)
        self.assertEqual(expected, result)

    def test_prune_query(self):
        # Test empty
        result = prune_query({}, {})
        self.assertEqual({}, result)

        # Test simple
        query = {'a': 2, 'b': 0, 'notinindex': 1}
        index = {'a': {100: 5}, 'b': {100: 0, 101: 2}, 'c': {101: 1}}
        expected = {'a': 2, 'b': 0}
        result = prune_query(query, index)
        self.assertEqual(expected, result)

    def test_index_frequency(self):
        # Test not present
        word = "fathom"
        index = {'a': {100: 1}}
        expected = 0
        result = index_frequency(word, index)
        self.assertEqual(expected, result)

        # Test present
        index = {'a': {100: 1}, 'fathom': {100: 2, 101: 1}}
        expected = 2
        result = index_frequency(word, index)
        self.assertEqual(expected, result)

    def test_tf_idf(self):
        docs_with_term = 1
        t_frequency = 5
        doc_count = 2
        expected = 3.4657
        result = tf_idf(t_frequency, doc_count, docs_with_term)
        self.assertAlmostEqual(expected, result, places=4)

    def test_query_weighting(self):
        # Test empty
        result = weight_query({}, {}, 0)
        self.assertEqual({}, result)

        query = {'a': 2, 'b': 0}
        index = {'a': {100: 5}, 'b': {100: 0, 101: 2}}
        doc_count = 2

        # Test TFIDF
        expected = {'a': 2*math.log(2/1), 'b': 0}
        result = weight_query(query, index, doc_count)
        self.assertEqual(expected, result)

    def test_index_weighting(self):
        # Test empty
        result = weight_index({}, 0)
        self.assertEqual({}, result)

        index = {'a': {100: 5}, 'b': {100: 0, 101: 2}}
        doc_count = 2

        # Test TFIDF
        expected = {'a': {100: 5 * math.log(2/1)}, 'b': {100: 0, 101: 2 * math.log(2/2)}}
        result = weight_index(index, doc_count)
        self.assertEqual(expected, result)

    def test_cosine_similarity(self):
        # Test empty
        result = cosine_similarity({}, {})
        self.assertEqual({}, result)

        # Simple test
        query = {'a': 1, 'notinindex': 0}
        index = {'a': {100: 1, 101: 1}, 'b': {100: 1}}
        expected = {100: 1 / math.sqrt(2), 101: 1}
        result = cosine_similarity(query, index)
        self.assertEqual(expected, result)

    def test_sort_dict(self):
        # Test empty
        result = sort_dict({})
        self.assertEqual([], result)

        # Test ascending
        dictionary = {'a': 12, 'b': 80, 'c': -1}
        expected = [('c', -1), ('a', 12), ('b', 80)]
        result = sort_dict(dictionary, descending=False)
        self.assertEqual(expected, result)

        # Test descending
        expected = [('b', 80), ('a', 12), ('c', -1)]
        result = sort_dict(dictionary, descending=True)
        self.assertEqual(expected, result)