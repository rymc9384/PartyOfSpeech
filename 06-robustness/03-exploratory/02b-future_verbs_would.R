## Author: Ryan McMahon
## Date Created: 03/08/2018
## Date Last Modified: 03/15/2018
## File: "~/06-robustness/03-exploratory/02b-future_verbs_would.R"

## Purpose: 
##      
##

## Edits:
##       03/09/18) Clean up formatting
##       03/15/18) Drop docs w/ < 25 tokens
##      
##        

## Notes:
##      
##  

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################

rm(list = ls())
library(stringr)
options(stringsAsFactors = F)

sessionInfo()

##############################
### 0) UTILITIES
##############################


# Call util functions into Global Env:
source("D:/Dropbox/Dissertation/02-pos_senate/01-code/PartyOfSpeech/06-robustness/utils_fw.R")

# Regex expression(s):
WOULD.re <- "[a-z]+_[A-Z]+ would_MD( [a-z]+_RB)? [a-z]+_VB"

##############################
### 1) LOAD & PREP DATA
##############################

## 1.0) Read in text:
df <- read.csv("D:/cong_text/final_pos/topic_lemtag_merged_114.csv")

## 1.1) Remove newlines:
df$lemma_text <- gsub(pattern = "[\n]", replacement = '', df$lemma_text)

## 1.2) Count future `would' phrases:
df$would <- str_extract_all(string = df$lemma_text, pattern = WOULD.re)

## 1.3) Count all tokens:
df$words <- NA

for (i in 1:nrow(df)){
  df$words[i] <- count_tokens(df$lemma_text[i])
}

## 1.4) Drop docs w/ fewer than 25 tokens:
df <- df[df$words >= 25, ]

##############################
### 2) SUBSET COUNTS
##############################

## 2.0) Republican woulds:
Rwould <- make_counts(x = df, count_cols = c('would'),
                       party = 'R', topic = 0, totalcol = 'words', 
                       outcolnames = c('word', 'counts1', 'priors1'))

## 2.1) Democratic woulds:
Dwould <- make_counts(x = df, count_cols = c('would'), 
                       party = 'D', topic = 0, totalcol = 'words', 
                       outcolnames = c('word', 'counts2', 'priors2'))

## 2.2) Merge R and D counts:
wouldAll <- merge(x = do.call(rbind, Rwould$counts[c(1)]), 
                y = do.call(rbind, Dwould$counts[c(1)]), 
                by="word", all = T)

## 2.3) Fill NAs to avoid numerical errors:
wouldAll[is.na(wouldAll[,2]),2] <- 0
wouldAll[is.na(wouldAll[,3]),3] <- 0.01
wouldAll[is.na(wouldAll[,4]),4] <- 0
wouldAll[is.na(wouldAll[,5]),5] <- 0.01


##############################
### 3) FIT MODEL
##############################

## 3.0) Fightin' Words model:
fw_would <- fightin(n1 = Rwould$nwords, n2 = Dwould$nwords, 
                  counts1 = wouldAll$counts1, counts2 = wouldAll$counts2, 
                  priors1 = wouldAll$priors1, priors2 = wouldAll$priors2)

## 3.1) Index words:
fw_would$word <- wouldAll$word

## 3.2) Print most partisan words:
cat("\n\n\tDEMS:\n")
head(fw_would[order(fw_would$zeta),], 20)
cat("\n\tREPS:\n")
tail(fw_would[order(fw_would$zeta),], 20)
