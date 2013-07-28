"""
Class for processing sentences, alignments and dependency parses
simultaneously.
"""
 
# -*- coding: utf-8 -*-
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
		During initialization the files are loaded for reading.
		"""
		self.dependency_file = open(dependencyfile,'r')
		self.sentence_file = open(sentencefile,'r')
		self.alignment_file = open(alignmentfile,'r')
		self.label_dict = {}
		
	def next(self):
		"""
		Return the next alignment, sentence and dependency_list.
		If the end of one of the files is reached, return False.
		"""
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
				
	def check_consistency(self, sentence, dep_list):
		"""
		Check whether a list with dependencies is
		consistent with a sentence, by comparing the words.
		Some flexibility is allowed, to account for words
		that are spelled differently. Return True if the
		dependency parse contains no more than 3 words not
		present in the sentence and False otherwise.
		"""
		words = set([])
		if dep_list == []:
			return True
		for relation in dep_list:
			dependent = re.findall('(?<=\, ).*(?=-[0-9]*\))',relation)
			words.add(dependent[0])
		words_sentence = set(sentence.split(' '))
		#some flexibility is allowed because of american/english spelling
		if len(words - words_sentence) < 3:
			return True
		else:
			return False
	
	def consistent_labels(self, alignment, sentence, labels):
		"""
		Find the percentage of inputted labels that is
		consistent with the alignment without computing
		the best parse tree.
		Returns a dictionary with labels as keys and as
		value a pair with how often the label occurred in
		the dependency parse and how often it was
		consistent with the alignment. Parameter labels should
		be presented as a dictionary assigning labels to spans.
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
			label_dict[label] = [current[0] + 1, current[1] + consistent]
		return label_dict

	def score(self, new, spanrel_type, rule_function, scoring_type):
		"""
		Score a sentence according to parameter inputs.
		::
			@param new				A list [new_alignment, new_sentence, dependency_list]
			@param spanrel_type		method from Dependencies specifying what
									type of spanrels to consider
			@param treetype			method from Alignments specifying what type
									of rules to consider
			@param scoring_type		Method from Scoring specifying how to score
									the sentence
		"""
		#Set labels and relations
		dependencies = Dependencies(new[2])
		labels = dependencies.labels()
		if spanrel_type!= None:
			relations = spanrel_type(dependencies)
		# Create a scoring object and parse the sentence
		scoring = Scoring(new[0],new[1], labels)
		productions = rule_function(scoring.alignment, relations, labels)
		grammar = scoring.grammar(productions)
		parse = scoring.parse(grammar)
		score = scoring_type(scoring, parse)
		#normalize score if necessary
		if scoring_type == Scoring.relation_score:
			score = scoring.normalize_score(score, dependencies.nr_of_deps)
		return parse, score		
		
	def score_all(self, treefile, scorefile, max_length = 40, spanrels = Dependencies.get_spanrels, rule_function = Alignments.hat_rules, scoring_type = Scoring.relation_score):
		"""
		Score all input sentences and write scores and
		trees to two different files. 
		A maximum sentence length can be specified.
		For parameters, see score method.
		"""
		self._reset_pointer()
		label_dictionary = {}
		parsed_sentences = 0
		sentence_nr = 1
		ts = 0
		total_score = {10:0, 20:0, 40:0, 100:0}
		sentences = {10:0, 20:0, 40:0, 100:0}
		trees = open(treefile, 'w')
		results = open(scorefile, 'w')
		new = self.next()
		while new:
			#check if sentence and dependency list are consistent
			print sentence_nr
			if not self.check_consistency(new[1], new[2]):
				print "Warning: dependencies and alignment might be inconsistent"			
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				tree, score = self.score(new, spanrels, rule_function, scoring_type)
				trees.write(str(tree) + '\n\n')
				results.write("s " + str(sentence_nr) + '\t\tlength: ' + str(sentence_length)
				 + '\t\tscore: ' + str(score) + '\n')
				#update total scores
				for key in total_score:
					if sentence_length < key:
						total_score[key] += score
						sentences[key] += 1 
				ts += score
				parsed_sentences += 1
			else:
				results.write("No result, sentence longer than " + str(max_length) + " words\n")
			new = self.next()
			sentence_nr += 1
		# Write results to file
		results.write("\n\nSCORES\n")
		results.write("\nlength\t\t\t nr of sentences \t\tscore")
		results.write("\n-----------------------------------------------")
		results.write("\n <10\t\t\t"+str(sentences[10])+'\t\t\t\t\t\t'+str(total_score[10]/sentences[10]))
		results.write("\n <20\t\t\t"+str(sentences[20])+'\t\t\t\t\t\t'+str(total_score[20]/sentences[20]))
		results.write("\n <40\t\t\t"+str(sentences[40])+'\t\t\t\t\t\t'+str(total_score[40]/sentences[40]))
		results.write("\n all\t\t\t"+str(sentences[100])+'\t\t\t\t\t\t'+str(total_score[100]/sentences[100])+"\n\n")
		#close files
		trees.close()
		results.close()
	
	def _reset_pointer(self):
		self.dependency_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
			
	def relation_count(self, max_length):
		"""
		Counts occurences of all relations in
		sentences shorter than max_length.
		"""
		parsed_sentences = 0
		self._reset_pointer()
		relations = {}
		new = self.next()
		while new:
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				dependencies = Dependencies(new[2])
				dependencies.update_labels(relations)
			new = self.next()
			parsed_sentences += 1
		return relations
	
	def relation_percentage(self, all_relations, relations_present):
		percentage_dict = {}
		for key in all_relations:
			percentage_dict[key] = relations_present.get(key,0)/all_relations[key]
		return percentage_dict
	
	def close_all(self):
		"""
		Close all input files.
		"""
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
			f.write(key + '\t\t' + str(dictionary[key]) + '\n')
		f.close()



