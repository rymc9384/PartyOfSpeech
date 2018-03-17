## Author: Ryan McMahon
## Date Created: 11/29/2017
## Date Last Modified: 03/12/2018
## File: "~/06-robustness/02-noun_ratios/01-other_nouns_combos.R"

## Purpose: 
##      
##

## Edits:
##      03/12/18) Add in test for NN(S) & NNP(S) based on footnote 11 in 
##                Cichocka et al. (2016, 809); drop releases w/ fewer than 25
##                tokens; add in regressions
##        

## Notes:
##      11/29/17) Based on "../../05-analysis/02-noun_ratios.R"
##  

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################

rm(list=ls())
library(stringr)
library(optparse)
options(stringsAsFactors = F)

## Parse command line arguments:
option_list <- list(
  make_option(c("-i", "--infile"), type="character", default="D:/cong_text/final_pos/topic_lemtag_merged_114.csv", 
              help="Merged topic lemma file [default=%default]", metavar="character"),
  make_option(c("-lf", "--logfile"), type="character", default="./just_nouns.Rout", 
              help="logfile name [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


sink(file = opt$logfile)
## Display package versions and other environment information:
cat("\tSession info:\n")
sessionInfo()

#########################
### 0) DEFINE FUNCTIONS
#########################


get_tags <- function(text){
  
  grams <- unlist(str_split(text, ' '))
  grams <- gsub(pattern = ".*_", replacement = '', grams)
  
  return(grams)
  
}

noun_ratio <- function(grams){
  
  
  n1.count <- str_count(string = grams, pattern = "NNS?(?=$)")
  n2.count <- str_count(string = grams, pattern = "(NNS?|NNPS?)(?=$)")
  n1.ratio <- sum(n1.count) / length(grams)
  n2.ratio <- sum(n2.count) / length(grams)
  return(c(n1.ratio, n2.ratio))
  
}


#########################
### 1) READ IN DATA
#########################
cat(paste0("\nReading in ", opt$infile, "...\n"))
merged <- read.csv(opt$infile)


#########################
### 2) COUNT NOUNS
#########################

cat("Counting nouns...\n")

merged$ntoks <- merged$nouns1 <- merged$nouns2 <- NA

for (i in 1:nrow(merged)){
  
  grams <- get_tags(text = merged$lemma_text[i])
  tmp <- noun_ratio(grams = grams)
  merged$ntoks[i] <- length(grams)
  merged$nouns1[i] <- tmp[1]
  merged$nouns2[i] <- tmp[2]
  
}

## Drop releases w/ fewer than 25 tokens:
merged <- merged[merged$ntoks >= 25,]


#########################
### 3) T-TESTS
#########################

cat(paste0(rep("*", 15)))
cat("\t\tPERFORMING T-TESTS\t\t")
cat(paste0(rep("*", 15)))

r.nn1 <- merged$nouns1[merged$party=="R"]
d.nn1 <- merged$nouns1[merged$party != "R"]

r.nn2 <- merged$nouns2[merged$party=="R"]
d.nn2 <- merged$nouns2[merged$party != "R"]

## 3.1) Just nouns:
# 3.1a) null = 0%
nn01a.ttest <- t.test(x = r.nn1, y = d.nn1, mu = 0.00, var.equal = FALSE)

# 3.1b) null = 1%:
nn01b.ttest <- t.test(x = r.nn1, y = d.nn1, mu = 0.01, var.equal = FALSE)

## 3.2) Nouns & Proper nouns:
# 3.2a) null = 0%
nn02a.ttest <- t.test(x = r.nn2, y = d.nn2, mu = 0.00, var.equal = FALSE)

# 3.2b) null = 1%:
nn02b.ttest <- t.test(x = r.nn2, y = d.nn2, mu = 0.01, var.equal = FALSE)


#########################
### 4) REGRESSION
#########################

## 4.1) Clean variables:
# 4.1a) make ratios into percentages
merged$nouns1 <- merged$nouns1 * 100
merged$nouns2 <- merged$nouns2 * 100
# 4.1b) binary party & scale word counts
merged$Repub <- ifelse(merged$party == "R", 1, 0)
merged$ctr_ntoks <- (log(merged$ntoks) - mean(log(merged$ntoks))) / sd(log(merged$ntoks))

## 4.2) Modeling
# 4.2a) just nouns
nn01a.lm <- lm(nouns1 ~ ctr_ntoks + Repub, data = merged)
nn01b.lm <- lm(nouns1 ~ ctr_ntoks * Repub, data = merged)
# 4.2b) nouns & proper
nn02a.lm <- lm(nouns2 ~ ctr_ntoks + Repub, data = merged)
nn02b.lm <- lm(nouns2 ~ ctr_ntoks * Repub, data = merged)



#########################
### 5) PRINTING T-TESTS
#########################

cat("\n\t******T-tests******")

## 5.1) Printing Just Nouns:
# 5.1a) null = 0%
cat("\n\nJust Nouns:\n\tNull = 0:")
print(nn01a.ttest)
# 5.1b) null = 0%
cat("\n\nJust Nouns:\n\tNull = 0.01:")
print(nn01b.ttest)

## 5.2) Printing Nouns & Proper:
# 5.2a) null = 0%
cat("\n\nNouns & Proper:\n\tNull = 0:")
print(nn02a.ttest)
# 5.2b) null = 0%
cat("\n\nNouns & Proper:\n\tNull = 0.01:")
print(nn02b.ttest)


#########################
### 6) PRINTING REGRESSIONS
#########################

cat("\n\t****** OLS MODELS ******")
cat("\n\t    * Scaled to % *")

## 6.1) Printing Just Nouns:
# 6.1a) null = 0%
cat("\n\nJust Nouns:\n\tAdditive:")
print(summary(nn01a.lm))
# 6.1b) null = 0%
cat("\n\nJust Nouns:\n\tInteractive:")
print(summary(nn01b.lm))

## 6.2) Printing Nouns & Proper:
# 6.2a) null = 0%
cat("\n\nNouns & Proper:\n\tAdditive:")
print(summary(nn02a.lm))
# 6.2b) null = 0%
cat("\n\nNouns & Proper:\n\tInteractive:")
print(summary(nn02b.lm))


## Stop logging:
cat("\n\n\tDONE!!")
sink()

