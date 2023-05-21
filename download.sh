#!/bin/bash
# This script download all PDB files for HomodimerDB

url=https://zhanggroup.org/HomodimerDB/
for target in `curl "$url/download.cgi"|grep '<tr><td><a href=data/pdb/div/'|cut -d/ -f4|cut -d'>' -f1`;do
    echo $target
    curl $url/data/pdb/div/$target -o $target
done
