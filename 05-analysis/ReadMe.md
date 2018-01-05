# A) How to run Fightin' Words confirmatory analysis:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to analysis directory:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\05-analysis\
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 01-fightin_words_confirmatory.py --infeatures D:/cong_text/final_pos/DTMs/newfeatures_vocab.pkl --intopicpattern D:/cong_text/final_pos/DTMs/party_counts* --outpath D:/cong_text/final_pos/analysis/ > fightin_words_confirmatory.log
```



# B) How to run noun ratios confirmatory analysis:


### 1. Navigate to analysis directory:
CMD
```
> d:
> cd Dropbox\Dissertation\02-pos_senate\01-code\05-analysis\
```

### 2. Call R script (change merged data location)
CMD
```
> RScript 02-noun_ratios.R --infile D:/cong_text/final_pos/topic_lemtag_merged_114.csv --logfile ./noun_ratios.Rout --outfile D:/cong_text/final_pos/analysis/noun_ratios.RData
```