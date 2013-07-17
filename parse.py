from file_processing import *

#parse all sentences according to variables specified
metric, treetype, max_length = 1, 'hats', 40

#check if the number of arguments is correct
if len(sys.argv) != 7:
	raise ValueError('nr of arguments incorrect, usage:\n python parse.py dependency_file sentence_file alignment_file print_scores_to print_trees_to print_relations_to')

all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
scores = sys.argv[4]
tree_file = sys.argv[5]
relation_file = sys.argv[6]

# compute trees and scores and write to files

files = ProcessFiles(all_alignments, all_sentences, all_dependencies)
files.score_all(tree_file, scores, max_length, metric, treetype)
relations = files.relation_count(40)
files.print_dict(relations, relation_file)
files.close_all()

#Waarom duurt het construeren van en grammatica zo lang voor:
# secondly , the requirement of the double hull as a condition for access to Community waters must be enforced as soon as possible and cease to be put off indefinitely .
