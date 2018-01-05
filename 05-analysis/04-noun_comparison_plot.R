## Author: Ryan McMahon
## Date Created: 11/28/2017
## Date Last Modified: 11/28/2017
## File: "~/05-analysis/03-noun_comparison_plot.R"

## Purpose: 
##      Generates a plot comparing partisan differences in noun usage 
##      from Cichocka et al. (2016) and this study. Simulates confidence 
##      interval for Cichocka et al. using summary statistics (2016, 809).
##      Simulations assume normal distribution in ratios, which is what I 
##      observed in Senate data. Additionally, t-statistics from these 
##      simulations match up with what is reported in their paper.
##

## Edits:
##      
##        
## 

## Local Software Information:
## R version 3.4.0 (2017-04-21) -- "You Stupid Darkness"
## Copyright (C) 2017 The R Foundation for Statistical Computing
## Platform: x86_64-w64-mingw32/x64 (64-bit)

################################################################################

rm(list = ls())
set.seed(11243)

#########################
### 0) LOAD + PROCESS SENATE RESULTS
#########################

# read in data
load("D:/cong_text/final_pos/analysis/noun_ratios.RData")

# scale diff in means to be percentage points
allnn.mu <- (allnn.ttest$estimate[1] - allnn.ttest$estimate[2]) * 100
noprop.mu <- (noprop.ttest$estimate[1] - noprop.ttest$estimate[2]) * 100


#########################
### 1) CONSTRUCT CICHOCKA ET AL. RESULTS
#########################

## 1.a) Parameters from Cichocka et al. (2016, 809)
R.n <- 45
R.mean <- 0.26
R.sd <- 0.02

D.n <- 56
D.mean <- 0.25
D.sd <- 0.01


## 1.b) Simulate confidence intervals for t-test:

# number of sims and var holding results
B <- 1001
diffs <- NA

# Simulate `B` times
for (i in 1:B){
  
  R <- rnorm(R.n, R.mean, R.sd)
  D <- rnorm(D.n, D.mean, D.sd)
  
  diffs[i] <- mean(R) - mean(D)
  
}

## 1.c) Process simulation results:

# Sort diffs in means, then get vals from 0.025, 0.5, and 0.975 quantiles;
# also, scale them to percentage points.
diffs <- sort(diffs)
Cich.ci <- diffs[c(14,988)] * 100
Cich.mu <- median(diffs) * 100



#########################
### 2) MAKE PLOT
#########################


pdf(file = "D:/Dropbox/Dissertation/02-pos_senate/02-writing/figures/01-noun_ratio_comparison.pdf", 
    width = 10.5, height = 7)

# adjust margins
par(mar=c(5,5,2,2))

# base plot
plot(x = 0, y = 0, type = "n", xlim = c(0, 2), ylim = c(-1, 2), axes = F,
     ylab = "Percentage Points Difference", xlab = "", cex.lab = 1.5,
     panel.first = grid(lwd=2.5))
axis(side = 1, at = c(0.5, 1, 1.5), cex.axis = 1.5,
     labels = c("Senate\nIncl. Proper Nouns", "Cichocka et al.\n(2016)", "Senate\nNo Proper Nouns"),
     lwd = 0, line = 1)
axis(side = 2, at = seq(-2,2,by=0.5), cex.axis = 1.5)
lines(x = c(0, 2), y = c(0, 0))

# diff in means as points
points(x = c(0.5, 1, 1.5), y = c(allnn.mu, Cich.mu, noprop.mu), pch = c(21, 23, 21), 
       bg = c("steelblue", "orangered2", "steelblue"), cex = 1.5, col = NA)

# confidence intervals
lines(x = c(0.5, 0.5), y = allnn.ttest$conf.int * 100, lwd = 3, col = "steelblue")
lines(x = c(1.0, 1.0), y = Cich.ci, lwd = 3, col = "orangered2")
lines(x = c(1.5, 1.5), y = noprop.ttest$conf.int * 100, lwd = 3, col = "steelblue")


dev.off()
