# A) How to merge the raw and lemmatized text CSVs:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\04-data_formatting\
```

### 3. Call python script (file locations editable in utils.py -> lemtag -> Config):
CMD
```
(textcleaning) > python 01-merge_lemma_meta.py > merge_lemma_meta.log
```



# B) How to merge the topic data and lemmatized text CSVs (now w/ metadata):

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\04-data_formatting\
```

### 3. Call python script (file locations can be passed in as args):
CMD
```
(textcleaning) > python 02-merge_topic_taglem.py > merge_topic_taglem.log
```



# C) How to build the raw DTM and collect the common/rare n-grams:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\04-data_formatting\
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 03-raw_dtm_building.py --infile D:/cong_text/final_pos/topic_lemtag_merged_114.csv --outpath D:/cong_text/final_pos/DTMs/ --outfile raw_dtmbuildobj.pkl > raw_dtm_building.log
```



# D) How to get feature counts by party and topic:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\04-data_formatting\
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 04-party_topic_counts.py --indtmbuild D:/cong_text/final_pos/DTMs/raw_dtmbuildobj.pkl --inmerged D:/cong_text/final_pos/topic_lemtag_merged_114.csv --outpath D:/cong_text/final_pos/DTMs/ --outfile party_counts_ > party_topic_counts.log
```



# D) How to translate raw features into feature sets containing tags of interest:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\04-data_formatting\
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 05-make_feature_sets.py --indtmbuild D:/cong_text/final_pos/DTMs/raw_dtmbuildobj.pkl --outpath D:/cong_text/final_pos/DTMs/ --outfile newfeatures_vocab.pkl > make_feature_sets.log
```

