from scoring import *
import sys

class Main():
	"""
	"""
	def __init__(self, alignmentfile, sentencefile, dependencyfile):
		"""
		During initialization the files are loaded for reading
		"""
		self.dependency_file = open(dependencyfile,'r')
		self.sentence_file = open(sentencefile,'r')
		self.alignment_file = open(alignmentfile,'r')
		
	def next(self):
		new_alignment = self.alignment_file.readline()
		new_sentence = self.sentence_file.readline()
		new_dependent = self.dependency_file.readline()
		#If end of file is reached, return False
		if new_alignment == '':
			return False
		dependency_list = []
		while new_dependent != '\n' and new_dependent != '':
			dependency_list.append(new_dependent)
			new_dependent = self.dependency_file.readline()
		return new_alignment, new_sentence, dependency_list
	
	def spanrels(self,dependency_list):
		dependencies = Dependencies(dependency_list)
		relations = dependencies.get_spanrels()
		labels = dependencies.labels()
		return relations, labels
		
	def comp_spanrels(self,dependency_list):
		dependencies = Dependencies(dependency_list)
		relations = dependencies.get_comp_spanrels()
		labels = dependencies.labels()
		return relations, labels
	
	def score(self, new, metric = 1, treetype = 'hats'):
		"""
		Load with number of metric used to score and the
		type of trees to be considered. Metric 1 considers
		all relations in the dependency tree, metric 2 only 
		the ones displaying compositionality. 'all' considers
		all trees over the alignments 'hats' only the HATs.
		@param new: a list [alignment, sentence, list with dependencies]
		"""
		# Read in information for the new sentence, if no new
		# information is available, return
#		if new[0] == '':
#			return False
		# Get the labels and relations
		if metric == 1:
			relations,labels = self.spanrels(new[2])
		elif metric == 2:
			relations,labels = self.comp_spanrels(new[2])
		else:
			raise ValueError("Metric does not exist")
		# Create a scoring object and parse the sentence
		scoring = Scoring(new[0],new[1], relations, labels)
		if treetype == 'all':
			productions = scoring.alignment.rules(relations,labels)
		elif treetype == 'hats':
			productions = scoring.alignment.hat_rules(relations,labels)
		else:
			raise NameError("Type of tree does not exist")
		grammar = scoring.grammar(productions)
		parse = scoring.parse(grammar)
		score = scoring.score(parse)
		return parse, score
		
	def score_all(self, treefile, scorefile, max_length, metric = 1, treetype = 'hats'):
		"""
		Score all input sentences and write scores and
		trees to two different files. 
		A maximum sentence length can be specified
		"""
		parsed_sentences = 0
		total_score = 0
		trees = open(treefile, 'w')
		results = open(scorefile, 'w')
		new = self.next()
		while new:
			print parsed_sentences + 1
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				tree, score = self.score(new, metric, treetype)
				trees.write(str(tree) + '\n\n')
				results.write(str(score) + '\n')
				parsed_sentences += 1
				total_score += score
			else:
				results.write("No result, sentence longer than" + max_length + "words\n")
			new = self.next()
		average = total_score/parsed_sentences
		print 'average score:', average
		results.write("\n\nAverage  score: " + str(average))
		#Close all files
		self.dependency_file.close()
		self.sentence_file.close()
		self.alignment_file.close()
		trees.close()
		results.close()


# Execution
if len(sys.argv) != 6:
	raise ValueError('nr of arguments incorrect, usage:\n python main.py dependency_file sentence_file alignment_file print_scores_to print_trees_to')

all_dependencies = sys.argv[1]
all_sentences = sys.argv[2]
all_alignments = sys.argv[3]
scores = sys.argv[4]
tree_file = sys.argv[5]

#Other variables:
metric, treetype, max_length = 1, 'hats', 20

main = 	Main(all_alignments, all_sentences, all_dependencies)
main.score_all(tree_file, scores, max_length, metric, treetype)





