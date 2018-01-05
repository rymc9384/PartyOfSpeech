# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 10:51:14 2017

@author: Ryan McMahon
"""

import os

from glob import glob
from utils import lemtag


config = lemtag.Config


if __name__ == "__main__":

    os.chdir(config.tagbasepath)

    tagrawfiles = glob(config.tagrawpath + "*.csv")
    taglemfiles = glob(config.taglemmapath + "*.csv")

    tagfilepairs = [(i, j) for i, j in zip(tagrawfiles,taglemfiles)]
    npairs = len(tagfilepairs)

    fulldf = None

    for i, pair in enumerate(tagfilepairs):
        print("Merging file pair {}/{}...".format(i, npairs))

        rawdf, lemdf = lemtag.loadrawlem(pair[0], pair[1])
        lemtag.testalign(raw=rawdf, lem=lemdf, col='tagged_text')

        rawdf['lemma_text'] = lemdf['lemma_text']

        print("Adding {} to the full merged data...\n".format(rawdf.senator[0]))
        fulldf = lemtag.appendsens(fulldf=fulldf, rawdf=rawdf)


    print("Saving all senators' merged data to {}{}\n".format(config.tagbasepath, config.lemmafinalout))
    fulldf.to_csv(config.lemmafinalout, index=False, encoding='utf-8')

    print("DONE!")
    