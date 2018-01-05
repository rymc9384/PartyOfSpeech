## Author: Ryan McMahon
## Date Created: 12/18/2017
## Date Last Modified: 12/18/2017
## File: "~/06-robustness/03-exploatory/01-verbtense_immigration_plot.R"

## Purpose: Generate figure showing verbtense differences in `Immigration` 
##          topic.
##

## Edits:
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


##############################
### 0) UTILITIES
##############################

# Call util functions into Global Env:
source("D:/Dropbox/Dissertation/02-pos_senate/01-code/06-robustness/utils_fw.R")

# Regex expressions:
FUTVB.re <- "[a-z]+_MD( [a-z]+_RB)? [a-z]+_VB"
ALLVB.re <- "[a-z]+_VB[A-Z]{0,1}"


##############################
### 1) LOAD & PREP DATA
##############################

## 1.0) Read in text:
df <- read.csv("D:/cong_text/final_pos/topic_lemtag_merged_114.csv")

## 1.1) Remove newlines:
df$lemma_text <- gsub(pattern = "[\n]", replacement = '', df$lemma_text)

## 1.2) Count verbs:
df$futvb <- str_extract_all(string = df$lemma_text, pattern = FUTVB.re)
df$allvb <- str_extract_all(string = df$lemma_text, pattern = ALLVB.re)

## 1.3) Count all tokens:
df$words <- NA

for (i in 1:nrow(df)){
  df$words[i] <- count_tokens(df$lemma_text[i])
}


##############################
### 2) SUBSET COUNTS
##############################

## 2.0) Republican verbs:
vbR <- make_counts(x = df, count_cols = c('futvb', 'allvb'), 
                   party = 'R', topic = 9, totalcol = 'words', 
                   outcolnames = c('word', 'counts1', 'priors1'))

## 2.1) Democratic verbs:
vbD <- make_counts(x = df, count_cols = c('futvb', 'allvb'), 
                   party = 'D', topic = 9, totalcol = 'words', 
                   outcolnames = c('word', 'counts2', 'priors2'))

## 2.2) Merge R and D counts:
vbAll <- merge(x = do.call(rbind, vbR$counts[c(1,2)]), 
               y = do.call(rbind, vbD$counts[c(1,2)]), 
               by="word", all = T)

## 2.3) Fill NAs to avoid numerical errors:
vbAll[is.na(vbAll[,2]),2] <- 0
vbAll[is.na(vbAll[,3]),3] <- 0.01
vbAll[is.na(vbAll[,4]),4] <- 0
vbAll[is.na(vbAll[,5]),5] <- 0.01


##############################
### 3) FIT MODEL
##############################

## 3.0) Fightin' Words model:
fw_vbs <- fightin(n1 = vbR$nwords, n2 = vbD$nwords, 
                  counts1 = vbAll$counts1, counts2 = vbAll$counts2, 
                  priors1 = vbAll$priors1, priors2 = vbAll$priors2)

## 3.1) Index words:
fw_vbs$word <- vbAll$word

## 3.2) Print most partisan words:
head(fw_vbs[order(fw_vbs$zeta),], 20)
tail(fw_vbs[order(fw_vbs$zeta),], 20)


##############################
### 4) MAKE FIGURE
##############################

pdf(file = "D:/Dropbox/Dissertation/02-pos_senate/02-writing/figures/03-verb_diff_immigration.pdf", 
    width = 15, height = 10, encoding = "WinAnsi.enc")

fightin_plot(words = fw_vbs$word, zeta = fw_vbs$zeta, freq = fw_vbs$freq, nwords = 15, zcut = 1.96)

dev.off()
