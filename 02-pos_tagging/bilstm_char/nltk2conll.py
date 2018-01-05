# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 13:22:13 2017

@author: Ryan McMahon
"""


import nltk

##### Write out the sample PTB data into CONLL style text files ######

## FUNCTIONS:

def format_nltk_data(data):
    """
    Makes list of sentences, with elements are 'WORD TAG' pairs 

    Args:
        data: list of sentences with (WORD, TAG) tuple elements
    Returns:
        List of sentences, with elements are 'WORD TAG' pairs 
        
    Example:
    data = [[('The', 'DET'), ('cat', 'NN')], [(WORD, TAG), ...]]
    returns: [['The DET', 'cat NN'], [WORD TAG,...]]
    """
    
    out = []
    
    for d in data:
        t_d = [x + ' ' + y for x,y in d]
        out.append(t_d)
        
    return out
    
    
def data_split(data, train_prop=0.7, dev_prop=0.1):
    """
    Generates training, development, and test sets.

    Args:
        data (list): sentences from the *format_nltk_data* function
        train_prop (float): proportion of data for training (< 1.0)
        dev_prop (float): proportion of data for development (< 1.0)
    Returns:
        Three splits of the data sized according to *_prop args
        
    Example:
    data = [[('The', 'DET'), ('cat', 'NN')], [(WORD, TAG), ...]]
    returns: [['The DET', 'cat NN'], [WORD TAG,...]]
    """
    
    
    if 1.0 - train_prop - dev_prop <= 0:
        raise ValueError('Training and Dev proportions sum to 1 or greater.')
    
    train_s, dev_s = int(train_prop * len(data)), int(dev_prop * len(data))
    test_start = train_s + dev_s

    tr, dev, te = data[:train_s], data[train_s:test_start], data[test_start:]
    
    return [tr,dev,te]
    
    


def write_raw_data(sents, filename):
    """
    Writes a vocab to a file

    Args:
        vocab: list of sentences with 'WORD TAG' pair elements
        filename: path to data file
    Returns:
        write a WORD TAG pair per line
    """
    with open(filename, "w") as f:
        for i, s in enumerate(sents):
            if i != 0:
                f.write("\n")
            for pair in s:
                f.write("{}\n".format(pair))
                
        f.write("")


## Actually formatting:

# Read in Treebank data:
raw_sents = list(nltk.corpus.treebank.tagged_sents())

# Format for writing to files:
sents = format_nltk_data(raw_sents)
    
# Split into train, dev, and test sets
train, dev, test = data_split(sents, 0.7, 0.1)

# Write out:
write_raw_data(train, 'data/ptb_samp/train.txt')
write_raw_data(dev, 'data/ptb_samp/dev.txt')
write_raw_data(test, 'data/ptb_samp/test.txt')

