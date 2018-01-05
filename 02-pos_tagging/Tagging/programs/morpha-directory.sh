#!/bin/sh
#
# Xiaofei Lu
#
# usage: sh morpha-directory.sh pathToDirectory options
# example: sh morpha-directory.sh ~/corpus/temp/ -t
#
# important: make sure that 1) the path to the directory ends with a slash "/", 2) the directory contains only those POS-tagged English text files (with the ".tag" suffix) to be lemmatized; and 3) there are no white spaces in your filenames
#
# the name of the tagged output file will be name of the input file plus the ".lem" suffix, e.g., sample.lem for sample.tag. 
#
# see the README file in the morph directory for available command options. 

for textfile in $1*
do
if [ "${textfile:(-4)}" != ".tag" ]; then
    continue
elif [ -z "$2" ]; then
    echo lemmatizing $textfile
    ./morpha < $textfile > ${textfile%.tag}.lem
else
    echo lemmatizing $textfile
    ./morpha $2 < $textfile > ${textfile%.tag}.lem
fi
done