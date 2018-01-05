# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 10:54:02 2017

@author: Ryan McMahon
"""

import argparse
import os
import pickle
import pandas as pd

from utils import topiccounts


if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Get feature counts by party and topic")
    parser.add_argument('--indtmbuild', help="Input DTM build pkl file", required = True, \
                        default="D:/cong_text/robust/DTMs/unitag_dtmbuildobj.pkl")
    parser.add_argument('--inmerged', help="Topic/lemtag merged CSV file", required=True, \
                        default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv")
    parser.add_argument('--outpath', help="Path to output directory", required=True, \
                        default="D:/cong_text/robust/DTMs/")
    parser.add_argument('--outfile', help="File name to save dataframe to (csv)", \
                        required=True, default="unitag_partytopiccounts.csv")

    ARGS = parser.parse_args()

    print("Reading in DTM build...")
    with open(ARGS.indtmbuild, "rb") as f:
        rawbuild = pickle.load(f)

    print("Subsetting build to just DTM and clearing memory...\n")
    DTM = rawbuild.DTM
    del rawbuild

    print("Reading in merged topic/lemma text data...\n")
    merged = pd.read_csv(ARGS.inmerged, encoding='utf-8')

    print("Declaring constants for processing...\n")
    ndocs = DTM.shape[0]
    avgdoclen = int(DTM.sum(axis=1).mean())

    GOPidx = list(merged.party == 'R')
    DEMidx = list(merged.party != 'R')
    unitopics = list(merged.topic.unique())
    unitopics.sort()


    print("Creating instance of the topiccounts class...\n")
    tcounts = topiccounts(counts={}, avgdoclen=avgdoclen, ndocs=ndocs, \
                          GOPidx=GOPidx, DEMidx=DEMidx)

    print("Getting counts by party for all topics...\n")
    tcounts.counttopic(DTM=DTM, Tidx=None, topic=0)

    # loop over topics to get counts and priors:
    print("Working on counts by topic...")
    for unitopic in unitopics:
        print("\t Topic {}...".format(unitopic))
        Tidx = list(merged.topic == unitopic)
        tcounts.counttopic(DTM=DTM, Tidx=Tidx, topic=unitopic)

    
    print("\nJoining party topic counts into single dataframe...")
    for i in range(len(tcounts.counts)):
        print("\tworking on topic {}...".format(i))
        k = tcounts.counts[i]
        tmp = [[a, b, c, d] for a, b, c, d in zip(k[0], k[1], k[2], k[3])]
        tmp_columns = ["gopcounts{}".format(i),
                       "demcounts{}".format(i),
                       "goppriors{}".format(i),
                       "dempriors{}".format(i)]
        if i == 0:
            countsdf = pd.DataFrame(tmp)
            countsdf.columns = tmp_columns
        else:
            tmp_df = pd.DataFrame(tmp)
            tmp_df.columns = tmp_columns
            countsdf = countsdf.join(tmp_df, on=None, how="left")


    print("Saving feature counts...")
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)
    outfile = ARGS.outpath + ARGS.outfile
    
    countsdf.to_csv(outfile, index=False, encoding='utf-8')
    
    print("DONE!")