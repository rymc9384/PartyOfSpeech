## Author: RBM
## Date Created: 10/05/2017
## Date Last Modified: 10/05/2017
## File: "~/03-topic_modeling/ExpAgenda/03-writing_PBS_scripts.R"
##
## PURPOSE: This script takes the general PBS script, for submitting the 
##          `01-estimating_ExpAgenda.R` script to the HPC, and generates new PBS 
##          scripts that vary the number of topics being estimated (between 30 
##          and 60) what corpus is being modeled (the 113th or 114th Congress).
##          It then writes those scripts to new folders so that they can be 
##          called by `02-ExpAgenda_submitter.sh` on the HPC.
##
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

################################################################################

rm(list=ls())

##############################
### 1) SET UP
##############################

## Read in the general PBS script:
base.script <- readLines(con = "./general_pbs_script.txt", encoding = "utf-8", warn = F)
base.script <- paste(base.script, collapse = "\n")


## Create data frame with values to insert into the script:
congress <- c(113, 114)
topics <- seq(from = 30, to = 60, by=1)
X <- expand.grid( list("congress"=congress, "topics"=topics) )
X$file <- paste0("ExpAgenda_", X$topics, "topics_", X$congress, ".pbs")



##############################
### 2) Create New Scripts:
##############################

## Add empty vector that will hold the new scripts:
X$script <- NA


## Loop over combinations and generate scripts:
for ( i in 1:nrow(X) ){
  
  text <- base.script
  text <- gsub(pattern = "TOPICS", replacement = X$topics[i], x = text, ignore.case = F)
  text <- gsub(pattern = "CONG", replacement = X$congress[i], x = text, ignore.case = F)
  X$script[i] <- text
  
}


## Create folders to hold the PBS scripts (if they don't exist):
for ( cong in congress ){

  outdir <- paste0("./pbs_scripts/", cong, "/")
  
  if ( !dir.exists(outdir) ){
    dir.create(path = outdir, recursive = T)
  }
  
}


## Write out scripts:
for ( cong in congress ){
  
  # subset by congress
  temp.df <- X[which(X$congress == cong), ]
  
  # loop over congress specific rows:
  for ( i in 1:nrow(temp.df) ){
    
    outfile <- paste0("./pbs_scripts/", cong, "/", temp.df$file[i])
    writeLines(text = temp.df$script[i], con = outfile)
    
  }
  
}

