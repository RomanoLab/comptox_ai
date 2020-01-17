#!/bin/bash

info_message()
{
    echo "remove_nones.sh - Remove any lines containing the string 'None' from a"
    echo "text file."
    echo ""
    echo "This is particularly useful for RDF files, since the Java parser"
    echo "included in NSMNTX raises an error when it encounters 'None'."
    echo ""
}

INPUT_FNAME = $1

check_filetype()
{
    FULL_FNAME = $1
    EXTENSION= ${FULL_FNAME##*.}
    if [ $EXTENSION = "rdf" ]
    then
        return 0
    else
        return 1
    fi
}


### Main

if check_filetype INPUT_FNAME
then
    sed -i '/None/d' INPUT_FNAME
else
    echo "Provided filename does not end in .rdf - aborting."
fi