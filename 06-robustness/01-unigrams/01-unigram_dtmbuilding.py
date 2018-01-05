# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 10:36:12 2017

@author: Ryan McMahon
"""

import argparse
import os
import re
import pandas as pd
import pickle


from utils import buildrawdtm


if __name__ == "__main__":
    
    # parsing arguments
    parser = argparse.ArgumentParser(description="Generate raw DTM and feature sets")
    parser.add_argument('--infile', help="Topic/lemtag merged CSV file", required=True, \
                        default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv")
    parser.add_argument('--outpath', help="Path to output directory", required=True, \
                        default="D:/cong_text/robust/DTMs/")
    parser.add_argument('--outfilelem', help="Filename for the dtmbuild object w/ unigram lemmas", \
                        required=True, default="unilem_dtmbuildobj.pkl")
    parser.add_argument('--outfiletag', help="Filename for the dtmbuild object w/ unigram tagonly", \
                        required=True, default="unitag_dtmbuildobj.pkl")
    
    ARGS = parser.parse_args()
    
    
    print("Compiling regex statements...\n")
    prpsing_re = re.compile("((?<=i)|(?<=(me|he|it|my))|(?<=(she|him|her|his|its))|" +
								  "(?<=(this|that|mine|hers))|" +
								  "(?<=myself)|(?<=(himself|herself))|(?<=yourself))" +
								  "_PRP\$?")
    prpplur_re = re.compile("((?<=(we|us))|(?<=our)|(?<=(they|them|ours))|" +
								  "(?<=(these|those|their))|(?<=theirs)|" +
								  "(?<=ourselves)|" +
								  "(?<=(yourselves|themselves)))_PRP\$?")
    
    gettags_re = re.compile("[^\s]+_")
    vbpast_re = re.compile("(VBD|VBN)")
    vbfuture_re = re.compile("(MD VB|MD RB VB)(?=\s|$)")
    
    
    print("Reading in tagged/lemmatized text data...\n")
    merged = pd.read_csv(ARGS.infile, encoding="utf-8")
    
    print("Removing newline characters...\n")
    merged['lemma_text'] = [re.sub('[\r]?[\n]', '', x) for x in merged.lemma_text]
    
    print("Splitting pronouns into singular and plural...\n")
    merged['new_text'] = [re.sub(prpsing_re, '_PRPSING', x) for x in merged.lemma_text]
    merged['new_text'] = [re.sub(prpplur_re, '_PRPPLUR', x) for x in merged.new_text]
    
    print("Creating tag only documents...\n")
    merged['tagonly_text'] = [re.sub(gettags_re, '', x) for x in merged.new_text]
    merged['tagonly_text'] = [re.sub('_', '', x) for x in merged.tagonly_text]
    
    print("Generating past and future tense verb tags...\n")
    merged['tagonly_text'] = [re.sub(vbpast_re, 'VBPAST', x) for x in merged.tagonly_text]
    merged['tagonly_text'] = [re.sub(vbfuture_re, 'VBFUT', x) for x in merged.tagonly_text]
    
    
    
    print("\n** WORKING ON lem_tag DOCUMENTS **\n")
    sens = list(merged.senator.unique())
    nsens = len(sens)
    
    dtmbuildnew = buildrawdtm(ngrams=(1,1))
    
    print("Looping over individual senators...")
    for i, sen in enumerate(sens):
        print("Getting common ngrams for {}... \t {}/{}".format(sen, i+1, nsens))
        sendf = merged[merged.senator == sen]
        sentext = list(sendf.new_text)
    
        dtmbuildnew.get_commonngrams(text=sentext, general=False)
    
    
    print("\nGetting common ngrams for all senators...\n")
    dtmbuildnew.get_commonngrams(text=list(merged.new_text), general=True)
    
    print("Getting rare ngrams for all senators...\n")
    dtmbuildnew.get_rarengrams(text=list(merged.new_text))
    
    print("Making senator and general common n-gram lists mutually exclusive...\n")
    dtmbuildnew.make_exclusive_commonngrams()
    
    print("Making replacement features:")
    print("\tfor general common n-grams...")
    dtmbuildnew.make_replacement_feats(which='general')
    print("\tfor senator specific common n-grams...")
    dtmbuildnew.make_replacement_feats(which='sens')
    print("\tfor rare n-grams...\n")
    dtmbuildnew.make_replacement_feats(which='rare')
    
    print("\n** WORKING ON lem_tag and tagonly DOCUMENT SETS **\n")
    
    print("Building full DTMs...\n")
    dtmbuildnew.fit_transformfull(text=list(merged.new_text))
    dtmbuildtag = buildrawdtm(ngrams=(1,1))
    dtmbuildtag.fit_transformfull(text=list(merged.tagonly_text))
    
    
    print("Saving unigram lemma dtmbuild object...")
    if os.path.exists(ARGS.outpath) == False:
        os.makedirs(ARGS.outpath)
    dtmlemoutfile = ARGS.outpath + ARGS.outfilelem
    
    with open(dtmlemoutfile, "wb") as f:
        pickle.dump(dtmbuildnew, f, protocol=-1)
    
    del dtmbuildnew
    
    print("Saving unigram tagonly dtmbuild object...")
    dtmtagoutfile = ARGS.outpath + ARGS.outfiletag
    with open(dtmtagoutfile, "wb") as f:
        pickle.dump(dtmbuildtag, f, protocol=-1)
    
    print("Done!")