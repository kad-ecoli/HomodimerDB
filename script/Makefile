CC=g++
CFLAGS=-O3
LDFLAGS=-static

all: tsv2fasta fasta2tsv

tsv2fasta: tsv2fasta.cpp
	${CC} ${CFLAGS} $@.cpp -o $@ ${LDFLAGS}

fasta2tsv: fasta2tsv.cpp
	${CC} ${CFLAGS} $@.cpp -o $@ ${LDFLAGS}
