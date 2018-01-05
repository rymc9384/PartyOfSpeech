## Author: Ryan McMahon
## Date Created: 11/30/2017
## Date Last Modified: 12/07/2017
## File: "~/06-robustness/03-exploatory/01-temp_verbtense.R"

## Purpose: 
##      
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


source("D:/Dropbox/Dissertation/02-pos_senate/01-code/06-robustness/utils_fw.R")


## Regex expressions:
FUTVB.re <- "[a-z]+_MD( [a-z]+_RB)? [a-z]+_VB"
PASTVB.re <- "[a-z]+_(VBD|VBN)"
ALLVB.re <- "[a-z]+_VB[A-Z]{0,1}"


## Read in text:
df <- read.csv("D:/cong_text/final_pos/topic_lemtag_merged_114.csv")

## Read in senator meta info:
seninfo <- read.csv("D:/cong_text/robust/senator_info_links_id_female.csv")

## merge senator sex into text data:
df <- merge(df, seninfo[,c("sen", "female")], by="sen", all.x = T)


## Cleaning newlines out
df$lemma_text <- gsub(pattern = "[\n]", replacement = '', df$lemma_text)


df$futvb <- str_extract_all(string = df$lemma_text, pattern = FUTVB.re)
df$pastvb <- str_extract_all(string = df$lemma_text, pattern = PASTVB.re)
df$allvb <- str_extract_all(string = df$lemma_text, pattern = ALLVB.re)
df$prp <- str_extract_all(string = df$lemma_text, pattern = "[a-z]+_PRP[$]?")

df$words <- NA

for (i in 1:nrow(df)){
  
  df$words[i] <- count_tokens(df$lemma_text[i])
  
}


vbR <- make_counts(x = df, count_cols = c('futvb', 'pastvb', 'allvb'), 
                   party = 'R', topic = 9, totalcol = 'words', 
                   outcolnames = c('word', 'counts1', 'priors1'))

vbD <- make_counts(x = df, count_cols = c('futvb', 'pastvb', 'allvb'), 
                   party = 'D', topic = 9, totalcol = 'words', 
                   outcolnames = c('word', 'counts2', 'priors2'))

vbAll <- merge(x = do.call(rbind, vbR$counts[c(1,3)]), 
               y = do.call(rbind, vbD$counts[c(1,3)]), 
               by="word", all = T)

# avoid numerical errors:
vbAll[is.na(vbAll[,2]),2] <- 0
vbAll[is.na(vbAll[,3]),3] <- 0.01
vbAll[is.na(vbAll[,4]),4] <- 0
vbAll[is.na(vbAll[,5]),5] <- 0.01

fw_vbs <- fightin(n1 = vbR$nwords, n2 = vbD$nwords, 
                  counts1 = vbAll$counts1, counts2 = vbAll$counts2, 
                  priors1 = vbAll$priors1, priors2 = vbAll$priors2)
fw_vbs$word <- vbAll$word
head(fw_vbs[order(fw_vbs$zeta),], 20)
tail(fw_vbs[order(fw_vbs$zeta),], 20)


fightin_plot(words = fw_vbs$word, zeta = fw_vbs$zeta, freq = fw_vbs$freq, nwords = 15, zcut = 1.96)


##############
### Pronouns:
##############

df$prp <- str_extract_all(string = df$lemma_text, pattern = "[a-z]+_PRP[$]?")

df.f <- df[which(df$female == 1), ]
df.m <- df[which(df$female == 0), ]

prpR <- make_counts(x = df.f, count_cols = c('prp'), 
                    party = 'D', topic = 20, totalcol = 'words', 
                    outcolnames = c('word', 'counts1', 'priors1'))

prpD <- make_counts(x = df.m, count_cols = c('prp'), 
                    party = 'D', topic = 20, totalcol = 'words', 
                    outcolnames = c('word', 'counts2', 'priors2'))

prpAll <- merge(x = do.call(rbind, prpR$counts[1]), 
                y = do.call(rbind, prpD$counts[1]), 
                by="word", all = T)

# avoid numerical errors:
prpAll[is.na(prpAll[,2]),2] <- 0
prpAll[is.na(prpAll[,3]),3] <- 0.01
prpAll[is.na(prpAll[,4]),4] <- 0
prpAll[is.na(prpAll[,5]),5] <- 0.01

fw_prps <- fightin(n1 = prpR$nwords, n2 = prpD$nwords, 
                   counts1 = prpAll$counts1, counts2 = prpAll$counts2, 
                   priors1 = prpAll$priors1, priors2 = prpAll$priors2)
fw_prps$word <- prpAll$word
head(fw_prps[order(fw_prps$zeta),], 20)
tail(fw_prps[order(fw_prps$zeta),], 20)

fightin_plot(words = fw_prps$word, zeta = fw_prps$zeta, freq = fw_prps$freq, nwords = 15, zcut = 1.96)



## SHE/HER
df$sheher <- str_extract_all(string = df$lemma_text, pattern = "(she|hers?)_PRP[$]? [a-z]+_[A-Z]+")

sheherR <- make_counts(x = df, count_cols = c('sheher'), 
                       party = 'R', topic = 0, totalcol = 'words', 
                       outcolnames = c('word', 'counts1', 'priors1'))

sheherD <- make_counts(x = df, count_cols = c('sheher'), 
                       party = 'D', topic = 0, totalcol = 'words', 
                       outcolnames = c('word', 'counts2', 'priors2'))

sheherAll <- merge(x = do.call(rbind, sheherR$counts[1]), 
                   y = do.call(rbind, sheherD$counts[1]), 
                   by="word", all = T)

# avoid numerical errors:
sheherAll[is.na(sheherAll[,2]),2] <- 0
sheherAll[is.na(sheherAll[,3]),3] <- 0.01
sheherAll[is.na(sheherAll[,4]),4] <- 0
sheherAll[is.na(sheherAll[,5]),5] <- 0.01

fw_shehers <- fightin(n1 = sheherR$nwords, n2 = sheherD$nwords, 
                      counts1 = sheherAll$counts1, counts2 = sheherAll$counts2, 
                      priors1 = sheherAll$priors1, priors2 = sheherAll$priors2)
fw_shehers$word <- sheherAll$word
head(fw_shehers[order(fw_shehers$zeta),], 20)
tail(fw_shehers[order(fw_shehers$zeta),], 20)

fightin_plot(words = fw_shehers$word, zeta = fw_shehers$zeta, freq =fw_shehers$freq, nwords = 15, zcut = 1.96)


