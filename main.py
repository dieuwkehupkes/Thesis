from scoring import *

all_dependencies = 'Data/dependencies.en.head100'
all_sentences = 'Data/aligned.0.en.head20'
all_alignments = 'Data/alignments.head20'

dependency_file = open(all_dependencies,'r')
sentence_file = open(all_sentences,'r')
alignment_file = open(all_alignments,'r')
results = open('results','w')

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
	if sentence_length < 16:
		scoring = Scoring(new_alignment, new_sentence, dependency_list)
		results.write(str(scoring.score)+'\n')
	else:
		results.write("sentence longer than 15 words\n")
	new_alignment = alignment_file.readline()
	new_sentence = sentence_file.readline()
	new_dependent = dependency_file.readline()
	
