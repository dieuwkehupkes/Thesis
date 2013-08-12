#!/bin/bash

echo -n > $2

#For ever label in, compute how many times it occurs in the parses
for label in 'cc' 'number' 'ccomp' 'prt' 'num' 'nsubjpass' 'csubj' 'conj' 'amod' 'nn' 'neg' 'mark' 'discourse' 'auxpass' 'infmod' 'mwe' 'advcl' 'aux' 'prep' 'parataxis' 'rel' 'nsubj' 'rcmod' 'advmod' 'punct' 'quantmod' 'tmod' 'acomp' 'pcomp' 'csubjpass' 'poss' 'npadvmod' 'xcomp' 'cop' 'attr' 'partmod' 'dep' 'appos' 'det' 'dobj' 'pobj' 'iobj' 'expl' 'predet' 'preconj';
do
	echo -n "$label\t\t" >> $2
	VAR1=$(grep -oc "$label-head" $1) # >> $2
	VAR2=$(grep -oc $label $1)
	expr $VAR2 - $VAR1 >> $2
done

