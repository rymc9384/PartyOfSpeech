## Author: Ryan McMahon
## Date Created: 03/07/2018
## Date Last Modified: 03/15/2018
## File: "~/06-robustness/03-exploratory/03-pronouns_female.R"

## Purpose: This script compares the use of gendered pronouns by senators' party
##          and sex. 
##

## Edits:
##       03/15/18) Drop docs w/ < 25 tokens
##      
##        

## Notes:
##      03/06/18) Based on "01-verbtense_immigration_plot.R" (12/18/2017)
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

# Regex expressions:
PRP.re <- "[a-z]+_PRP[$]?"

##############################
### 1) LOAD & PREP DATA
##############################

## 1.0) Read in text:
df <- read.csv("D:/cong_text/final_pos/topic_lemtag_merged_114.csv")

## 1.1) Read in senator meta info:
seninfo <- read.csv("D:/cong_text/robust/senator_info_links_id_female.csv")

## 1.2) Merge senator sex into text data:
df <- merge(df, seninfo[,c("sen", "female")], by="sen", all.x = T)

## 1.3) Remove newlines:
df$lemma_text <- gsub(pattern = "[\n]", replacement = '', df$lemma_text)

## 1.4) Count pronouns:
df$prp <- str_extract_all(string = df$lemma_text, pattern = PRP.re)

## 1.5) Count all tokens:
df$words <- NA

for (i in 1:nrow(df)){
  df$words[i] <- count_tokens(df$lemma_text[i])
}

## 1.6) Drop docs w/ fewer than 25 tokens:
df <- df[df$words >= 25, ]


##############################
### 2) SUBSET COUNTS
##############################

## 2.0) Split female/male senators:
df.f <- df[which(df$female == 1), ]
df.m <- df[which(df$female == 0), ]


## 2.1) Democratic pronouns by sex:
# 2.1a) females
prpFD <- make_counts(x = df.f, count_cols = c('prp'), 
                    party = 'D', topic = 0, totalcol = 'words', 
                    outcolnames = c('word', 'counts1', 'priors1'))
# 2.1b) males
prpMD <- make_counts(x = df.m, count_cols = c('prp'), 
                    party = 'D', topic = 0, totalcol = 'words', 
                    outcolnames = c('word', 'counts2', 'priors2'))
# 2.1c) combine
prpAllD <- merge(x = do.call(rbind, prpFD$counts), 
                y = do.call(rbind, prpMD$counts), 
                by="word", all = T)


## 2.2) Republican pronouns by sex:
# 2.2a) females
prpFR <- make_counts(x = df.f, count_cols = c('prp'), 
                     party = 'R', topic = 0, totalcol = 'words', 
                     outcolnames = c('word', 'counts1', 'priors1'))
# 2.2b) males
prpMR <- make_counts(x = df.m, count_cols = c('prp'), 
                     party = 'R', topic = 0, totalcol = 'words', 
                     outcolnames = c('word', 'counts2', 'priors2'))
# 2.2c) combine
prpAllR <- merge(x = do.call(rbind, prpFR$counts), 
                 y = do.call(rbind, prpMR$counts), 
                 by="word", all = T)

## 2.3) Fill NAs to avoid numerical errors:
# 2.3a) dems
prpAllD[is.na(prpAllD[,2]),2] <- 0
prpAllD[is.na(prpAllD[,3]),3] <- 0.01
prpAllD[is.na(prpAllD[,4]),4] <- 0
prpAllD[is.na(prpAllD[,5]),5] <- 0.01
# 2.3b) reps
prpAllR[is.na(prpAllR[,2]),2] <- 0
prpAllR[is.na(prpAllR[,3]),3] <- 0.01
prpAllR[is.na(prpAllR[,4]),4] <- 0
prpAllR[is.na(prpAllR[,5]),5] <- 0.01


##############################
### 3) FIT MODEL
##############################

## 3.0) Fightin' Words model:
# 3.0a) dems
fw_prpD <- fightin(n1 = prpFD$nwords, n2 = prpMD$nwords, 
                  counts1 = prpAllD$counts1, counts2 = prpAllD$counts2, 
                  priors1 = prpAllD$priors1, priors2 = prpAllD$priors2)
# 3.0a) reps
fw_prpR <- fightin(n1 = prpFR$nwords, n2 = prpMR$nwords, 
                   counts1 = prpAllR$counts1, counts2 = prpAllR$counts2, 
                   priors1 = prpAllR$priors1, priors2 = prpAllR$priors2)
## 3.1) Index words:
fw_prpD$word <- prpAllD$word
fw_prpR$word <- prpAllR$word

## 3.2) Print most partisan words:
#3.2a) dems
cat("\n\nDEMS\n\tMales:")
head(fw_prpD[order(fw_prpD$zeta),], 20)
cat("\n\tFemales:")
tail(fw_prpD[order(fw_prpD$zeta),], 20)

#3.2b) reps
cat("\n\nREPS:\n\tMales:")
head(fw_prpR[order(fw_prpR$zeta),], 20)
cat("\n\tFemales:")
tail(fw_prpR[order(fw_prpR$zeta),], 20)
