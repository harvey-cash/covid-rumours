from elasticsearch import Elasticsearch
import json

elastic_client = Elasticsearch(hosts=["http://143.167.8.152:9300"], http_auth=('students', 'foxtrot'))


def search_for_terms(amount, claim_dict):
    """
    Search using a term_frequency dictionary
    :param amount: integer number of tweets to return
    :param claim_dict: dictionary of {term: frequency}s
    :return: array of tweet IDs
    """

    must_array = [{"match": {"is_a_retweet": "false"}}, {"match": {"is_a_quote": "false"}}]
    should_array = [{"match": {"tweet_text": "*" + str([term, frequency]) + "*"}} for term, frequency in claim_dict.items()]

    query_body = {
        "query": {
            "bool": {
                "must": must_array,
                "must_not": [
                    {"match": {"hashtags": "obamagate"}},
                    {"exists": {"field": "in_reply_to_user_id"}},
                    {"exists": {"field": "in_reply_to_status_id"}},
                    {"exists": {"field": "in_reply_to_screen_name"}},
                    {"match": {"message": "*media_url*"}}
                ],
                "should": should_array
            }
        },
        "collapse": {
            "field": "tweet_id.keyword"
        }
    }

    result = elastic_client.search(index="covid19_misinfo_index", body=query_body, size=amount, request_timeout=999999,
                                   _source="tweet_id")  #

    tweets = [doc["_source"]["tweet_id"] for doc in result['hits']['hits']]

    return tweets


def random_rumours(amount, categories):
    #     #using hashtags
    #     public_authority_actions = []
    #     community_impact = ["filmyourhospital", "filmyourhospitals", "endthelockdown", "endthelockdownuk", "reopenbritain"]
    #     medical_advice = ["coronavirusfacts",  "coronafacts", "covid19symptoms", "covidsymptoms", "hydroxichloroquine", "hydroxychloroquine"]
    #     claims_about_prominent_actors = ["gatesvirus", "sorosvirus", "coronavillains", "kungflu", "wholiedpeopledied", "chinaliedandpeopledied",  "chinaliedpeopledied", "chinaliespeopledied", "israelvirus", "americavirus", "coronaviruscoverup", "chinesevirus", "wuhanvirus", "ccpvirus"]
    #     conspiracy_theories = ["5g",  "5gcoronavirus", "coronavirus5g", "chinesebioterrorism", "gatesvirus", "ciavirus", "deepstatevirus", "preventnwo",  "nwoevilelites", "nwovirus", "nwo", "greatreset", "coronacon",   "coronafakenews",  "coronafraud", "coronahoax", "scamdemic", "plandemic", "filmyourhospital", "filmyourhospitals", "coronaviruscoverup", "coronavillains", "depopulation", "nwoevilplans"]
    #     virus_transmission = ["coronavirusfacts",  "coronafacts"]
    #     virus_origin = ["coronavirusfacts",  "coronafacts", "covid19symptoms", "covidsymptoms", "coronasymptoms"]
    #     civil_disobedience = ["endthelockdown", "endthelockdownuk", "reopenbritain", "resistthegreatreset", "idonotconsent", "covidiots", "coronaviruscoverup"]
    #     vaccines = ["coronavirusfacts",  "coronafacts", "astrazeneca",  "oxfordvaccine"]
    #     other = ["coronabollocks", "coronacon",   "coronafakenews",  "coronafraud", "coronahoax", "cronyvirus", "scamdemic", "plandemic"]

    #     def f(x):
    #         return {
    #             "Public authority actions, policy, and communications": (public_authority_actions, float(x[1])),
    #             "Community spread and impact": (community_impact, float(x[1])),
    #             "Medical advice and self-treatments": (medical_advice, float(x[1])),
    #             "Claims about prominent actors": (claims_about_prominent_actors, float(x[1])),
    #             "Conspiracy theories": (conspiracy_theories, float(x[1])),
    #             "Virus transmission": (virus_transmission, float(x[1])),
    #             "Virus origin and properties": (virus_origin, float(x[1])),
    #             "Public preparedness, protests, and civil disobedience": (civil_disobedience, float(x[1])),
    #             "Vaccines, medical treatments, and tests": (vaccines, float(x[1])),
    #             "Other": (other, float(x[1])),
    #         }[x[0]]

    should_array = []
    must_array = [{"match": {"is_a_retweet": "false"}}, {"match": {"is_a_quote": "false"}}]
    # for x in categories:
    #   query = f(x)
    #  should_array.append({"terms": {"hashtags": query[0], "boost": query[1]}})

    input_file = open("bowPerCategoryNew.json", "r")
    input_data = input_file.read()
    # using BOW
    category_BOW = json.loads(
        input_data)  # this is a dict, so category_BOW["Virus origin and properties"] = array of words

    should_array = []
    for x in categories:
        for y in category_BOW[x]:  # input must be exactly the same as keys used in json
            should_array.append({"match": {"tweet_text": "*" + y + "*"}})
            # this will change based on how the json is parsed - y[0] just needs to be the text, and y[1] the number of times that
            # word appears in the bag. x[0] is the category input to the method, and x[1] is the number input to the method for that
            # category (user boost)

    query_body = {
        "query": {
            "bool": {
                "must": must_array,
                "must_not": [
                    {"match": {"hashtags": "obamagate"}},
                    {"exists": {"field": "in_reply_to_user_id"}},
                    {"exists": {"field": "in_reply_to_status_id"}},
                    {"exists": {"field": "in_reply_to_screen_name"}},
                    {"match": {"message": "*media_url*"}}
                ],
                "should": should_array
            }
        },
        "collapse": {
            "field": "tweet_id.keyword"
        }
    }

    result = elastic_client.search(index="covid19_misinfo_index", body=query_body, size=amount, request_timeout=999999,
                                   _source="tweet_id")  #

    all_hits = result['hits']['hits']

    tweets = []
    for num, doc in enumerate(all_hits):
        tweets.append(doc["_source"]["tweet_id"])
    return tweets


def text_from_id(ids):
    should_array = []

    for x in ids:
        should_array.append({"match": {"tweet_id": x}})

    query_body = {
        "query": {
            "bool": {
                "must": {
                    "bool": {
                        "should": should_array
                    }
                }
            }
        },
        "collapse": {
            "field": "tweet_id.keyword"
        }
    }

    result = elastic_client.search(index="covid19_misinfo_index", body=query_body, request_timeout=30000,
                                   _source="tweet_text")

    all_hits = result['hits']['hits']

    res = []
    for num, doc in enumerate(all_hits):
        res.append(doc["_source"]["tweet_text"])
    return res
