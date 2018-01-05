# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 13:24:04 2017

@author: Ryan McMahon
"""

import argparse
import os
from utils import newfeatures


if __name__ == "__main__":
    
    # parsing arguments
    parser = argparse.ArgumentParser(description="Get feature counts by party and topic")
    parser.add_argument('--indtmbuild', help="Raw DTM build pkl file", required = False, \
                        default="D:/cong_text/final_pos/DTMs/raw_dtmbuildobj.pkl")
    parser.add_argument('--outpath', help="Path to output directory", required=False, \
                        default="D:/cong_text/final_pos/DTMs/")
    parser.add_argument('--outfile', help="Name of vocab outfile", \
                        required=False, default="newfeatures_vocab.pkl")

    ARGS = parser.parse_args()


    print("Creating instance of newfeatures class...\n")
    features = newfeatures()
    
    print("Loading {}...\n".format(ARGS.indtmbuild))
    features.loadbuildobj(infile=ARGS.indtmbuild)
    
    print("Splitting pronouns into singular and plural...\n")
    features.prp_num_sub()
    
    print("Replacing senator specific lemmas...\n")
    features.replace_specific()
    
    print("Making past and future verb tense features...\n")
    features.verb_tense_sub()
    
    print("Making singular and plural noun features...\n")
    features.noun_num_sub()
    
    print("Making general noun features, w/ and w/o proper nouns...\n")
    features.noun_super_sub()
    
    print("Saving new feature sets...\n")
    if not os.path.exists(ARGS.outpath):
        os.makedirs(ARGS.outpath)
    outfile = ARGS.outpath + ARGS.outfile
    features.save(outfile = outfile)
    
    print("DONE!")
    