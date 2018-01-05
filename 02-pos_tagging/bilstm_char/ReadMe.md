# BiLSTM POS Tagger 

## Based on [this repo](https://github.com/guillaumegenthial/sequence_tagging) and [blog post](https://guillaumegenthial.github.io/sequence-tagging-with-tensorflow.html). 

## See the ``original_ner_README.md'' document to see the documentation for that project.

----

The model was originally intended for Named Entity Recognition (NER), but many of the techniques that are succesful in that domain are also applicable to tagging.

In order to run the model, the data needs to be in CONLL (2003) format, except with NER tags replaced with POS tags:

```
Pierre NNP
Vinken NNP
, ,
61 CD
years NNS
old JJ
, ,
will MD
join VB
the DT
board NN
as IN
a DT
nonexecutive JJ
director NN
Nov. NNP
29 CD
. .

Mr. NNP
Vinken NNP
is VBZ
chairman NN
of IN
Elsevier NNP
N.V. NNP
, ,
the DT
Dutch NNP
publishing VBG
group NN
. .
```

For this example model, I use the Penn Treebank WSJ sample available in the NLTK library. 

### Running model:

First, write out the PTB WSJ sample data in a CONLL format:
```
python nltk2conll.py
'''

Then build vocab from the data and extract trimmed glove vectors according to the configuration in `config.py`.

```
python build_data.py
```

Finally, train and test model with 

```
python main.py
```

On a 70-10-20 train, dev, test split, this model acheived a 96.86% token level accuracy on the test set.