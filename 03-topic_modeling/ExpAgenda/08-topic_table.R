## Author: RBM
## Date Created: 11/20/2017
## Date Last Modified: 11/20/2017
## File: "~/03-topic_modeling/ExpAgenda/08-topic_table.R"
##
## PURPOSE: This code calculates descriptive statistics for the topic model
##          and outputs the data in a format for easy conversion to latex table. 
##          Also copies best run data to new "final model" file.
##
## NOTES: 
## 
##
## EDITS:
##        
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

## "optparse" package: 1.4.4 (depends on "getopt" package: 1.20.0)

################################################################################


rm(list = ls())
library(optparse)
options(stringsAsFactors = FALSE)

set.seed(11769)

## Parse command line arguments:
option_list <- list(
  make_option(c("-b", "--bounds"), type="character", default="./num_topics/lower_bounds_114.RData", 
              help="lower bounds rdata file [default= %default]", metavar="character"),
  make_option(c("--labeled"), type="character", default="./topic_labeling/labeled_topics_114.csv", 
              help="path to textsDF w/ topic numbers will be stored [default= %default]", metavar="character"),
  make_option(c("--outmodel"), type="character", default="D:/cong_text/rdata/topic_modeling/best_run_114.RData", 
              help="filename and path for best run model data [default= %default]", metavar="character"),
  make_option(c("--outtable"), type="character", default="./topic_labeling/topic_summary_table_114.csv", 
              help="filename and path for output summary table [default= %default]", metavar="character")
) 

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


#############################################
### 0) SET UP ENVIRONMENT
#############################################

message("Setting up the environment...")

## Load lower-bounds data (run_summary):
load(opt$bounds)



#############################################
### 1) FUNCTIONS
#############################################

message("Defining functions...")


## 1.a) Index of Maximum:
w_max <- function( x ){
  
  ##################
  ## ARGS:
  # 1) x (vector) = vector of sortable values
  #
  ##################
  
  return( which(x == max(x)) )
  
}


## 1.b) Get topic/stem assignments:
max_index <- function( x ){
  
  ##################
  ## ARGS:
  # 1) x (matrix, n x K) = matrix of topic probabilities; n = D or |V|
  # 
  #
  ##################
  
  max_t <- apply(X = x, MARGIN = 1, FUN = w_max)
  
  return(max_t)
  
}




#############################################
### 2) EVALUATE BOUNDS
#############################################

message("Selecting best run and loading fit...")


## 2.a) Which run has max lower-bound:
best.run <- w_max(run_summary$lower.bound)

message(paste0("Best run: ", run_summary$file[best.run]))

## 2.b) Load that run (expAgenda):
load(run_summary$file[best.run]) 



#############################################
### 3) LOAD LABELED TOPICS
#############################################

message("Reading in labeled topics...")

labeled <- read.csv(opt$labeled)



#############################################
### 4) CALCULATE DESCRIPTIVES
#############################################

## 4.a) Topic proportions:
max.topic <- max_index(x = expAgenda$rs)
topic.props <- round( prop.table( table(max.topic) ) * 100, 2 )


## 4.b) Stem proportions:
max.stem <- max_index(x = expAgenda$mus)
stem.props <- round( prop.table( table(max.stem) ) * 100, 2 )


## 4.c) Topic probabilities:
p.topics <- NA

for (i in seq_along(max.topic)){
  p.topics[i] <- expAgenda$rs[i, max.topic[i]]
}
q.topics <- round(quantile(p.topics, c(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.975, 0.999)), 3)

message("\n\n# Quantiles\n0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.975, 0.999")
message(paste(q.topics, collapse=" "))



#############################################
### 5) FORMAT FOR TABLE
#############################################

message("\n\nGenerating table with descriptives...")

## 5.a) Trim down labeled topics table:
outtable <- labeled[,c("topic", "label", "stems", "notes")]

# take only top 5 stems
for (i in seq_along(outtable$stems)){

  tmp_stems <- unlist(strsplit(outtable$stems[i], ", "))
  tmp_stems <- paste(tmp_stems[1:5], collapse=", ")
  
  outtable$stems[i] <- tmp_stems
  
}


## 5.b) Create topic/stem proportions:

outtable$proportions <- NA
for (i in seq_along(topic.props)){
  
  outtable$proportions[i] <- paste0(topic.props[i], " / ", stem.props[i])
  
}


#############################################
### 6) SAVING
#############################################



message("Saving best run data...")
save(expAgenda, file = opt$outmodel)

message("Saving formatted table...")
write.csv(x = outtable, file = opt$outtable, row.names = FALSE)


message("\n\nDONE!")
