# A) How to build the unigram DTM objects:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\06-robustness\01-unigrams
```

### 3. Call python script w/ desired args:
CMD
```
(textcleaning) > python 01-unigram_dtmbuilding.py --infile D:/cong_text/final_pos/topic_lemtag_merged_114.csv --outpath D:/cong_text/robust/DTMs/ --outfilelem unilem_dtmbuildobj.pkl --outfiletag unitag_dtmbuildobj.pkl > unigram_dtmbuilding.log
```


# B) How to get unigram feature counts by party and topic:

### 1. Activate Conda Environment: 
CMD
```
> C:\Users\YOU\> activate textcleaning 
```

### 2. Navigate to directory with python scripts:
CMD
```
(textcleaning) > d:
(textcleaning) > cd Dropbox\Dissertation\02-pos_senate\01-code\06-robustness\01-unigrams
```

### 3. Call python script w/ desired args (either using tag only or lem_tag data):
CMD
```
(textcleaning) > python 02-unigram_party_topic_counts.py --indtmbuild D:/cong_text/robust/DTMs/unitag_dtmbuildobj.pkl --inmerged D:/cong_text/final_pos/topic_lemtag_merged_114.csv --outpath D:/cong_text/robust/DTMs/ --outfile unitag_partytopiccounts.csv > tags_party_topic_counts.log
(textcleaning) > python 02-unigram_party_topic_counts.py --indtmbuild D:/cong_text/robust/DTMs/unilem_dtmbuildobj.pkl --inmerged D:/cong_text/final_pos/topic_lemtag_merged_114.csv --outpath D:/cong_text/robust/DTMs/ --outfile unilem_partytopiccounts.csv > lems_party_topic_counts.log
```
