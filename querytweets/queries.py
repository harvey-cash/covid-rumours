from elasticsearch import Elasticsearch

elastic_client = Elasticsearch(hosts=["http://143.167.8.152:9300"], http_auth=('students', 'foxtrot'))


def random_rumours(amount, categories):
    fiveg = ["5g", "5gcoronavirus", "coronavirus5g"]
    chinesevirus = ["chinaliedandpeopledied", "chinaliedpeopledied", "chinaliespeopledied", "chinesebioterrorism",
                    "chinesevirus", "wuhanvirus", "ccpvirus", "kungflu"]
    americavirus = ["americavirus", "ciavirus", "deepstatevirus", "sorosvirus"]
    endlockdown = ["endthelockdown", "endthelockdownuk", "reopenbritain"]
    newworldorder = ["preventnwo", "nwoevilelites", "nwovirus", "nwo", "greatreset", "resistthegreatreset",
                     "nwoevilplans", "depopulation"]
    gatesvirus = ["gatesvirus"]
    wholied = ["wholiedpeopledied"]
    israelvirus = ["israelvirus"]
    generalrumour = ["coronabollocks", "coronacon", "coronafakenews", "coronafraud", "coronahoax", "cronyvirus",
                     "scamdemic", "plandemic"]
    antifakenews = ["coronavirusfacts", "coronafacts", "covidiots"]
    emptyhospitals = ["filmyourhospital", "filmyourhospitals"]
    antivax = ["idonotconsent"]
    medical = ["astrazeneca", "covid19symptoms", "covidsymptoms", "oxfordvaccine", "hydroxichloroquine",
               "hydroxychloroquine", "coronasymptoms"]
    antiestablishment = ["coronaviruscoverup", "coronavillains", "depopulation"]

    def f(x):
        return {
            "fiveg": (fiveg, float(x[1])),
            "chinesevirus": (chinesevirus, float(x[1])),
            "americavirus": (americavirus, float(x[1])),
            "endlockdown": (endlockdown, float(x[1])),
            "newworldorder": (newworldorder, float(x[1])),
            "gatesvirus": (gatesvirus, float(x[1])),
            "wholied": (wholied, float(x[1])),
            "israelvirus": (israelvirus, float(x[1])),
            "generalrumour": (generalrumour, float(x[1])),
            "antifakenews": (antifakenews, float(x[1])),
            "emptyhospitals": (emptyhospitals, float(x[1])),
            "antivax": (antivax, float(x[1])),
            "medical": (medical, float(x[1])),
            "antiestablishment": (antiestablishment, float(x[1]))
        }[x[0]]

    must_array = [{"match": {"is_a_retweet": "false"}}, {"match": {"is_a_quote": "false"}}]
    for x in categories:
        query = f(x)
        must_array.append({"terms": {"hashtags": query[0], "boost": query[1]}})

    query_body = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": must_array,
                        "must_not": [
                            {"match": {"hashtags": "obamagate"}},
                            {"exists": {"field": "in_reply_to_user_id"}},
                            {"exists": {"field": "in_reply_to_status_id"}},
                            {"exists": {"field": "in_reply_to_screen_name"}},
                            {"match": {"message": "*media_url*"}}
                        ]
                    }
                },
                "random_score": {}
            }
        }
    }

    result = elastic_client.search(index="covid19_misinfo_index", body=query_body, size=amount, request_timeout=30000,
                                   _source="tweet_text,tweet_id")

    all_hits = result['hits']['hits']

    tweets = []
    for num, doc in enumerate(all_hits):
        tweets.append(doc["_source"]["tweet_text"])
    return tweets
