# -*- coding: utf-8 -*-
"""
Created on Wed Oct  4 11:49:56 2017

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd

from collections import Counter
from utils import Config, tokenidx


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Format Processed ExpAgenda Topic Model Text for the HDP Topic Model Check")
    parser.add_argument('-i', '--infile', help="CSV of processed text (from `01-processingExpAgenda.py`)", required=True)
    parser.add_argument('-op', '--outpath', help="Where to save output", required=False, type=str, default="D:/cong_text/csvs/tokenized/topicmodeling/HDP/")
    parser.add_argument('-s', '--split', help="Train/test split; default = 0.9 for train", required = True, type=float, default = 0.9)
    parser.add_argument('--outtrain', help="Filename for the training output", required=True)
    parser.add_argument('--outtest', help="Filename for the testing output", required=True)
    
    ARGS = parser.parse_args()
    
    
    os.chdir(Config.outpath)
    
    # Read in data:
    print("Reading in {}...".format(ARGS.infile))
    df = pd.read_csv(ARGS.infile, header=0)
    df = df.dropna()
    
    # Put text into a list:
    text = list(df.topic_text)
    
    # Split into training and test sets:
    n_train = int(len(text) * ARGS.split)
    print("Splitting corpus into {} training and {} testing documents...".format(n_train, len(text) - n_train))
    train = text[:n_train]
    test = text[n_train:]
    
    # Map tokens to numeric IDs:
    print("Mapping tokens to numeric IDs...")
    w2idx, idx2w = tokenidx(train)
    
    # Build word counts:
    print("Building word counts...")
    C = Counter()
    for doc in train:
        C += Counter(i for i in doc.split(' '))
        
    print("Counts produced for {} tokens...".format(len(C)))
    
    # Format documents for the HDP model (e.g., ['[M] id1:count1 id30:count30 ...', ...]),
    # where [M] is the number of unique terms in the document
    print("Formatting text for the HDP model...")
    newtrain = []
    newtest = []
    
    for doc in train:
        newdoc = [str(w2idx[w]) + ":" + str(C[w]) for w in doc.split(' ')]
        newdoc = str(len(newdoc)) + " " + " ".join(newdoc)
        newtrain.append(newdoc)
        
    for doc in test:
        newdoc = [str(w2idx[w]) + ":" + str(C[w]) for w in doc.split(' ') if w in w2idx.keys()]
        newdoc = str(len(newdoc)) + " " + " ".join(newdoc)
        newtest.append(newdoc)
    
    if os.path.exists(ARGS.outpath) == False:
            os.makedirs(ARGS.outpath)
        
    os.chdir(ARGS.outpath)
    
    # Write out data
    print("Saving training data to {}...".format(ARGS.outpath + ARGS.outtrain))
    with open(ARGS.outtrain, "w") as outfile:
        outfile.write('\n'.join(newtrain))
        
    print("Saving testing data to {}...".format(ARGS.outpath + ARGS.outtest))
    with open(ARGS.outtest, "w") as outfile:
        outfile.write('\n'.join(newtest))
        
    print("DONE!")
    