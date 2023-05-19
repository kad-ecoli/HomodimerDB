#!/bin/bash
FILE=`readlink -e $0`
bindir=`dirname $FILE`
rootdir=`dirname $bindir`

#cat $rootdir/data/nonredundant/seqs_longer.fasta $rootdir/data/nonredundant/seqs_shorter.fasta | sed 's/;\t/\t>/g'|cut -f2|$bindir/fasta2tsv - - |sort|uniq| $bindir/tsv2fasta - $rootdir/data/nonredundant/seq.fasta 
$bindir/makeblastdb -in $rootdir/data/nonredundant/seqs.fasta -dbtype prot -out $rootdir/data/nonredundant/seqs.fasta
