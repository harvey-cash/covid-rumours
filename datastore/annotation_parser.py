from tkinter import filedialog
import json

"""
This script is responsible for the specifics of parsing the Google Forms response Sheets
into JSONs that can be added to the datastore
"""

NON_TWEET_QUESTIONS = 2  # Number of non-tweet questions (Timestamp, Participant ID)
PARTICIPANT_ID_COLUMN = 1  # Second column
META_DATA_COLUMNS = 2  # tweetsToAnnotate and knownRumours JSON
DELIMITER = '\t'  # TSV


def load_annotation_files():
    """ Launches a filedialog interface to select files to parse"""
    files = filedialog.askopenfiles(title="Select annotation response TSV files", filetypes=[("TSV Files", ['.tsv'])])
    if files is None:
        return []

    return [load_annotation_file(file.name) for file in files]


def load_annotation_file(file_path):
    """ Parses an AnnotationsForm TSV and returns a list of annotation dictionaries
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

    # Parse header for meta data
    tweets_to_annotate, known_rumours = parse_meta_data(lines[0])
    tweet_count = len(tweets_to_annotate["tweetSample"])

    annotations = []

    # Parse each line for participant IDs and question responses
    for line in lines[1:]:  # Omitting header
        participant_id, responses = parse_line(line, tweet_count)

        annotation_dict = {"participantID": participant_id, "annotations": []}

        # Populate the annotations
        for i, (category, claim) in enumerate(responses):
            # Omit unannotated tweets?
            if category == "" and claim == "":
                continue

            tweet_id = tweets_to_annotate["tweetSample"][i]["tweetID"]  # Fetch from original JSON

            # ToDo: Replace "other" claim strings with -1 or -2 codes?
            annotation_dict["annotations"].append({
                "tweetID": tweet_id,
                "category": category,
                "rumourID": claim
            })

        annotations.append(annotation_dict)  # An entry for each participant to annotate this form

    return annotations


def parse_meta_data(header_string):
    """ Returns tweetsToAnnotate and knownRumours used in form generation as python dictionaries """
    columns = header_string.split(DELIMITER)
    tweets_to_annotate = json.loads(columns[-2])  # Second from last
    known_rumours = json.loads(columns[-1])
    return tweets_to_annotate, known_rumours


def parse_line(line_string, tweet_count):
    """ Returns participant ID and list of ("CATEGORY", rumourID) tuples for each tweet
     - includes empty string values for those not answered """
    fields = line_string.split(DELIMITER)

    participant_id = int(fields[PARTICIPANT_ID_COLUMN])  # Second column
    responses = []

    tweet_answers = fields[NON_TWEET_QUESTIONS:]  # Drop the non-tweet question answers

    for i in range(tweet_count):
        category = tweet_answers[i*2]  # Simply a string e.g. "Virus Transmission" or "" if not answered
        claim_string = tweet_answers[i*2 + 1]  # Either "Other: reason" or "Rumour #XX: description"
        claim = parse_claim_id(claim_string)  # If it is a rumourID, recover the numeric value

        responses.append((category, claim))

    return participant_id, responses


def parse_claim_id(claim_string):
    """ Extract numeric id if one exists, else return the string unmodified """
    if claim_string.startswith("Claim #") or claim_string.startswith("Rumour #"):
        return int((claim_string.split('#')[1]).split(':')[0])  # Extract number
    else:
        return claim_string


