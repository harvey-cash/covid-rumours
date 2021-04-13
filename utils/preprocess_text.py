import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import string  
import gensim
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer


def remove_stopwords(content):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(content)
    clean_content = [w.lower() for w in word_tokens if w.lower() not in stop_words]
    return clean_content

def lemmatize_words(content):
    wordnet_lemmatizer = WordNetLemmatizer()
    word_tokens = word_tokenize(content)
    clean_content = [wordnet_lemmatizer.lemmatize(w.lower()) for w in word_tokens]
    return clean_content

def stem_words(content):
    porter = PorterStemmer()
    #lan_porter = LancasterStemmer()
    word_tokens = word_tokenize(content)
    clean_content = [porter.stem(w.lower()) for w in word_tokens]
    return clean_content

def remove_small_terms(content):
    SMALL_WORD_THRESHOLD = 3
    word_tokens = word_tokenize(content)
    clean_content = [w for w in word_tokens if len(w) > SMALL_WORD_THRESHOLD]
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
    nostop_content = remove_stopwords(content)
    lemmatized_content = lemmatize_words(" ".join(nostop_content))
    stemmed_content = stem_words(" ".join(lemmatized_content))
    clean_content = remove_small_terms(" ".join(stemmed_content))
    return " ".join(clean_content)