# A) How to build the PTB WSJ features:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\PartyOfSpeech\07-descriptive\PTB
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 01-build_ptb_counts.py --outpath D:/cong_text/final_pos/ptb/ --outfile ptb_dtm_vocab.pkl
```

