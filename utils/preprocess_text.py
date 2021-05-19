import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import string  
import gensim
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
import re

db_stopwords = [
    'iphoto',
    'photo',
    'photograph',
    'foto',
    'screenshot',
    'ss',
    'video',
    'film',
    'facebook',
    'fb',
    'twitter',
    'instagram',
    'insta',
    'whatsapp',
    'graphic',
    'post',
    'audio',
    'clip',
    'show',
    'shown',
]

def remove_stopwords(content):
    stop_words = set(stopwords.words('english'))
    stop_words.update(db_stopwords)
    #word_tokens = word_tokenize(content)
    clean_content = [w.lower() for w in content if w.lower() not in stop_words]
    return clean_content

def lemmatize_words(content):
    wordnet_lemmatizer = WordNetLemmatizer()
    #word_tokens = word_tokenize(content)
    clean_content = [wordnet_lemmatizer.lemmatize(w.lower()) for w in content]
    return clean_content

def stem_words(content):
    porter = PorterStemmer()
    #lan_porter = LancasterStemmer()
    #word_tokens = word_tokenize(content)
    clean_content = [porter.stem(w.lower()) for w in content]
    return clean_content

def remove_small_terms(content):
    SMALL_WORD_THRESHOLD = 3
    #word_tokens = word_tokenize(content)
    clean_content = [w for w in content if len(w) > SMALL_WORD_THRESHOLD]
    return clean_content

def remove_punctuation(content):
    re.sub(r'http\S+', '', content)
    clean_content = [re.sub('[^0-9a-z]+','', w) for w in content]
    # Removes additional space created because of removing punctuation
    clean_content = [w for w in clean_content if w.strip()]
    return clean_content

# def clean_preprocess(content):
#     wordnet_lemmatizer = WordNetLemmatizer()
#     porter = PorterStemmer()
#     #lan_porter = LancasterStemmer()
#     stop_words = set(stopwords.words('english'))
#     clean_content=[]
#     #turn string into tokens
#     word_tokens = word_tokenize(content)
#     words = [porter.stem(wordnet_lemmatizer.lemmatize(w.lower())) for w in word_tokens if w not in stop_words] #remove stop words
#     #lowercase, remove stop words and punctuation/numbers
#     clean_content.append( [w for w in words if len(w) > 3] ) 
#     return clean_content

def clean_all(content):
    tokens = word_tokenize(content)
    nostop_content = remove_stopwords(tokens)
    lemmatized_content = lemmatize_words(nostop_content)
    stemmed_content = stem_words(lemmatized_content)
    clean_content = remove_small_terms(stemmed_content)
    return " ".join(clean_content)