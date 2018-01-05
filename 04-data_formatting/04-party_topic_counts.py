# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 09:56:52 2017

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
    parser.add_argument('--indtmbuild', help="Raw DTM build pkl file", required = True, \
                        default="D:/cong_text/final_pos/DTMs/raw_dtmbuildobj.pkl")
    parser.add_argument('--inmerged', help="Topic/lemtag merged CSV file", required=True, \
                        default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv")
    parser.add_argument('--outpath', help="Path to output directory", required=True, \
                        default="D:/cong_text/final_pos/DTMs/")
    parser.add_argument('--outfile', help="Start of filename the count output (e.g., party_counts_", \
                        required=True, default="party_counts_")

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


    print("Saving feature counts by party and topic...")
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)
    outfilebase = ARGS.outpath + ARGS.outfile
    
    for t in range(len(tcounts.counts)):
        print("\t Topic {}...".format(t))
        outfile = outfilebase + 'topic{}.pkl'.format(t)
        with open(outfile, "wb") as f:
            pickle.dump(tcounts.counts[t], f, protocol=-1)
    
    print("DONE!")
    