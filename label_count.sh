#!/bin/bash

echo -n > $2

#For ever label in, compute how many times it occurs in the parses
for label in 'cc' 'number' 'ccomp' 'prt' 'num' 'nsubjpass' 'csubj' 'conj' 'amod' 'nn' 'neg' 'mark' 'auxpass' 'infmod' 'mwe' 'advcl' 'aux' 'prep' 'parataxis' 'nsubj' 'rcmod' 'advmod' 'quantmod' 'tmod' 'acomp' 'pcomp' 'poss' 'npadvmod' 'xcomp' 'cop' 'attr' 'partmod' 'dep' 'appos' 'det' 'dobj' 'pobj' 'iobj' 'expl' 'predet' 'preconj';
do
	echo -n "$label\t\t" >> $2
	cat Testing/trees | grep -oc nsubj
	cat $1 | grep -oc $label >> $2
done

