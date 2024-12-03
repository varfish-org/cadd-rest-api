#!/bin/bash

cat << "EOF" > "$8"
#Chrom	Pos	Ref	Alt	RawScore	PHRED
1	100	A	G	0.1	0.1
1	200	C	T	0.2	0.2
EOF

gzip -c "$8" > "$8.tmp"
mv "$8.tmp" "$8"
