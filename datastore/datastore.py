"""
This library is responsible for interactions with the datastore.
The datastore stores all the Tweets to be annotated, and (once annotated) their annotations.

JSON of tweets:
    tweetID: {
        numericID,
        text,
        annotations: [
            { participantID, category, veracity, rumour, etc. }
            { participantID, ... }
        ]
    }

# Lookup tweetID
JSON of numeric IDs:
    numericID: tweetID

"""
import json

TWEET_STORE_PATH = "./tweet_store.json"     # Dictionary of all tweet data
ID_LOOKUP_PATH = "./id_lookup.json"         # Lookup Tweet ID from numeric ID
NUMERIC_ID_PATH = "./numeric_id.txt"       # Store of last assigned numeric ID


def store_tweet(tweet_json_string):
    """Add to store if tweetID is not already present in the store"""

    # Parse JSON string
    tweet = json.loads(tweet_json_string)
    tweet_id = tweet["tweetID"]

    tweet_store = load_tweet_store()

    # Return failure if tweetID is already in store
    if tweet_id in tweet_store:
        return "Tweet ID {tweet_id} Already in store!".format(tweet_id=tweet_id)

    # Generate new unique numeric ID and add to lookup table
    numeric_id = generate_new_numeric_id()
    append_id_lookup(numeric_id, tweet_id)

    tweet["numericID"] = numeric_id  # Add numeric id to tweet dictionary

    # Write tweet to store and return success
    tweet_store[tweet_id] = str(tweet)
    write_tweet_store(tweet_store)

    return "Success!"


def load_tweet_store():
    """ Return the tweet store as a python dictionary """
    # ToDo: Only load if not already loaded - save disk read time
    with open(TWEET_STORE_PATH, 'r') as tweet_json_file:
        return json.loads(tweet_json_file.read())


def write_tweet_store(tweet_dict):
    """ Overwrite the store """
    with open(TWEET_STORE_PATH, 'w') as file:
        file.write(json.dumps(tweet_dict))


def generate_new_numeric_id():
    """ Returns a new unique numeric id """
    numeric_id = -1

    # Read the current latest id
    with open(NUMERIC_ID_PATH, "r") as file:
        numeric_id = int(file.read())

    # Increment and write
    numeric_id += 1

    with open(NUMERIC_ID_PATH, "w") as file:
        file.write(str(numeric_id))

    return numeric_id


def append_id_lookup(numeric_id, tweet_id):
    """ Add pair to lookup table """
    # Read dict
    lookup_dict = {}
    with open(ID_LOOKUP_PATH, 'r') as file:
        lookup_dict = json.loads(file.read())

    lookup_dict[str(numeric_id)] = tweet_id

    # Write
    with open(ID_LOOKUP_PATH, 'w') as file:
        file.write(json.dumps(lookup_dict))


def lookup_tweet_id(numeric_id):
    """ Given a numeric ID, look up its tweet ID
    :return string id or None if not found
    """
    lookup_dict = {}
    with open(ID_LOOKUP_PATH, 'r') as file:
        lookup_dict = json.loads(file.read())

    return lookup_dict.get(str(numeric_id))
