## Author: Ryan McMahon
## Date Created: 03/07/2018
## Date Last Modified: 03/28/2018
## File: "~/06-robustness/03-exploratory/04-pronouns_plus_figure.R"

## Purpose: This script examines partisan differences in pronoun use and the 
##          tokens that follow a pronoun. 
##

## Edits:
##       03/28/18) Use plot w/o point labels; use lemmas w/o tags in lists;
##                  sample w/ probability inverse to total freq 
##                  (goes from 581k ngrams to ~110k)
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
options(stringsAsFactors = F)
set.seed(1124)
sessionInfo()

##############################
### 0) UTILITIES
##############################

# Call util functions into Global Env:
source("D:/Dropbox/Dissertation/02-pos_senate/01-code/PartyOfSpeech/06-robustness/utils_fw.R")

SING.re <- "((?<=i)|(?<=(me|he|it|my))|(?<=(she|him|her|his|its))|(?<=(this|that|mine|hers))|(?<=myself)|(?<=(himself|herself))|(?<=yourself))_PRP[$]?(?=($| ))"
PLUR.re <- "((?<=(we|us))|(?<=^our)|(?<= our)|(?<=(they|them|ours))|(?<=(these|those|their))|(?<=theirs)|(?<=ourselves)|(?<=(yourselves|themselves)))_PRP[$]?(?=($| ))"


##############################
### 1) LOAD DATA
##############################

## 1.0) Read in output from "/05-analysis/05-pronoun_ngram_fightin_words.py":
df <- read.csv("D:/cong_text/robust/exploratory/pronoun_ngrams_raw.csv")

## 1.1) Format word column and make tagged column:
df$tagged <- df$word
df$word <- gsub(pattern = "_.*?(?=($| ))", '', df$word, perl = T)


##############################
### 2) TOP NGRAMS
##############################

## 2.0) Print most partisan words:
cat("\n\n**** MOST PARTISAN BI & TRIGRAMS ****")
cat("\n\tDEMS:\n")
head(df[order(df$zeta),], 20)
cat("\n\tREPS:\n")
tail(df[order(df$zeta),], 20)


##############################
### 3) SAMPLING NGRAMS
##############################

## 3.0) Sample low count words
PRkeep <- log(df$count)/3
PRkeep <- ifelse(PRkeep >= 1, 1, PRkeep) 
tokeep <- rbinom(n = PRkeep, size = 1, prob = PRkeep)

## 3.1) Print summary of sampled and omitted ngrams:
cat("\n\n**** SAMPLED NGRAM SUMMARIES ****")
cat("\n\tCounts:\n")
summary(df$count[tokeep==1])
cat("\n\tZetas:\n")
summary(df$zeta[tokeep==1])

cat("\n\n**** DROPPED NGRAM SUMMARIES ****")
cat("\n\tCounts:\n")
summary(df$count[tokeep==0])
cat("\n\tZetas:\n")
summary(df$zeta[tokeep==0])

## 3.2) Subset data frame using sampled ngrams
df <- df[tokeep==1,]

##############################
### 4) MAKE FIGURE
##############################

## 4.0) Declare colors for legend:
cols <- c("#d7191c","#fdae61","black","#2b83ba","#99d594")

## 4.1) Print to file:

pdf(file = "D:/Dropbox/Dissertation/02-pos_senate/02-writing/figures/04-pronoun_plus.pdf", 
    width = 16, height = 10, encoding = "WinAnsi.enc")

with(data = df,
     fw_nowords_plot(words=word, tagged=tagged, zeta=zeta/4.42, freq=count, nwords=15, zcut=1, 
                     classes=c("singular", "plural"), regexs=c(SING.re, PLUR.re), 
                     ylabel=expression(zeta[w]^(R-D)/4.42), corpus=T, leg=F)
)

legend("topleft", legend = c("GOP singular", "GOP plural", "Ambiguous number",
                             "Dem plural", "Dem singular"), 
       pch = c(21,23,22,21,23), pt.bg = cols, col = cols, pt.cex = 2, ncol = 2, inset = 0.05, cex=1.25, bty = "n")

dev.off()