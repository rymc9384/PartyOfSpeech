#!/bin/bash

for file in *.pbs;
do
	echo "Processing $file file..."
	dos2unix $file
	qsub $file
	
	# I don't fully understand this
	#JOB=`qsub -A open ~/work/cong_text/03-topic_modeling/ExpAgenda/`

	echo "JobID = ${JOB} for batch $file submitted on `date`";
done
exit
