from scoring import *
import sys #Adapt later such that files and parameters can be entered via commandline

all_dependencies = 'Data/europarl.dependencies.en.head100'
all_sentences = 'Data/europarl-v7.nl-en.en.head100'
all_alignments = 'Data/europarl-v7-alignments.en-ne.head100'

dependency_file = open(all_dependencies,'r')
sentence_file = open(all_sentences,'r')
alignment_file = open(all_alignments,'r')
results = open('results','w')
trees = open('trees','w')

# Go through the files and for every line in the file containing
# the alignments, compute the score. Count to keep sentences
# and alignments together

new_alignment = alignment_file.readline()
new_sentence = sentence_file.readline()
new_dependent = dependency_file.readline()
sentence_nr = 0

while new_alignment != '':
	sentence_nr += 1
	print sentence_nr
	#find dependencies
	dependency_list = []
	while new_dependent != '\n' and new_dependent != '':
		dependency_list.append(new_dependent)
		new_dependent = dependency_file.readline()
	#score sentence
	sentence_length = len(new_sentence.split())
	if sentence_length < 20:
		scoring = Scoring(new_alignment, new_sentence, dependency_list)
		results.write(str(scoring.score)+'\n')
		trees.write(str(scoring.parse)+'\n')
	else:
		results.write("No result, sentence longer than 15 words\n")
	new_alignment = alignment_file.readline()
	new_sentence = sentence_file.readline()
	new_dependent = dependency_file.readline()

results.close()



all_dependencies = 'Data/europarl.dependencies.en.head100'
all_sentences = 'Data/europarl-v7.nl-en.en.head100'
all_alignments = 'Data/europarl-v7-alignments.en-ne.head100'

dependency_file = open(all_dependencies,'r')
sentence_file = open(all_sentences,'r')
alignment_file = open(all_alignments,'r')
results = open('results','w')
trees = open('trees','w')

