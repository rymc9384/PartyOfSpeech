## Author: RBM
## Date Created: 10/05/2017
## Date Last Modified: 10/05/2017
## File: "~/03-topic_modeling/ExpAgenda/01-estimating_ExpAgenda.R"
##
## PURPOSE: This script estimates the Expressed Agenda topic model (Grimmer 2010)
##          using the formatted press release text. 
##
## NOTES: 
##       10/05/17) Run on Penn State's HPC cluster. The software information 
##                 listed below reflects what is installed on that system, 
##                 thus the R platform being linux instead of windows. 
##                 Descriptions of package versions are available in the log 
##                 files.
##                  
##
## EDITS:
##        
##

## Software Information:

## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-redhat-linux-gnu (64-bit)

################################################################################


rm(list=ls())
library(DataCombine, lib.loc = "/storage/home/rbm166/R/x86_64-redhat-linux-gnu-library/3.4")
library(MCMCpack, lib.loc = "/storage/home/rbm166/R/x86_64-redhat-linux-gnu-library/3.4")
library(optparse, lib.loc = "/storage/home/rbm166/R/x86_64-redhat-linux-gnu-library/3.4")
options(stringsAsFactors = F)

time.str <- gsub(pattern = " ", replacement = "_", x = Sys.time())
outfile.default <- paste0("modelfit_", time.str, "_114.RData") 
logfile.default <- paste0("modellog_", time.str, "_114.Rout")


## Parse command line arguments:
option_list <- list(
  make_option(c("-t", "--topics"), type="integer", default=NULL, 
              help="Number of topics to fit [default=%default]", metavar="character"),
  make_option(c("-k", "--kappa"), type="integer", default=100, 
              help="vMF dispersion parameter [default=%default]", metavar="character"),
  make_option(c("-d", "--delta"), type="double", default=0.0001, 
              help="Tolerance for change in Mus to accept convergence [default=%default]", metavar="character"),
  make_option(c("-i", "--infile"), type="character", default="./Processed/ExpAgenda_Processed_114.RData", 
              help="Formatted ExpAgenda object RData [default=%default]", metavar="character"),
  make_option(c("-op", "--outpath"), type="character", default="./Fits/114/", 
              help="output directory [default= %default]", metavar="character"),
  make_option(c("-of", "--outfile"), type="character", default=outfile.default, 
              help="processed output file name [default= %default]", metavar="character"),
  make_option(c("-lp", "--logpath"), type="character", default="./Logs/", 
              help="log directory [default= %default]", metavar="character"),
  make_option(c("-lf", "--logfile"), type="character", default=logfile.default, 
              help="log file name [default= %default]", metavar="character")
  )

opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)


## Start logging:
if (!dir.exists(opt$logpath)){
  dir.create(path = opt$logpath, recursive = TRUE)
}

logfile.full <- paste0(opt$logpath, opt$logfile)
sink(file = logfile.full)


## Display package versions and other environment information:
cat("\tSession info:\n")
sessionInfo()


## Execute the model script from Grimmer (2010):
cat("\n\n\tExecuting model script...\n")
source(file = "./ExpAgenda-master/R/ExpAgendaVonmon.R")


## Read in formatted data:
cat(paste0("\n\n\tReading in ", opt$infile, "...\n"))
load(file = opt$infile)


## Fit model:
set.seed(11769)
cat(paste0("\n\n\tFitting model with ", opt$topics, " topics, a kappa of ", opt$kappa, ", and delta of ", opt$delta, "...\n"))
expAgenda <- ExpAgendaVonmon(obj = processed, n.cats = opt$topics, kappa = opt$kappa, 
                             verbose = T, tol_afr = opt$delta)


## Save fit:
if (!dir.exists(opt$outpath)){
  dir.create(path = opt$outpath, recursive = TRUE)
}

cat(paste0("\n\n\tSaving output to ", opt$outpath, opt$outfile, "...\n"))
setwd(opt$outpath)
save(expAgenda, file = opt$outfile)


## Stop logging:
cat("\n\n\tDONE!!")
sink()
