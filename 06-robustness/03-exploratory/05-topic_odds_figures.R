## Author: Ryan McMahon
## Date Created: 05/28/2018
## Date Last Modified: 05/29/2018
## File: "~/06-robustness/03-exploratory/05-topic_odds_figures.R"

## Purpose: This script odds-ratios for different stylistic frames across the 
##          corpus.
##          
##

## Edits:
##        05/29/18) Make x-axis labels more accurately reflect meaning
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

rm(list=ls())
options(stringsAsFactors = F)
setwd("D:/")


topics <- read.csv("./Dropbox/Dissertation/02-pos_senate/01-code/PartyOfSpeech/03-topic_modeling/ExpAgenda/topic_labeling/topic_summary_table_114.csv", encoding='utf8')
verbs <- read.csv("./cong_text/final_pos/analysis/114zetas_deltas_vrbtense_feats.csv", encoding='utf8')
prps <- read.csv("./cong_text/final_pos/analysis/114zetas_deltas_prpnum_feats.csv")


verbs$pastOR <- ( exp(verbs$VBPASTdelta) - 1 ) * 100
verbs$futOR <- ( exp(verbs$VBFUTdelta) - 1 ) * 100
verbs$pastSE <- (verbs$VBPASTdelta / verbs$VBPASTzeta) * 100
verbs$futSE <- (verbs$VBFUTdelta / verbs$VBFUTzeta) * 100

prps$singOR <- ( exp(prps$PRPSINGdelta) - 1 ) * 100
prps$plurOR <- ( exp(prps$PRPPLURdelta) - 1 ) * 100
prps$singSE <- (prps$PRPSINGdelta / prps$PRPSINGzeta) * 100
prps$plurSE <- (prps$PRPPLURdelta / prps$PRPPLURzeta) * 100


### Past Tense Verbs Plot:

pdf(file = "./Dropbox/Dissertation/02-pos_senate/02-writing/02-main/figures/05a-past_odds.pdf", width = 9.5, height = 9)

par(mfrow=c(1,1))
par(mar=c(5,1,0,0))
plot(x = 0, y = 0, type = "n", xlim = c(-12, 12), ylim = c(0, 50), axes=F, 
     xlab = "% Point Change in Odds", 
     ylab = "", main = "", cex.lab = 1.5)

axis(side = 1, at = seq(-12,12,4),  cex.axis=1.5)
mtext(text = "Topic", side = 2, line = -1, at = 25, cex = 1.5)

lines(x = c(0,0), y = c(1,50), lty = "dotted", col = "gray70")
lines(x = c(-8, 8), y = c(47.5, 47.5), lty = "dotted", col = "gray70", lwd = 2)

# all topics 
points(x = verbs$pastOR[1], y = 50, pch = 22, bg = "orangered2", cex = 1.5)
lines(x = c(verbs$pastOR[1] - 1.96*verbs$pastSE[1], verbs$pastOR[1] + 1.96*verbs$pastSE[1]), y = c(50, 50), lwd = 2, col = "orangered2")
text(x = 5, y = 50, labels = "All topics", pos = 2)

# individual topics
points(x = sort(verbs$pastOR[-1]), y = 45:1, pch=21, bg = ifelse(sign(sort(verbs$pastOR[-1])) == 1, "orangered2", "steelblue"), cex=1.5)

j <- 45
tmp <- verbs[-1,]
tmp <- tmp[order(tmp$pastOR, decreasing = F),]
for(i in 1:45){
  
  tmpx <- c(tmp$pastOR[i] - 1.96*tmp$pastSE[i], tmp$pastOR[i] + 1.96*tmp$pastSE[i])
  tmplab <- topics$label[tmp$topic[i]]
  tmplab <- unlist(strsplit(tmplab, ""))
  tmplab[1] <- toupper(tmplab[1])
  tmplab <- paste0(tmplab, collapse = "")
  
  lines(x = tmpx, y = c(j,j), lwd = 2, 
        col = ifelse(sign(tmp$pastOR[i]) == 1, "orangered2", "steelblue"))
  
  
  text(x = tmpx[1], y = j, labels = tmplab, pos=2)
  
  j <- j - 1
  
}

dev.off()



### Future Tense Verbs Plot:

pdf(file = "./Dropbox/Dissertation/02-pos_senate/02-writing/02-main/figures/05b-future_odds.pdf", width = 9.5, height = 9)


par(mfrow=c(1,1))
par(mar=c(5,0,0,0))
plot(x = 0, y = 0, type = "n", xlim = c(-16, 16), ylim = c(0, 50), axes=F, 
     xlab = "% Point Change in Odds", 
     ylab = "", main = "", cex.lab = 1.5)
axis(side = 1, at = seq(-12,12,4), cex.axis=1.5)
mtext(text = "Topic", side = 2, line = -4, at = 25, cex = 1.5)

lines(x = c(0,0), y = c(1,50), lty = "dotted", col = "gray70")
lines(x = c(-10, 10), y = c(47.5, 47.5), lty = "dotted", col = "gray70", lwd = 2)

# all topics 
points(x = verbs$futOR[1], y = 50, pch = 22, bg = "steelblue", cex = 1.5)
lines(x = c(verbs$futOR[1] - 1.96*verbs$futSE[1], verbs$futOR[1] + 1.96*verbs$futSE[1]), y = c(50, 50), lwd = 2, col = "steelblue")
text(x = -3.5, y = 50, labels = "All topics", pos = 2)

points(x = sort(verbs$futOR[-1]), y = 45:1, pch=21, bg = ifelse(sign(sort(verbs$futOR[-1])) == 1, "orangered2", "steelblue"), cex=1.5)

