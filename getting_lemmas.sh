#!/bin/bash

# bash getting_lemmas.sh en data/documents/en/article

# language=$1
# documents_dir=$2

# for filename in $documents_dir/*
# do 
# 	echo $(basename $filename)
# 	output=data/FreeLing_outputs/$language/$(basename $filename)
# 	analyzer_client 50005 < $filename > $output
# done

# echo "\n\nExtracting the lemmas..."
# python getting_lemmas.py



declare -a languages=("en" "es")
for language in "${languages[@]}"
do
	echo $language
	documents_dir=data/documents/$language/article
	for filename in $documents_dir/*
	do 
		echo $(basename $filename)
		output=data/FreeLing_outputs/$language/$(basename $filename)
		if [ "$language" == "en" ]
		then
			analyzer_client 50005 < $filename > $output
		else
			analyzer_client 50006 < $filename > $output
		fi
	done
done
