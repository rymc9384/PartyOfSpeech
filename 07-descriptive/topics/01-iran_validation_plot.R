## Author: Ryan McMahon
## Date Created: 11/30/2017
## Date Last Modified: 11/30/2017
## File: "~/07-descriptive/topics/01-iran_validation_plot.R"

## Purpose: 
##      Generates a plot of how many press releases from the "Iran Deal" topic 
##      are put out each day. Major events regarding the nuclear deal are shown 
##      to line up with spikes in releases.
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

rm(list=ls())
options(stringsAsFactors = F)


## Read in doc topic data:
df <- read.csv("D:/cong_text/csvs/topics/ExpAgenda_Topics_114.csv")

## Format dates:
df$form_date <- as.Date(x = df$form_date, format = "%Y-%m-%d")



### IRAN DEAL:
## Events (per Arms Control Association: https://www.armscontrol.org/factsheet/Timeline-of-Nuclear-Diplomacy-With-Iran)
# March 4, 2015 - Previous day, Netanyahu gives speech to joint session of Cong.
# April 14, 2015 - Senate Foreign Relations Committee unanimously passes Corker leg
# May 7, 2015 - Senate passes the Corker legislation 98-1 on congressional review of an Iran nuclear deal.
# July 14, 2015 - deal signed in Vienna
# July 22, 2015 - criticism of "side deals"
# July 14, 2016 - anniversary of deal signing

iran.keys <- c("2015-03-04", "2015-04-14", "2015-05-07", "2015-07-14", "2016-07-14")

## Create subset of Iran releases:
iran.df <- df[df$topic == 8, ]

## Article counts by date:
iran.tab <- table(iran.df$form_date)


pdf(file = "D:/Dropbox/Dissertation/02-pos_senate/02-writing/figures/02-iran_event_validation.pdf", 
    width = 13, height = 5)

par(mar = c(5,4,2,2))

iran.bar <- as.data.frame(barplot(height = iran.tab, ylim = c(0, 22), 
                                  ylab = "Counts", xlab = "Date (Y-M-D)", 
                                  space = 0, width = 1, names.arg = ""))
iran.bar$dates <- as.character(sort(unique(iran.df$form_date)))
iran.bar <- iran.bar[iran.bar$dates %in% iran.keys, ]

axis(side = 1, at = iran.bar$V1[-2], labels = iran.keys[-2])
text(x = iran.bar$V1[1], y = iran.tab[names(iran.tab) == iran.bar$dates[1]] + 2, labels = "Netanyahu speech")
text(x = iran.bar$V1[2], y = iran.tab[names(iran.tab) == iran.bar$dates[2]], labels = "FRC Vote")
text(x = iran.bar$V1[3], y = iran.tab[names(iran.tab) == iran.bar$dates[3]] + 1, labels = "Senate Vote")
text(x = iran.bar$V1[4], y = iran.tab[names(iran.tab) == iran.bar$dates[4]] + 1, labels = "Deal Signed")
text(x = iran.bar$V1[5], y = iran.tab[names(iran.tab) == iran.bar$dates[5]] + 1, labels = "Anniversary of Signing")


dev.off()