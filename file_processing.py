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
	
	
	def score_all_sentences(self, rule_function, probability_function, label_args, max_length = 40, scorefile = '', treefile = ''):
		self._reset_pointer()
		parsed_sentences = 0
		sentence_nr = 1
		new = self.next()
		writeScores, writeTrees = False, False
		
		#Create files
		if scorefile != '':
			scoref = open(scorefile,'w')
			writeScores = True
		if treefile != '':
			treesf = open(treefile, 'w')
			writeTrees = True
		
		#Create dictionary to score different subsets of the file
		total_score = {10:0, 20:0, 40:0, 100:0}
		sentences = {10:0, 20:0, 40:0, 100:0}
		
		#process file until one of them ends
		while new:
			print sentence_nr
			#consistency check
			if not self.check_consistency(new[1], new[2]):
				print "Warning: dependencies and alignment might be inconsistent"
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				dependencies = Dependencies(new[2])
				#set labels for spans and create a scoring object
				labels = dependencies.labels(label_args[0], label_args[1], label_args[2])
				scoring = Scoring(new[0], new[1], labels)
				#Set arguments for probability function
				if probability_function == Rule.probability_spanrels:
					args = [dependencies.get_spanrels(), dependencies.nr_of_deps]
				else:
					args = [labels]
				tree, score = scoring.score(rule_function, probability_function, args)
				#update total scores
				for key in total_score:
					if sentence_length < key:
						total_score[key] += score
						sentences[key] += 1 
				#write to files
				if writeScores:
					scoref.write("s %i\t\tlength: %i\t\tscore: %f\n" % (sentence_nr, sentence_length, score))
				if writeTrees:
					treesf.write("%s\n\n" % tree)
				print 'score', score
				parsed_sentences +=1
			else:
				if writeTrees:
					treesf.write("No result, sentence longer than %i words\n" % max_length)
			sentence_nr += 1
			new = self.next()
		#Make a table of the results
		results_table = [ ['length', 'nr of sentences','score'], ['','',''], ['<10', sentences[10], total_score[10]/sentences[10]],['<20', sentences[20], total_score[20]/sentences[20]],['<40', sentences[40], total_score[40]/sentences[40]], ['all', sentences[100], total_score[100]/sentences[100]]]
		results_string = ''
		for triple in results_table:
			print '%s %20s %20s' % (triple[0], triple[1], triple[2])
			results_string += '%s %20s %20s\n' % (triple[0], triple[1], triple[2])
		if writeScores:
			scoref.write('\n\nSCORES\n\n------------------------------------------------------\n%s' %results_string)
			scoref.close()
		if writeTrees:
			treesf.close()

	def _reset_pointer(self):
		self.dependency_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
	
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
		Gives an upperbound for the score of the alignment.
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
		
	def relation_count(self, max_length):
		"""
		Counts occurences of all relations in dependency
		parses of sentences shorter than max_length.
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