j <- 45
tmp <- verbs[-1,]
tmp <- tmp[order(tmp$futOR, decreasing = F),]
for(i in 1:45){
  
  tmpx <- c(tmp$futOR[i] - 1.96*tmp$futSE[i], tmp$futOR[i] + 1.96*tmp$futSE[i])
  tmplab <- topics$label[tmp$topic[i]]
  tmplab <- unlist(strsplit(tmplab, ""))
  tmplab[1] <- toupper(tmplab[1])
  tmplab <- paste0(tmplab, collapse = "")
  
  lines(x = tmpx, y = c(j,j), lwd = 2, 
        col = ifelse(sign(tmp$futOR[i]) == 1, "orangered2", "steelblue"))
  
  
  text(x = tmpx[2], y = j, labels = tmplab, pos=4)
  
  j <- j - 1
  
}

dev.off()



### Singular Pronouns Plot:

pdf(file = "./Dropbox/Dissertation/02-pos_senate/02-writing/02-main/figures/05c-singular_odds.pdf", width = 9.5, height = 9)

par(mfrow=c(1,1))
par(mar=c(5,0,0,0))
plot(x = 0, y = 0, type = "n", xlim = c(-5, 40), ylim = c(0, 50), axes=F, 
     xlab = "% Point Change in Odds", 
     ylab = "", main = "", cex.lab = 1.5)

axis(side = 1, at = seq(-5,40,5), cex.axis=1.5)
#mtext(text = expression("Odds-Ratio        " %->% "        More Republican"), 
#      side = 1, line = 3, at = -3.5, adj = 0, cex = 1.5)
mtext(text = "Topic", side = 2, line = -2, at = 25, cex = 1.5)

lines(x = c(0,0), y = c(1,50), lty = "dotted", col = "gray70")
lines(x = c(-5, 40), y = c(47.5, 47.5), lty = "dotted", col = "gray70", lwd = 2)

# all topics 
points(x = prps$singOR[1], y = 50, pch = 22, bg = "orangered2", cex = 1.5)
lines(x = c(prps$singOR[1] - 1.96*prps$singSE[1], prps$singOR[1] + 1.96*prps$singSE[1]), y = c(50, 50), lwd = 2, col = "orangered2")
text(x = 25, y = 50, labels = "All topics", pos = 2)

# individual topics
points(x = sort(prps$singOR[-1]), y = 45:1, pch=21, bg = ifelse(sign(sort(prps$singOR[-1])) == 1, "orangered2", "steelblue"), cex=1.5)

j <- 45
tmp <- prps[-1,]
tmp <- tmp[order(tmp$singOR, decreasing = F),]
for(i in 1:45){
  
  tmpx <- c(tmp$singOR[i] - 1.96*tmp$singSE[i], tmp$singOR[i] + 1.96*tmp$singSE[i])
  tmplab <- topics$label[tmp$topic[i]]
  tmplab <- unlist(strsplit(tmplab, ""))
  tmplab[1] <- toupper(tmplab[1])
  tmplab <- paste0(tmplab, collapse = "")
  
  lines(x = tmpx, y = c(j,j), lwd = 2, 
        col = ifelse(sign(tmp$singOR[i]) == 1, "orangered2", "steelblue"))
  
  if (i < 23){
    text(x = tmpx[2], y = j, labels = tmplab, pos=4)
  } else{
    text(x = tmpx[1], y = j, labels = tmplab, pos=2)
  }
  
  
  j <- j - 1
  
}

dev.off()



### Plural Pronouns  Plot:

pdf(file = "./Dropbox/Dissertation/02-pos_senate/02-writing/02-main/figures/05d-plural_odds.pdf", width = 9.5, height = 9)


par(mfrow=c(1,1))
par(mar=c(5,0,0,0))
plot(x = 0, y = 0, type = "n", xlim = c(-17, 17), ylim = c(0, 50), axes=F, 
     xlab = "% Point Change in Odds", 
     ylab = "", main = "", cex.lab = 1.5)
axis(side = 1, at = seq(-15,15,5), cex.axis=1.5)
mtext(text = "Topic", side = 2, line = -3, at = 25, cex = 1.5)

lines(x = c(0,0), y = c(1,50), lty = "dotted", col = "gray70")
lines(x = c(-10, 10), y = c(47.5, 47.5), lty = "dotted", col = "gray70", lwd = 2)

# all topics 
points(x = prps$plurOR[1], y = 50, pch = 22, bg = "steelblue", cex = 1.5)
lines(x = c(prps$plurOR[1] - 1.96*prps$plurSE[1], prps$plurOR[1] + 1.96*prps$plurSE[1]), y = c(50, 50), lwd = 2, col = "steelblue")
text(x = -3.5, y = 50, labels = "All topics", pos = 2)

points(x = sort(prps$plurOR[-1]), y = 45:1, pch=21, bg = ifelse(sign(sort(prps$plurOR[-1])) == 1, "orangered2", "steelblue"), cex=1.5)

j <- 45
tmp <- prps[-1,]
tmp <- tmp[order(tmp$plurOR, decreasing = F),]
for(i in 1:45){
  
  tmpx <- c(tmp$plurOR[i] - 1.96*tmp$plurSE[i], tmp$plurOR[i] + 1.96*tmp$plurSE[i])
  tmplab <- topics$label[tmp$topic[i]]
  tmplab <- unlist(strsplit(tmplab, ""))
  tmplab[1] <- toupper(tmplab[1])
  tmplab <- paste0(tmplab, collapse = "")
  
  lines(x = tmpx, y = c(j,j), lwd = 2, 
        col = ifelse(sign(tmp$plurOR[i]) == 1, "orangered2", "steelblue"))
  
  
  text(x = tmpx[2], y = j, labels = tmplab, pos=4)
  
  j <- j - 1
  
}

dev.off()

