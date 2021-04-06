import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
import string  
import gensim
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer

def clean_text(content_collection):
    wordnet_lemmatizer = WordNetLemmatizer()
    porter = PorterStemmer()
    #lan_porter = LancasterStemmer()
    stop_words = set(stopwords.words('english'))
    clean_content=[]
    for content in content_collection:
        #turn string into tokens
        word_tokens = word_tokenize(content)
        words = [porter.stem(wordnet_lemmatizer.lemmatize(w.lower())) for w in word_tokens if w not in stop_words] #remove stop words
        #lowercase, remove stop words and punctuation/numbers
        clean_content.append( [w for w in words if len(w) > 3] ) 
    return clean_content