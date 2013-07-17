from scoring import *
import sys

class ProcessFiles():
	"""
	Brings together all functions by enabling the user
	to apply functions from the other classes to files
	containing alignments, sentences and
	dependency parses.
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
		print 'creating grammar'
		if treetype == 'all':
			productions = scoring.alignment.rules(relations,labels)
		elif treetype == 'hats':
			productions = scoring.alignment.hat_rules(relations,labels)
		else:
			raise NameError("Type of tree does not exist")
		grammar = scoring.grammar(productions)
		print 'parse sentence'
		parse = scoring.parse(grammar)
		score = scoring.score(parse)
		return parse, score
	
	def consistent_labels(self, alignment, sentence, labels):
		"""
		Find the percentage of inputted labels that is
		consistent with the alignment without computing
		the best parse tree.
		Returns a dictionary with labels as keys and as
		value a pair with how often the label occured in
		the dependency parse and how often it was
		consistent with the alignment
		@param input: a dictionary that assigning labels
		to spans
		Gives an upperbound for the score of the alignment
		"""
		label_dict = {}
		this_alignment = Alignment(alignment,sentence)
		spans = this_alignment.spans()
		for label in labels:
			consistent = 0
			if labels[label] in spans:
				consistent = 1
			current = label_dict.get(label,[0,0])
			label_dict[label] = (current[0] + 1, current[1] + consistent)
		return label_dict
		
		
	def score_all(self, treefile, scorefile, max_length, metric = 1, treetype = 'hats'):
		"""
		Score all input sentences and write scores and
		trees to two different files. 
		A maximum sentence length can be specified
		"""
		self.reset_pointer()
		parsed_sentences = 0
		total_score = 0
		trees = open(treefile, 'w')
		results = open(scorefile, 'w')
		new = self.next()
		while new:
			print parsed_sentences + 1
			sentence_length = len(new[1].split())
			print 'sentence length ', sentence_length
			if sentence_length < max_length:
				tree, score = self.score(new, metric, treetype)
				trees.write(str(tree) + '\n\n')
				results.write(str(score) + '\n')
				total_score += score
			else:
				results.write("No result, sentence longer than" + str(max_length) + "words\n")
			parsed_sentences += 1
			new = self.next()
		average = total_score/parsed_sentences
		print 'average score:', average
		results.write("\n\nAverage  score: " + str(average))
		trees.close()
		results.close()
	
	def reset_pointer(self):
		self.dependency_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
			
	def relation_count(self, max_length):
		"""
		Counts occurences of all relations
		sentences shorter than max_length.
		As this uses readline, do not execute
		after executing other functions that
		loop through file.
		"""
		parsed_sentences = 0
		self.reset_pointer()
		relations = {}
		new = self.next()
		while new:
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				dependencies = Dependencies(new[2])
				new_relations = dependencies.label_count()
				for key in new_relations:
					relations[key] = relations.get(key, 0) + new_relations[key]
			new = self.next()
			parsed_sentences += 1
		return relations
		
	def close_all(self):
		self.dependency_file.close()
		self.sentence_file.close()
		self.alignment_file.close()
	
	def print_dict(self, dictionary, filename):
		"""
		Print the contents of a dictionary
		to a file.
		"""
		f = open(filename, 'w')
		for key in dictionary:
			f.write(key + '\t' + str(dictionary[key]) + '\n')
		f.close()



