#!/bin/bash

cat << "EOF" > $7
#Chrom	Pos	Ref	Alt	RawScore	PHRED
1	100	A	G	0.1	0.1
1	200	C	T	0.2	0.2
EOF

gzip -c $7 > $7.tmp
mv $7.tmp $7
