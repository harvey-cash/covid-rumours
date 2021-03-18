"""
This script is responsible for the specifics of parsing the Google Forms response Sheets
into JSONs that can be added to the datastore
"""

NON_TWEET_QUESTIONS = 3  # Number of non-tweet questions (Timestamp, Email Address, Participant ID)
DELIMITER = ','  # CSV


def load_annotation_csv(file_path):
    """ Parses an AnnotationsForm CSV and returns a list of annotation dictionaries
    [{
        "participantID": 1,
        "annotations": [
            {"numericTweetID": 1, "category": "Virus Transmission", "rumourID": None},
            {"numericTweetID": 2, "category": "Medical Advice", "rumourID": 15}
        ]
    }]
    """
    lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse header for numeric tweet IDs
    numeric_tweet_ids = parse_header_string(lines[0])

    # Parse each line for participant IDs and question responses
    for line in lines[1:]:  # Omitting header
        participant_id, responses = parse_line(line)

    return []


def parse_header_string(header_string):
    """ Returns list of numeric tweet IDs parsed from CSV header """
    numeric_tweet_ids = []

    column_names = header_string.split(DELIMITER)  # CSV
    tweet_questions = column_names[NON_TWEET_QUESTIONS:]  # Drop the non-tweet question titles
    tweet_count = round(len(tweet_questions) / 2)  # Category and claim question for each tweet

    for i in range(tweet_count):
        # ~~~ "Tweet #12: Category" ~~~
        question_string = tweet_questions[i*2]  # skip every other question
        numeric_id = int((question_string.split('#')[1]).split(':')[0])  # Extract number
        numeric_tweet_ids.append(numeric_id)

    return numeric_tweet_ids


def parse_line(line_string):
    """ Returns participant ID and list of ("CATEGORY", rumourID) tuples for each tweet answered """
    fields = line_string.split(DELIMITER)

    participant_id = int(fields[2])  # Third column
    responses = []

    tweet_answers = fields[NON_TWEET_QUESTIONS:]  # Drop the non-tweet question answers
    tweet_count = round(len(tweet_answers) / 2)  # Category and claim answers for each tweet

    for i in range(tweet_count):
        category = tweet_answers[i*2]  # Simply a string e.g. "Virus Transmission"
        claim_string = tweet_answers[i*2 + 1]  # Either "Other: reason" or "Rumour #XX: description"
        claim = parse_claim_id(claim_string)  # If it is a rumourID, recover the numeric value

        responses.append((category, claim))

    return participant_id, responses


def parse_claim_id(claim_string):
    """ Extract numeric id if one exists, else return the string unmodified """
    if claim_string.startswith("Claim #"):
        return int((claim_string.split('#')[1]).split(':')[0])  # Extract number
    else:
        return claim_string


