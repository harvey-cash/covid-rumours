import unittest

from datastore import datastore


class MyTestCase(unittest.TestCase):

    def test_load_store(self):
        store = datastore.load_tweet_store()
        self.assertEqual({"testID": {"numericID": 0, "text": "this is a test tweet store", "annotations": []}}, store)

    def test_generate_id(self):
        first = datastore.generate_new_numeric_id()
        second = datastore.generate_new_numeric_id()
        self.assertEqual(first+1, second)

    def test_id_lookup(self):
        self.assertEqual(None, datastore.lookup_tweet_id(200))
        datastore.append_id_lookup(200, "lookup_test")
        self.assertEqual("lookup_test", datastore.lookup_tweet_id(200))

    def test_store_tweet(self):
        tweet_string = '{"tweetID": "test_store_tweet", "text": "#plandemic!"}'
        self.assertEqual("Success!", datastore.store_tweet(tweet_string))
        tweet_string = '{"tweetID": "test_store_tweet", "text": "#plandemic!"}'
        self.assertEqual('Tweet ID test_store_tweet Already in store!', datastore.store_tweet(tweet_string))


if __name__ == '__main__':
    unittest.main()
