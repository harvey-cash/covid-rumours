import unittest

from datastore import datastore, annotation_parser


class MyTestCase(unittest.TestCase):

    def test_load_store(self):
        store = datastore.load_tweet_store()
        self.assertEqual({"testID": {"numericID": 1, "text": "this is a test tweet store", "annotations": []}}, store)

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

    def test_add_annotations(self):
        annotation_dict = {"participantID": 0, "category": "MEDICAL", "veracity": "TRUE", "rumourID": 0}
        response = datastore.add_annotations(0, annotation_dict)
        self.assertEqual("Tweet with numeric ID 0 not found in datastore id lookup!", response)
        response = datastore.add_annotations(1, annotation_dict)
        self.assertEqual("Success!", response)

    def test_annotation_parser(self):
        file_path = "../../Annotations/Annotation Test Form_11SK8qCyvDyrrZfT8Hk6P4Er8yBPLpDgTXN4id6hpg6I_responses - Form Responses 1.tsv"
        expected = [
            {
                "participantID": 1,
                "annotations": [
                    {"numericTweetID": 112, "category": "Virus Transmission", "rumourID": "Other: Claim not listed"},
                    {"numericTweetID": 201, "category": "Medical Advice", "rumourID": 15}
                ]
            },
            {
                "participantID": 10,
                "annotations": [
                    {"numericTweetID": 201, "category": "Medical Advice", "rumourID": 101}
                ]
            },
            {
                "participantID": 12,
                "annotations": [
                    {"numericTweetID": 112, "category": "Virus Transmission", "rumourID": 3}
                ]
            }
        ]
        self.assertEqual(expected, annotation_parser.load_annotation_file(file_path))

    def test_load_files(self):
        result = annotation_parser.load_annotation_files()
        expected = [[
            {
                "participantID": 1,
                "annotations": [
                    {"numericTweetID": 112, "category": "Virus Transmission", "rumourID": "Other: Claim not listed"},
                    {"numericTweetID": 201, "category": "Medical Advice", "rumourID": 15}
                ]
            },
            {
                "participantID": 10,
                "annotations": [
                    {"numericTweetID": 201, "category": "Medical Advice", "rumourID": 101}
                ]
            },
            {
                "participantID": 12,
                "annotations": [
                    {"numericTweetID": 112, "category": "Virus Transmission", "rumourID": 3}
                ]
            }
        ]]
        self.assertEqual(expected, result)

    def test_parse_header(self):
        header = "Timestamp\tEmail Address\tParticipant ID\tTweet #200: Category\tTweet #200: Claim Identification\tTweet #11: Category\tTweet #11: Claim Identification"
        result = annotation_parser.parse_header_string(header)
        self.assertEqual([200, 11], result)

    def test_parse_line(self):
        line = "3/18/2021 6:25:48\t\t1\tVirus Transmission\tOther: Claim not listed\tMedical Advice\tClaim #15: 5G towers contribute to the spread of Coronavirus"
        result = annotation_parser.parse_line(line)
        expected = (1, [("Virus Transmission", "Other: Claim not listed"), ("Medical Advice", 15)])
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
