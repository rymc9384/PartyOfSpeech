# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 12:32:18 2017

@author: Ryan McMahon
"""

import csv
import nltk
import os
import re
import sys
import pandas as pd

from glob import glob
from utils import Config


# Fix field limit for CSVs (from stackoverflow):
maxInt = sys.maxsize
decrement = True

while decrement:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

# Declare path to Java 1.8:
Config.java_home()

# Declare tokenizers:
sent_toker = nltk.tokenize.sent_tokenize # defaults to Punkt
word_toker = nltk.tokenize.TreebankWordTokenizer()

# Declare tagger:
Tagger = nltk.tag.StanfordPOSTagger(Config.tagger, Config.jar)

# Increase max memory allocated to Java for tagging to 5GB:
Tagger.java_options = '-mx5000m'

# Define a tagging function that incorporates try/excepts:
def tagfunc(Tagger, doc, j):
    # Tagger = NLTK.tag instance
    # doc = list(list(str)); list of sentences, which are lists of tokens
    # j = int; document indicator.
    try:
        return(Tagger.tag_sents(doc))
    except OSError:
        pass  # fallback to dict
    try:
        temp_sents = []
        for sent in doc:
            temp_sents.append(Tagger.tag(sent))
        return(temp_sents)
    except OSError:
        print("Failed to tag document {}".format(j))
        return([[('','')], [('','')]])
    

# Make the output folders:
try:
    os.makedirs(Config.tokenout)
    os.makedirs(Config.taggedout)
except FileExistsError:
    None
    

if __name__ == "__main__":
    # Go to CSVs of text:
    os.chdir(Config.pathinput)

    files = glob("*.csv")

    for i, file in enumerate(files):
        contents = []
        print("\n\nReading in file {}...".format(file))
        with open(file) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                contents.append(row)

        # Put into a dataframe:
        df = pd.DataFrame(data=contents[1:])
        df.columns = contents[0]
        
        # Reindex using `docid`; 
        # This lets us gauge posting dates even if that's missing for a doc:
        dfindex = []
        for doc in df.docid:
            dfindex.append(int(re.sub('[a-z]*$', '', doc)))
            
        df.index = dfindex
        df.sort_index(inplace=True)
        
        if file == '43-heller.csv':
            df = Config.fix_heller_dates(df)
        
        # Subset to 2013-2016:
        df['form_date'] = pd.to_datetime(df['form_date'], yearfirst=True)
        validdates = df['form_date'] >= pd.to_datetime('2013-01-03', yearfirst=True)
        lastvalid = max(validdates.index.where(validdates == True))
        
        df = df.loc[:lastvalid, :]
        
        # Drop empty docs:
        notempty = df['clean_text'] != ''
        df = df.loc[notempty, :]
        
        n_docs = len(df)

        # Tokenize into sentences:
        print("Tokenizing text...")
        sent_docs = []
        for row in df['clean_text']:
            sent_docs.append(sent_toker(row))

        # Tokenize into words:
        word_docs = []
        for doc in sent_docs:
            word_docs.append(word_toker.tokenize_sents(doc))

        # Tag tokens:
        print("Tagging text...")
        tagged_docs = []
        for j, doc in enumerate(word_docs):
            tagged_docs.append(tagfunc(Tagger, doc, j))
            
            if j % int(n_docs/10) == 0:
                perc_done = round(j /n_docs, 1) * 100
                print("{}% of documents tagged...".format(perc_done))

        # Format tagged text:
        tagged_string = [[['_'.join(i) for i in sent] for sent in doc] for doc in tagged_docs]
        tagged_string2 = [' '.join([' '.join(sent) for sent in doc]) for doc in tagged_string]

        # Format tokenized text (so tokens are whitespace delimited):
        token_string = [' '.join([' '.join(sent) for sent in doc]) for doc in word_docs]

        # Make new data frames for tokenized and tagged texts:
        df_tokenized = df.loc[:, ['docid', 'senator', 'form_date', 'title']]
        df_tagged = df.loc[:, ['docid', 'senator', 'form_date', 'title']]

        # Add tokenized docs and tagged docs:
        df_tokenized['tokenized_text'] = token_string
        df_tagged['tagged_text'] = tagged_string2

        # Save the new dataframes:
        print("Saving tokenized and tagged texts...")
        tokenout = Config.tokenout + file
        taggedout = Config.taggedout + file

        df_tokenized.to_csv(path_or_buf=tokenout, index=False, encoding='utf-8')
        df_tagged.to_csv(path_or_buf=taggedout, index=False, encoding='utf-8')

        print("***** Done with file {} *****".format(i))
