## Author: Ryan McMahon
## Date Created: 11/27/2017
## Date Last Modified: 04/03/2018
## File: "~/05-analysis/03-fightin_tables.R"

## Purpose: 
##      
##

## Edits:
##        04/03/18) Modify to accomodate the in-data having zeta and delta 
##                  columns
##        
## 

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################

rm(list=ls())
options(stringsAsFactors = F)

#########################
### 0) FUNCTIONS + CONSTANTS
#########################

## 0.a) Constants
# intertopic
R.ZETA1 <- 4.42
D.ZETA1 <- -4.42

# intratopic
R.ZETA2 <- 3.29
D.ZETA2 <- -3.29


## 0.b) Topic significance

topicsig <- function(zetas, cutR=R.ZETA2, cutD=D.ZETA2){
  
  t <- length(zetas)
  
  r <- which(zetas >= cutR)
  d <- which(zetas <= cutD)
  n <- which( 1:t %in% r == F & 1:t %in% d == F)
  
  zetas[r] <- "GOP"
  zetas[d] <- "DEM"
  zetas[n] <- "---"
  
  return(zetas)
  
}




#########################
### 1) READ IN DATA
#########################

# pronouns
prp.df <- read.csv("D:/cong_text/final_pos/analysis/114zetas_deltas_prpnum_feats.csv")
# verbs
vb.df <- read.csv("D:/cong_text/final_pos/analysis/114zetas_deltas_vrbtense_feats.csv")
# nouns
nn.df <- read.csv("D:/cong_text/final_pos/analysis/114zetas_deltas_nounnum_feats.csv")

# merge
df <- cbind(prp.df, vb.df[,-1], nn.df[,-1])

# subset inter-topic
df.inter <- df[1, ]
df <- df[-1, ]

# remove constituent frames
rm('prp.df', 'vb.df', 'nn.df')

# columns w/ zetas
zcols <- grep(pattern = "zeta", x = colnames(df))

#########################
### 2) INTERTOPIC
#########################

tab.inter <- df.inter[,c(1,zcols)]
tab.inter[1,-1] <- topicsig(zetas = tab.inter[1,-1], cutR = R.ZETA1, cutD = D.ZETA1)


#########################
### 3) INTRATOPIC
#########################

tab.intra <- df[,c(1,zcols)]

for (i in 2:7){
  
  tab.intra[,i] <- topicsig(zetas = tab.intra[,i])
  
}


#########################
### 3) SUMMARY BY COL
#########################

# get number of topics sig in predicted direction for each column
n.sig <- NA

for (i in 2:7){
  
  if (i %% 2 == 0){
    n.sig[i] <- sum(tab.intra[,i] == "GOP")
  } else{
    n.sig[i] <- sum(tab.intra[,i] == "DEM")
  }
  
}



#########################
### 4) MERGE TABLES & SAVE
#########################

tab.full <- rbind(tab.inter, tab.intra, n.sig)

write.csv(x = tab.full, file = "D:/cong_text/final_pos/analysis/114zetas_table.csv", row.names = F)
