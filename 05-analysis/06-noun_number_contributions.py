# -*- coding: utf-8 -*-
"""
Created on Thu Mar  8 14:33:30 2018

@author: Ryan McMahon
"""


import argparse
import os
import pandas as pd
import re

from utils import featureset, datautils, analysisutils


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Conduct intra- and inter-topic analyses")
    parser.add_argument('--infeatures', help="Features object file", required=False, \
                        default="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl")
    parser.add_argument('--intopicpattern', help="Path with pattern for party topic counts", \
                        required=False, default="D:/cong_text/final_pos/DTMs/party_counts*")

    ARGS = parser.parse_args()



    print("Loading feature sets...\n")
    feats = featureset(featurefile = ARGS.infeatures)
    feats.loadself()

    print("Finding all party topic count files...\n")
    d = datautils(countspathpattern = ARGS.intopicpattern)

    print("Loading party counts for all topics...\n")
    d.load_counts(topic = 0)

    print("Analyzing all ngrams...\n")
    d._features = feats._prp_feats
    d.builddf()
    a = analysisutils(wordcounts=d._tempdf)
    a.fightinwords()

    print(a.get_word('NN'))
    print('\n')
     
    print(a.get_word('NNS'))
    print('\n')
    
    print(a.get_word('NNP'))
    print('\n')
    
    print(a.get_word('NNPS'))
    print('\n')
    
    print(a.get_word('PRPSING'))
    print('\n')
    
    print(a.get_word('PRPPLUR'))
