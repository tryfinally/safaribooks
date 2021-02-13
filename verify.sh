#!/bin/bash

if [[ $# != 1 ]]; then
	echo "Usage: ${0} download directory, like Books/"
	exit 1
fi

echo "Verifying $1 ..."
echo "Book that did not download"
for d in ${1}/*/  ${1}/.[^.]*/; do
	flag=0
	book=""
    for f in "${d}"* ; do
    	if [[ $f == *.epub ]]; then
    		flag=1
    		book=$f
    	fi
    done
    if [[ $flag == 0 ]]; then
    	echo "-- ${d}"
    fi
done
