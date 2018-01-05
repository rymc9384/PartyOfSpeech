# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 11:15:02 2017

@author: Ryan McMahon
"""

import re
import string
import pandas

from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer


class Config():

    def makepattern():
        toremove = string.punctuation
        toremove = toremove.replace("$", "") # don't remove hyphens
        pattern = r"[{}]".format(toremove) # create the pattern

        return(pattern)

    # Configurations for file paths/name:
    inpath = "D:/cong_text/csvs/tokenized/raw/"
    outpath = "D:/cong_text/csvs/tokenized/topicmodeling/ExpAgendas/"
    senatorinfo = "D:/Dropbox/Dissertation/02-pos_senate/01-code/01alt-senator_info_links_senid.csv"

    # Configurations for functions:
    ub_min = 0.9
    lb_max = 0.005
    tolower = True
    dropna = True
    left = 'senator'
    right = 'sen'

    # Declaring functions:
    pattern = makepattern()

    stops = stopwords.words('english')
    stemmer = PorterStemmer()
    CVub = CountVectorizer(min_df=ub_min, lowercase=tolower)
    CVlb = CountVectorizer(max_df=lb_max, lowercase=tolower)


def cleantext(text=None, pattern=Config.pattern, stemmer=Config.stemmer, stops=Config.stops):
    text = [re.sub(pattern, "", doc) for doc in text]
    text = [re.sub('\s+', " ", doc) for doc in text]
    if stemmer:
        text = [' '.join([stemmer.stem(w) for w in doc.split(' ') if not w in stops]).strip() for doc in text]

    return(text)


def preprocessfile(file=None, df_all=None, badvocab=None, mindate=None, \
                   maxdate=None, dropna=Config.dropna, CVub=Config.CVub):
    # file = path to csv with tokenized text
    #
    if not file:
        raise TypeError('Need a file!')

    if not badvocab:
        badvocab = Counter()

    df = pandas.read_csv(file, header=0)
    if dropna == True:
        df.dropna(inplace=True)
        
    df['form_date'] = pandas.to_datetime(df['form_date'], yearfirst=True)
        
    if mindate:
        validdates = df['form_date'] >= pandas.to_datetime(mindate, yearfirst=True)
        df = df.loc[validdates, :]
    
    if maxdate:
        try:
            validdates = df['form_date'] <= pandas.to_datetime(maxdate, yearfirst=True)
            df = df.loc[validdates, :]
        except ValueError:
            if type(df_all) == pandas.core.frame.DataFrame:
                return(df_all, badvocab)
            else:
                return(df, badvocab)

    text = list(df.tokenized_text)
    text = cleantext(text=text)

    df.drop(labels=['tokenized_text'], axis=1, inplace=True)
    df['topic_text'] = text

    try:
        CVub.fit(text)
        badvocab += Counter(CVub.get_feature_names())
    except ValueError:
        None
        
    if type(df_all) == pandas.core.frame.DataFrame:
        df_all = df_all.append(df)
    else:
        df_all = df

    return(df_all, badvocab)


def preprocesscombined(text=None, badvocab=None, CVlb=Config.CVlb, CVub=Config.CVub):
    # text (list(str)) = all processed text from individual files
    #
    if not text:
        raise TypeError('Need the combined texts!')

    if not badvocab:
        badvocab = Counter()

    CVlb.fit(text)
    CVub.fit(text)

    badvocab += Counter(CVlb.get_feature_names() + CVub.get_feature_names())
    text = [' '.join([w for w in doc.split(' ') if w not in badvocab.keys()]).strip() for doc in text]

    return(text)


def mergecombinedinfo(df_all=None, infofile=Config.senatorinfo, left=Config.left, right=Config.right):
    if type(df_all) != pandas.core.frame.DataFrame:
        raise TypeError('Need the combined dataframe!')

    info = pandas.read_csv(infofile)

    merged = df_all.merge(info, how='left', left_on=left, right_on=right)

    if len(merged) != len(df_all):
        raise Warning("Merged data differs in length from original, inspect it!")

    return(merged)


# String to idx for tokens:
def tokenidx(sentences):
    ###
    # PURPOSE: Map tokens to integer labels.
    #
    # Args:
    #   (1) sentences (list): a list of sentences w/ space delimited tokens
    #
    # Output:
    #   (1) out (list): out[0] (dict) = words to idx; 
    #                   out[1] (list) = idx to words
    #
    ###
    tokens = dict()
    revtokens = []
    idx = 0
    
    for sentence in sentences:
        for w in sentence.split(' '):
            if not w in tokens:
                tokens[w] = idx
                revtokens += [w]
                idx += 1
            else:
                continue

    out = [tokens, revtokens]

    return out