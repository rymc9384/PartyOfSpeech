# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 14:14:03 2018

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
    parser.add_argument('--infeatures', help="Features object file", required=True, \
                        default="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl")
    parser.add_argument('--intopicpattern', help="Path with pattern for party topic counts", \
                        required=True, default="D:/cong_text/final_pos/DTMs/party_counts*")
    parser.add_argument('--outpath', help="Path to where to save output CSVs", \
                        required=True, default="D:/cong_text/final_pos/robust/exploratory/")

    ARGS = parser.parse_args()



    print("Loading feature sets...\n")
    feats = featureset(featurefile = ARGS.infeatures)
    feats.loadself()

    print("Finding all party topic count files...\n")
    d = datautils(countspathpattern = ARGS.intopicpattern)

    print("Loading party counts for all topics...\n")
    d.load_counts(topic = 0)

    print("Analyzing all ngrams...\n")
    d._features = feats._raw_feats
    d.builddf()
    a = analysisutils(wordcounts=d._tempdf)
    a.fightinwords()

    tmp_df = a._fwoutput

    print("Isolating ngrams containing a pronoun out of {} features...\n".format(len(tmp_df)))
    prpidx = []
    for i,w in enumerate(tmp_df.word):
        search = re.search('([a-z]+_PRP[$]? [a-z]+_[A-Z]+)|([a-z]+_[A-Z]+ [a-z]+_PRP[$]?)', w)
        if search is not None:
            prpidx.append(i)

    print("Found {} pronoun ngrams...\n".format(len(prpidx)))
    prp_df = tmp_df.iloc[prpidx,:]


    outfile = ARGS.outpath + "pronoun_ngrams_raw.csv"
    print("Saving pronoun ngram fightin words to {}...\n".format(outfile))
    prp_df.to_csv(outfile, encoding='utf-8', index=False)
