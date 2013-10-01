from file_processing import *

#parse all sentences according to variables specified
max_length = 40
label_args = [0,0,1]

#check if the number of arguments is correct
#if len(sys.argv) != 7:
#	raise ValueError('nr of arguments incorrect, usage:\n python parse.py dependency_file sentence_file alignment_file print_scores_to print_trees_to print_relations_to')

all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
relations = sys.argv[4]

r = open(relations, 'w')
files = ProcessFiles(all_alignments, all_sentences, all_dependencies)
label_dict = files.consistent_labels("Constituencies", max_length)
for label in label_dict:
	total, found = label_dict[label]
	r.write('%s %25i %25i %25f\n' % (label, total, found, float(found)/float(total) ))	

total, found = 0,0
for label in label_dict:
	total += label_dict[label][0]
	found += label_dict[label][1]

#r.write('\n\nTotal\t\t' + str(total) +'\t\t' + str(found) + '\t\t' + str(found/total))
r.write('\n\nTotal %25i %25i %25f' % (total, found, float(found)/float(total)))




r.close()
files.close_all()
