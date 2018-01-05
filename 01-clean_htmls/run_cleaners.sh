#!/bin/bash

i=0
max=100
while [ $i -lt $max ]
do
   echo "Processing Senator $i..."
   ~/../../mnt/c/Anaconda3/envs/textcleaning/python.exe run_cleaners.py --html-path D:/cong_text/htmls --number $i --output D:/cong_text/csvs --rmprepost y --rmquotes n >run_cleaners.out
   i=$(( $i + 1 ))
done
