# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 11:38:07 2017

@author: Ryan McMahon
"""

import argparse
import os

from utils import topiclem

config = topiclem.Config

if __name__ == "__main__":

    # parsing arguments
    parser = argparse.ArgumentParser(description="Merge document topic data with lemmatized and tagged text (incl. metadata)")
    parser.add_argument('--topicfile', help="Input topic data file", required=False, default=None)
    parser.add_argument('--mergeoutfile', help="Filename for the merged output", required=False, default=None)

    ARGS = parser.parse_args()

    # update configs if necessary
    if ARGS.topicfile != None:
        config.topicfile = ARGS.topicfile

    if ARGS.mergeoutfile != None:
        config.mergeoutfile = ARGS.mergeoutfile

    # load data
    topicdf, taglemdf = topiclem.loadtopiclem(config.topicfile, config.taglemfile)

    # merge
    merged = topiclem.mergetoplem(topicdf, taglemdf, taglemcols=config.taglemcols, \
                                howmerge=config.howmerge, mergeon=config.mergeon)

    # check merge
    topiclem.testmergelen(topicdf, merged)

    # save
    if os.path.exists(config.mergeoutpath) == False:
        os.makedirs(config.mergeoutpath)

    outfile = config.mergeoutpath + config.mergeoutfile

    merged.to_csv(outfile, index=False, encoding='utf-8')
