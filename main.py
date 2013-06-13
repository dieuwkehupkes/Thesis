from scoring import *
import sys #Adapt later such that files and parameters can be entered via commandline

#all_dependencies = 'Testing/test_dependency.2'
#all_sentences = 'Testing/test_sentence.2'
#all_alignments = 'Testing/test_alignment.2'
#scores = 'Testing/test_results.2'
#tree_file = 'Testing/test_trees.2'

if len(sys.argv) != 6:
	raise ValueError('nr of arguments incorrect, usage:\n python main.py dependency_file sentence_file alignment_file print_scores_to print_trees_to')


all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
scores = sys.argv[4]
tree_file = sys.argv[5]

dependency_file = open(all_dependencies,'r')
sentence_file = open(all_sentences,'r')
alignment_file = open(all_alignments,'r')
results = open(scores,'w')
trees = open(tree_file,'w')

# Go through the files and for every line in the file containing
# the alignments, compute the score and print it to a file, as well
# as the corresponding tree.


new_alignment = alignment_file.readline()
new_sentence = sentence_file.readline()
new_dependent = dependency_file.readline()

sentence_nr = 0
parsed_sentences = 0
total_score = 0

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
		print 'Initializing Dependencies'
		dependencies = Dependencies(dependency_list)
		# preferred relations
		relations = dependencies.get_comp_spanrels()
		scoring = Scoring(new_alignment, new_sentence, relations)
		results.write(str(scoring.score)+'\n')
		parse = str(scoring.parse)
		trees.write(parse +'\n\n')
		parsed_sentences += 1
		total_score += scoring.score
	else:
		results.write("No result, sentence longer than 20 words\n")
	new_alignment = alignment_file.readline()
	new_sentence = sentence_file.readline()
	new_dependent = dependency_file.readline()

average = total_score/parsed_sentences
print 'average score:', average

dependency_file.close()
sentence_file.close()
alignment_file.close()
results.close()
trees.close()


