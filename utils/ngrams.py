# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 16:44:27 2021

@author: Ruxandra
"""

import gensim
import gensim.models
import preprocess_text as pp
import pandas as pd
from nltk.corpus import stopwords

def create_trigrams(content):
    bigram = gensim.models.Phrases(content, min_count=10)
    trigram = gensim.models.Phrases(bigram[content])  
    
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    
    return bigram_mod, trigram_mod

df = pd.read_csv('../RumourDatabase.csv',encoding='utf8')
clean_content = pp.clean_df(df['Claim'], clean_non_alpha=True)
bigram_mod, trigram_mod = create_trigrams(clean_content)
print(trigram_mod[bigram_mod[clean_content[600]]])

'''
#different way to clean this
stop_words = set(stopwords.words('english'))
cleaned_content = pp.remove_non_alpha_chars(df['Claim'])
tokenized_words_no_removal = pp.clean_df(cleaned_content, stop_words = [], filter_short=0)
bigram_mod_token_no_removal, trigram_mod_token_no_removal = create_trigrams(tokenized_words_no_removal)
cleaned_trigrams_no_removal = pp.clean_df(trigram_mod_token_no_removal[bigram_mod_token_no_removal[tokenized_words_no_removal]], stop_words = stop_words, filter_short=3)
print(cleaned_trigrams_no_removal[600])
'''