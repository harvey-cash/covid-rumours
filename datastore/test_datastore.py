import unittest

from datastore import annotation_parser


class MyTestCase(unittest.TestCase):

    def test_annotation_parser(self):
        file_path = "../../Annotations/Annotation Test Form_1Xx9SfKG-M7C0v8Hvz-WvZSY_b9LdOjygBr0eBuiueow_responses - Form Responses 1.tsv"
        expected = [
            {
                "participantID": 1,
                "annotations": [
                    {"tweetID": "gioshwsejh32hg39", "category": "Medical Advice", "rumourID": 101},
                    {"tweetID": "q1tusehjsehj9oi3g23", "category": "Community", "rumourID": "Other: Claim not listed"}
                ]
            },
            {
                "participantID": 10,
                "annotations": [
                    {"tweetID": "q1tusehjsehj9oi3g23", "category": "Community", "rumourID": "Other: Claim not listed"}
                ]
            },
            {
                "participantID": 12,
                "annotations": [
                    {"tweetID": "gioshwsejh32hg39", "category": "Virus Transmission", "rumourID": 3}
                ]
            }
        ]
        self.assertEqual(expected, annotation_parser.load_annotation_file(file_path))

        file_path = "../../Annotations/Test_1G5gOX3N8QITNqe0BZHXP3DlK99bcjADWyeeeuMOWSus_responses - Form responses 1.tsv"
        expected = [{
            "participantID": 11,
            "annotations": [
                {"tweetID": "gioshwsejh32hg39", "category": "Virus Transmission", "rumourID": 8},
                {"tweetID": "q1tusehjsehj9oi3g23", "category": "Medical Advice", "rumourID": 15}
            ]
        }]
        self.assertEqual(expected, annotation_parser.load_annotation_file(file_path))

    def test_parse_meta_data(self):
        header = 'Timestamp	Participant ID	Tweet #1: Category	Tweet #1: Claim Identification	Tweet #2: Category	Tweet #2: Claim Identification	{"tweetSample":[{"tweetID":"gioshwsejh32hg39","numericID":1,"text":"covid is not as bad as normal flu #plandemic","rumourShortlist":[1,8,16,80]},{"tweetID":"q1tusehjsehj9oi3g23","numericID":2,"text":"@user drinking bleach cures covid","rumourShortlist":[15,8,100,211]}]}	{"1":{"rumourID":1,"category":"VACCINE","veracity":"FALSE","description":"Vaccines cause autism."},"8":{"rumourID":8,"category":"MEDICAL","veracity":"FALSE","description":"Drink  lots of water and you will be fine."},"15":{"rumourID":15,"category":"5G","veracity":"FALSE","description":"5G towers contribute to the spread of Coronavirus"}}'
        result = annotation_parser.parse_meta_data(header)
        expected_tweets = {"tweetSample":[{"tweetID":"gioshwsejh32hg39","numericID":1,"text":"covid is not as bad as normal flu #plandemic","rumourShortlist":[1,8,16,80]},{"tweetID":"q1tusehjsehj9oi3g23","numericID":2,"text":"@user drinking bleach cures covid","rumourShortlist":[15,8,100,211]}]}
        expected_rumours = {"1":{"rumourID":1,"category":"VACCINE","veracity":"FALSE","description":"Vaccines cause autism."},"8":{"rumourID":8,"category":"MEDICAL","veracity":"FALSE","description":"Drink  lots of water and you will be fine."},"15":{"rumourID":15,"category":"5G","veracity":"FALSE","description":"5G towers contribute to the spread of Coronavirus"}}
        self.assertEqual((expected_tweets, expected_rumours), result)

    def test_parse_line(self):
        line = "3/18/2021 6:25:48\t1\tVirus Transmission\tOther: Claim not listed\tMedical Advice\tClaim #15: 5G towers contribute to the spread of Coronavirus"
        result = annotation_parser.parse_line(line, 2)
        expected = (1, [("Virus Transmission", "Other: Claim not listed"), ("Medical Advice", 15)])
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
