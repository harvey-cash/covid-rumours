import nltk
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import ToktokTokenizer
import pandas as pd

def lowercase(word_tokens):
    return [w.lower() for w in word_tokens]

def remove_stopwords(word_tokens, stop_words):
    return [w for w in word_tokens if w not in stop_words]

def lemmatize_words(word_tokens):
    wordnet_lemmatizer = WordNetLemmatizer()
    return [wordnet_lemmatizer.lemmatize(w) for w in word_tokens]

def stem_words(word_tokens, porter_stem=False, lan_stem=False):
    if not porter_stem and not lan_stem:
        return word_tokens
    porter = PorterStemmer() if porter_stem else LancasterStemmer()
    return [porter.stem(w) for w in word_tokens]

def remove_small_terms(word_tokens, threshold=3):
    return [w for w in word_tokens if len(w) > threshold]

def remove_non_alpha_chars(content_collection):
    only_alpha = content_collection.str.replace(r'[_\W\d]',' ')
    only_alpha = only_alpha.str.strip()
    return only_alpha

def remove_non_alpha_chars_from_str(claim):
    only_alpha = claim.replace(r'[_\W\d]',' ')
    return only_alpha.strip()

def clean_df(content_collection, stop_words=[], filter_short=3, lemmatize=True, porter_stem=False, lan_stem=False, clean_non_alpha=True):
    word_tok = ToktokTokenizer()
    clean_content = []
    if clean_non_alpha:
        content_collection = remove_non_alpha_chars(content_collection)
    for content in content_collection:
        word_tokens = word_tok.tokenize(content)
        words = lowercase(word_tokens)
        words = remove_stopwords(words, stop_words)
        words = lemmatize_words(words)
        words = stem_words(words, porter_stem, lan_stem)
        clean_content.append(remove_small_terms(words, filter_short))
    return clean_content

def clean_str(claim, stop_words=[], filter_short=3, lemmatize=True, porter_stem=False, lan_stem=False, clean_non_alpha=True):
    word_tok = ToktokTokenizer()
    if clean_non_alpha:
        claim = remove_non_alpha_chars_from_str(claim)
    word_tokens = word_tok.tokenize(claim)
    words = lowercase(word_tokens)
    words = remove_stopwords(words, stop_words)
    words = lemmatize_words(words)
    words = stem_words(words, porter_stem, lan_stem)
    return " ".join(remove_small_terms(words, filter_short))


# Shouldn't have arbitrary code executing at the bottom of a library file. Put it in a method and call it, if you need
# it to be in this script?
"""
stop_words = set(stopwords.words('english'))
df = pd.read_csv('../RumourDatabase.csv',encoding='utf8')
clean_content = clean_str(df['Claim'][0], stop_words = stop_words, lemmatize=False, porter_stem=True)
print(clean_content)
"""
