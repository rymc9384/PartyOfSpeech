# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 09:39:33 2018

@author: Ryan McMahon
"""

import argparse
import os
import pandas as pd
import pickle
import re
from utils import featureset, datautils, analysisutils


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Conduct intra- and inter-topic analyses")
    parser.add_argument('--infeatures', help="Features object file", required=False, \
                        default="D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl")
    parser.add_argument('--intopicpattern', help="Path with pattern for party topic counts", \
                        required=False, default="D:/cong_text/final_pos/DTMs/party_counts*")
    parser.add_argument('--outfile', help="Where to save zetas column vector (pkl)", \
                        required=False, default="D:/cong_text/final_pos/DTMs/zetas_vector.pkl")

    ARGS = parser.parse_args()

    # Regex for verb tense:
    PAST_RE = re.compile("(VBD|VBN)")
    FUTURE_RE = re.compile("(MD VB|MD RB VB)(?=\s|$)")


    print("Loading feature sets...\n")
    feats = featureset(featurefile = ARGS.infeatures)
    feats.loadself()

    print("Finding all party topic count files...\n")
    d = datautils(countspathpattern = ARGS.intopicpattern)


    print("Loading party counts for all topics...")
    d.load_counts(topic = 0)


    print("Setting up features -- fixing pronoun number and verb tense tags...")
    d._features = feats._prpnum_feats
    d._features = [re.sub(PAST_RE, 'VBPAST', feat) for feat in d._features]
    d._features = [re.sub(FUTURE_RE, 'VBFUT', feat) for feat in d._features]

    feats_df = pd.DataFrame(d._features, columns=['word'])

    print("Fitting Fightin' Words Model (uninformative prior)..")
    d.builddf()
    a = analysisutils(wordcounts=d._tempdf)
    a.fightinwords()

    fw_df = a._fwoutput

    print("Merging Fightin' Words Zeta Values to feature vector...")
    feats_fw_df = pd.merge(left=feats_df, right=fw_df[['word','zeta']], how='left', on='word')
    zetas = feats_fw_df.as_matrix(columns=['zeta'])

    print("Saving Zeta vector to {}...".format(ARGS.outfile))
    with open(ARGS.outfile, "wb") as f:
        pickle.dump(zetas, f, protocol=-1)

    print("DONE!")
