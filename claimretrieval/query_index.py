from utils import preprocess_text

def create_query_dict(query):
    clean_query = preprocess_text.clean_all(query)
    query_words = clean_query.split()
    query_dict = {}
    for word in query_words:
        if word not in query_dict:
            query_dict[word] = 0
        query_dict[word] += 1
    return query_dict


