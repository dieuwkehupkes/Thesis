from file_processing import *

#parse all sentences according to variables specified
rule_generator = Alignments.hat_rules
max_length = 40
prob_function = Rule.probability_spanrels
prob_function_args = [True,True]
label_args = [1,1,3]

#check if the number of arguments is correct
#if len(sys.argv) != 7:
#	raise ValueError('nr of arguments incorrect, usage:\n python parse.py dependency_file sentence_file alignment_file print_scores_to print_trees_to print_relations_to')

all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
if len(sys.argv) > 4:
	scores = sys.argv[4]
else:
	scores = ''
if len(sys.argv) > 5:
	tree_file = sys.argv[5]
else:
	tree_file = ''
#relation_file = sys.argv[6]

# compute trees and scores and write to files

files = ProcessDependencies(all_alignments, all_sentences, all_dependencies)
files.score_all_sentences(rule_generator, prob_function, prob_function_args, label_args, max_length, tree_file, scores)

#relations = files.relation_count(40)
#files.print_dict(relations, relation_file)
files.close_all()
