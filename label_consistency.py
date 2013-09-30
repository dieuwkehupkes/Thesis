from file_processing import *

#parse all sentences according to variables specified
rule_generator = Alignments.hat_rules
label_rule = Dependencies.labels
max_length = 40
label_args = [0,0,1]

#check if the number of arguments is correct
#if len(sys.argv) != 7:
#	raise ValueError('nr of arguments incorrect, usage:\n python parse.py dependency_file sentence_file alignment_file print_scores_to print_trees_to print_relations_to')

all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
relations = sys.argv[4]

files = ProcessFiles(all_alignments, all_sentences, all_dependencies)
label_dict = files.consistent_labels("Dependencies", max_length)
files.print_dict(label_dict, relations)
files.close_all()
