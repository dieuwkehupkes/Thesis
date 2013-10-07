"""
File_processing is a module for processing sentences, alignments and treestructures.
It brings together the functions from the other classes, enabeling the user to apply the functions
using information from three files containing alingments, sentences and parses.
Explain the different possibilities of the class.
"""

from scoring import *
import sys
from constituencies import *

class ProcessFiles():
	"""
	Brings together all functions by enabling the user
	to apply functions from the other classes to files
	containing alignments, sentences and
	dependency parses.
	"""
	def __init__(self, alignmentfile, sentencefile, treefile, targetfile = False):
		"""
		During initialization the files are loaded for reading.
		"""
		self.tree_file = open(treefile,'r')
		self.sentence_file = open(sentencefile,'r')
		self.alignment_file = open(alignmentfile,'r')
		if targetfile:
			self.target_file = open(targetfile,'r')
		else:
			self.target_file = False
		self.label_dict = {}
		
	def next(self):
		"""
		Return the next alignment, sentence and tree_list.
		If the end of one of the files is reached, return False.
		"""
		new_alignment = self.alignment_file.readline()
		new_sentence = self.sentence_file.readline()
		new_tree = self.tree_file.readline()
		if self.target_file != False:
			new_target = self.target_file.readline()
		else:
			new_target = ''
		#If end of file is reached, return False
		if new_alignment == '':
			return False
		tree_list = []
		while new_tree != '\n' and new_tree != '':
			tree_list.append(new_tree)
			new_tree = self.tree_file.readline()
		return new_alignment, new_sentence, tree_list, new_target
	
	def next_sentence(self):
		"""
		Return the next sentence. If the end of the file is reached,
		return None.
		"""
		new_sentence = self.sentence_file.readline()
		if new_sentence == '' or new_sentence == '\n':
			return False
		else:
			return new_sentence

	def print_function(self, to_print, filename):
		if filename:
			filename.write(to_print)

	def score_all_sentences(self, rule_function, probability_function, prob_function_args, label_args, max_length = 40, scorefile = '', treefile = ''):
		"""
		Not implemented in general class, use from more specific subclasses.
		If not present, raise not implemented error.
		"""
		raise NotImplementedError

	def _reset_pointer(self):
		self.tree_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
	

	def consistent_labels(self, label_type, max_length = 40):
		"""
		Determines the consistency of a set of alignments with a type of labels
		over the entire corpus.
		"""
		self._reset_pointer()
		sentence_nr = 1
		label_dict = {}
		new = self.next()
		while new:
			print sentence_nr
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				a = Alignments(new[0],new[1])
				if label_type == "Dependencies":
					dependencies = Dependencies(new[2])
					labels = dependencies.labels()
				elif label_type == "Constituencies":
					constituencies = Constituencies(new[2][0])
					labels = constituencies.find_labels()
				else:
					raise ValueError("Type of labels not implemented")
			label_dict = a.consistent_labels(labels, label_dict)
			new = self.next()
			sentence_nr+= 1
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
		self.tree_file.close()
		self.sentence_file.close()
		self.alignment_file.close()
	
	def print_dict(self, dictionary, filename):
		"""
		Print the contents of a dictionary
		to a file.
		"""
		f = open(filename, 'w')
		for key in dictionary:
			value = self.transform_contents(dictionary[key])
			f.write(key + '\t\t' + value + '\n')
		f.close()
	
	def transform_contents(self,value):
		"""
		Return a suitable string representation of
		input
		"""
		if isinstance(value,str):
			return value
		elif isinstance(value,list) or isinstance(x,tuple):
			str_list = [str(v) for v in value]
			return '\t'.join(str_list)
		elif isinstance(value,int):
			return str(value)
		else:
			#not yet implemented, maybe it can be printed
			return value
	
	def evaluate_grammar(self,grammar, max_length, scoref):
		"""
		Parse the corpus with inputted grammar and evaluate
		how well the resulting parses cohere with the
		alignments.
		"""
		self._reset_pointer()
		if scoref:
			scoref = open(scoref,'w')
		parser = ViterbiParser(grammar)
		sentence_nr,parsed_sentences = 1,0
		total_score = 0
		new = self.next()
		while new:
			print "evaluating sentence %i" %sentence_nr
			sentence = new[1]
			sentence_length = len(sentence.split())
			if sentence_length < max_length:
				a = Alignments(new[0],sentence)
				parse = parser.nbest_parse(sentence.split())[0]
				score = a.agreement(parse)
				scorestr = 	"s %i\t\tlength: %i\t\tscore: %f\n" % (sentence_nr, sentence_length, score)
				self.print_function(scorestr,scoref)
				parsed_sentences +=1
				total_score += score
			new = self.next()
			sentence_nr += 1
		scorestr = "\n\ntotal sentences parsed: %i\naverage score: %f\n" % (parsed_sentences, float(total_score)/parsed_sentences)
		print scorestr
		self.print_function(scorestr,scoref)		
		if scoref:
			scorefc.close()


	def em(self, start_grammar, max_iter, n=1, max_length = 40,):
		"""
		When passing a Weightedgrammar, iteratively
		parse corpus and infer a new grammar object, until
		maximum number of iterations is reached. Return the
		new grammar
		:param start_grammar	WeightedGrammar
		:param max_iter			Maximum number of iterations
		:param max_length		Maximum sentence length considered
		:param n				Parse trees to be considered to construct new grammar
		"""
		#Figure out why not more parses are returned!!
		i = 0
		new_grammar = start_grammar
		while i <= max_iter:
			new_grammar_dict = self.em_iteration(new_grammar, n, max_length)
			new_grammar = self.to_WeightedGrammar(new_grammar_dict)
			i +=1
		return new_grammar
		
	
	def em_iteration(self, grammar, n=1, max_length = 40):
		"""
		Parse the corpus with current grammar, extract a
		new grammar from n best parses and return this grammar.
		:param grammar = a WeightedGrammar object
		"""
		new_grammar = {}
		self._reset_pointer()
		new_sentence = self.next_sentence()
		sentence_nr = 1
		while new_sentence:
			print sentence_nr
			sentence_length = len(new_sentence.split())
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				pass
			else:
				new_grammar = self.update_grammar_dict(new_sentence, grammar,new_grammar,n)
			new_sentence = self.next_sentence()
			sentence_nr += 1
		grammar_norm = self.normalise2(new_grammar)
		return grammar_norm
	
	def update_grammar_dict(self,sentence, grammar, grammar_dict, n=1):
		"""
		Parse the corpus with the inputted grammar,
		and extract a new grammar from the n best trees.
		Return the new grammar
		:param grammar			a Weighted grammar
		:param grammar_dict		a dictionary representing the current new grammar that has to be updated	
		"""
		#Viterbi parser outputs only one parse
		print 'update grammatica for sentence: %s' % sentence
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(sentence.split(),n)
		nr_of_parses = 1
		for parse in parses:
#			print 'parse %i' % nr_of_parses
			for production in parse.productions():
				lhs = production.lhs()
				rhs = production.rhs()
				if lhs in grammar_dict:
					grammar_dict[lhs]['COUNTS'] += 1
					grammar_dict[lhs][rhs] = grammar_dict[lhs].get(rhs,0) +1
				else:
					grammar_dict[lhs] = {'COUNTS':1, rhs:1}
			nr_of_parses += 1
		return grammar_dict
		
	def normalise(self,rule_dict):
		"""
		Given a nested dictionary that represent rules as follows:
		{lhs : {rhs1 : count, rhs2: count ...}, ....}, return a
		similar nested dictionary with normalised counts
		"""
		TOP = nltk.Nonterminal('TOP')
		normalised_dict = dict({TOP: {}})
		total_lhs = 0
		for lhs in rule_dict:
			if not isinstance(lhs, nltk.Nonterminal):
				if lhs != 'COUNTS':
					raise TypeError("Instance should be a nltk.Nonterminal")
				continue
			normalised_dict[lhs] = {}
			total = 0
			#loop twice through dictionary
			#first to obtain total counts
			for rhs in rule_dict[lhs]:
				total += 1
				# then to adjuct the counts in the
				# new dictionary
				for rhs in rule_dict[lhs]:
					if rhs != 'COUNTS':
						normalised_dict[lhs][rhs] = rule_dict[lhs][rhs]/float(total)
				if 'root' in lhs.symbol() or 'ROOT' in lhs.symbol():
					total_lhs += total
					normalised_dict[TOP][(lhs,)] = total
		for lhs in normalised_dict[TOP]:
			normalised_dict[TOP][lhs] = normalised_dict[TOP][lhs]/float(total_lhs)
		return normalised_dict

	def normalise2(self, rule_dict):
		"""
		More efficient version of normalise, that assumes that total counts
		of lhs are already present in dictionary under 'counts'.
		"""
		new_dict = {}
		for lhs in rule_dict:
			if not isinstance(lhs, nltk.Nonterminal):
				if lhs != 'COUNTS':
					raise TypeError("Instance should be a Nonterminal")
				continue
			new_dict[lhs] = new_dict.get(lhs,{})
			for rhs in rule_dict[lhs]:
				if rule_dict[lhs] == 'COUNTS':
					continue
				rule_prob = rule_dict[lhs][rhs]/float(rule_dict[lhs]['COUNTS'])
				new_dict[lhs][rhs] = rule_prob
		return new_dict
				
	def to_WeightedGrammar(self,rule_dict):
		"""
		Transforms a set of rules represented in a
		nested dictionary into a WeightedGrammar object.
		"""
		#delete counts from dictionary if present
		for lhs in rule_dict:
			if 'COUNTS' in rule_dict[lhs]:
				del rule_dict[lhs]['COUNTS']
		#create grammar
		productions = []
		for lhs in rule_dict:
			for rhs in rule_dict[lhs]:
				if isinstance(rhs, str):
					if rhs != 'COUNTS':
						raise TypeError("Instance should be a nltk.Nonterminal")
				probability = rule_dict[lhs][rhs]
				rhs_list = list(rhs)
				new_production = nltk.WeightedProduction(lhs,rhs_list,prob=probability)
				productions.append(new_production)
		start = nltk.Nonterminal('TOP')
		return WeightedGrammar(start,productions)


class ProcessDependencies(ProcessFiles):
	"""
	Subclass of ProcessFiles that is focussed on the specific
	occasion in which trees are dependencies.
	"""

	def score_all_sentences(self, rule_function, probability_function, prob_function_args, label_args, max_length = 40, scorefile = False, treefile = False):
		self._reset_pointer()
		parsed_sentences = 0
		sentence_nr = 1
		new = self.next()
		treesf, scoref = False,False
		
		#Create files
		if scorefile:
			scoref = open(scorefile,'w')
		if treefile:
			treesf = open(treefile, 'w')
		
		#Create dictionary to score different subsets of the file
		total_score = {10:0, 20:0, 40:0, 100:0}
		sentences = {10:0, 20:0, 40:0, 100:0}
		
		#process file until one of them ends
		while new:
			print sentence_nr
			#consistency check
			if not self.check_consistency(new[1], new[2]):
				print "Warning: dependencies and alignment might be inconsistent"
			sentence = new[1]
			alignment = new[0]
			sentence_length = len(sentence.split())
			dependencies = Dependencies(new[2])
			a = Alignments(alignment,sentence)
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				print_string_t = "No result, sentence longer than %i words\n" % max_length
			elif not dependencies.checkroot():
				print_string_t = "No result, dependency structure is no tree"
			elif not a.consistent:
				print_string_t = "No result, alignment inconsistent with sentence"
			elif 'cannot' in sentence:
				print_string_t = "No result, dependency parse and sentence out of sync due to tokenization 'cannot'"
			else:
				l = dependencies.labels(label_args[0], label_args[1], label_args[2])
				labels = dependencies.annotate_span(l)
				scoring = Scoring(alignment, sentence, labels)
				#Set arguments for probability function
				if probability_function == Rule.probability_spanrels:
					p1, p2 = prob_function_args[0], prob_function_args[1]
					args = [dependencies.spanrelations(p1,p2), dependencies.nr_of_deps]
				else:
					args = [labels]
				tree, score, rank = scoring.score(rule_function, probability_function, args)
				#update total scores
				for key in total_score:
					if sentence_length < key:
						total_score[key] += score
						sentences[key] += 1 
				#write to files
				print_string_s = "s %i\t\tlength: %i\t\tscore: %f\t\trank: %i\n" % (sentence_nr, sentence_length, score, rank)
				print_string_t = "%s\n\n" % tree
				print 'score', score
				parsed_sentences +=1
			self.print_function(print_string_t,treesf)
			self.print_function(print_string_s,scoref)
			sentence_nr += 1
			new = self.next()
		#Make a table of the results
		results_table, results_string = self._results_string(total_score, sentences)
		if scoref:
			scoref.write('\n\nSCORES\n\n------------------------------------------------------\n%s' %results_string)
			scoref.close()
		if treesf:
			treesf.close()	

	def _results_string(self,total_score, sentences):
		score10, score20,score40,score100 = 0,0,0,0
		if sentences[100] != 0:
			score100 = total_score[100]/sentences[100]
		if sentences[40] != 0:
			score40 = total_score[40]/sentences[40]
		if sentences[20] != 0:
			score20 = total_score[20]/sentences[20]
		if sentences[10] != 0:
			score10 = total_score[10]/sentences[10]
			
		results_table = [ ['length', 'number','score'], ['','',''], ['<10', sentences[10], score10],['<20', sentences[20], score20],['<40', sentences[40], score40], ['all', sentences[100], score100] ]
		results_string = ''
		for triple in results_table:
			print '%s %20s %20s' % (triple[0], triple[1], triple[2])
			results_string += '%s %20s %20s\n' % (triple[0], triple[1], triple[2])
		return results_table, results_string

	def sample(self, samplesize, maxlength = False, display = False):
		"""
		Create a sample of sentence from the inputted files.
		Create a file with the sentences, and files with the
		matching alignments, dependencies and targetsentences.
		If display = True, create a texfile that can be ran
		to give a visual representation of the selected sentences.
		Return an array with the list of sentence numbers that
		were selected.
		"""
		# determine the number of sentences in the file
		import random
		self._reset_pointer()
		f_length = 0
		sentences = []
		for line in self.sentence_file:
			f_length+= 1
			if maxlength and len(line.split()) <= maxlength:
				 sentences.append(f_length)
		# select a sample by generating a random
		# sequence of numbers
		if not maxlength:
			selection = random.sample(range(1,f_length+1),samplesize)
		else:
			s = random.sample(range(len(sentences)),samplesize)
			selection = [sentences[i] for i in s]
		selection.sort()
		# create files
		self._reset_pointer()
		a = open('sample_sentences.txt', 'w')
		s = open('sample_alignments.txt','w')
		d = open('sample_dependencies.txt','w')
		t = open('sample_source.txt','w')
		if display == True:
			disp = open('sample.tex','w')
			disp.write(self.tex_preamble())
		i=0
		while i < selection[-1]:
			i +=1
			new = self.next()
			if i in selection:
				a.write(new[0]), s.write(new[1]), t.write(new[3])
				for  dependency in new[2]:
					d.write(dependency)
				d.write('\n')
				if display == True:
					disp.write('\section*{Sentence %i}' %i)
					disp.write(self.texstring(new))
		if display == True:
			disp.write('\end{document}')
			disp.close()
		a.close(), s.close(), d.close(), t.close()
		return selection
	
	def tex_preamble(self):
		tex_preamble = '\documentclass{report}\n\usepackage[english]{babel}\n\usepackage{fullpage}\n\usepackage[all]{xy}\n\usepackage{tikz-dependency}\n\\author{Dieuwke Hupkes}\n\\title\n{Dependencies}\n\\begin{document}'
		return tex_preamble
	
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

	def _reset_pointer(self):
		self.tree_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
	
	def consistent_labels(self, label_type, max_length = 40):
		"""
		Determines the consistency of a set of alignments with a type of labels
		over the entire corpus.
		"""
		self._reset_pointer()
		sentence_nr = 1
		label_dict = {}
		new = self.next()
		while new:
			print sentence_nr
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				a = Alignments(new[0],new[1])
				if label_type == "Dependencies":
					dependencies = Dependencies(new[2])
					labels = dependencies.labels()
				elif label_type == "Constituencies":
					constituencies = Constituencies(new[2][0])
					labels = constituencies.find_labels()
				else:
					raise ValueError("Type of labels not implemented")
			label_dict = a.consistent_labels(labels, label_dict)
			new = self.next()
			sentence_nr+= 1
		return label_dict

	def all_rules(self,max_length = 40):
		"""
		Creates a dictionary with all the grammar rules
		of the entire file. Returns a Weighted grammar object
		with normalised counts.
		"""
		all_rules = {nltk.Nonterminal('TOP'):{'COUNTS':0}}
		self._reset_pointer()
		sentences = 0
		sentence_nr = 1
		new = self.next()
		while new:
			print sentence_nr
			sentence_length = len(new[1].split())
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				productions = []
				lexicon = []
			else:
				sentence = new[1]
				if 'cannot' in sentence:
					continue
				dependencies = Dependencies(new[2], sentence)
				a = Alignments(new[0],sentence)
				labels = dependencies.label_all()
				if not labels:
					print 'sentence skipped because of inconsistency with dependency parse'
					new = self.next()
					sentence_nr +=1
					continue
				scoring = Scoring(new[0], new[1], labels)
				productions = a.hat_rules(Rule.uniform_probability, [], labels)
				lexicon = a.lexrules(labels)

			for production in productions:
				lhs = production.lhs
				rhs = tuple(production.rhs)
				if 'root' in lhs.symbol() or 'ROOT' in lhs.symbol():
					all_rules[nltk.Nonterminal('TOP')]['COUNTS']+= 1
					all_rules[nltk.Nonterminal('TOP')][(lhs,)] = all_rules[nltk.Nonterminal('TOP')].get((lhs,),0) + 1
				if lhs in all_rules:
					all_rules[lhs]['COUNTS'] += 1
					all_rules[lhs][rhs] = all_rules[lhs].get(rhs,0) +1
				else:
					all_rules[lhs] = {'COUNTS':1, rhs:1}
			for lexical_rule in lexicon:
				lhs = lexical_rule.lhs()
				rhs = lexical_rule.rhs()
				if lhs in all_rules:
					all_rules[lhs]['COUNTS'] += 1
					all_rules[lhs][rhs] = all_rules[lhs].get(rhs,0) +1
				else:
					all_rules[lhs] = {'COUNTS':1, rhs:1}
			new = self.next()
			sentence_nr +=1
		return all_rules
		
			
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
		self.tree_file.close()
		self.sentence_file.close()
		self.alignment_file.close()
	
	def print_dict(self, dictionary, filename):
		"""
		Print the contents of a dictionary
		to a file.
		"""
		f = open(filename, 'w')
		for key in dictionary:
			value = self.transform_contents(dictionary[key])
			f.write(key + '\t\t' + value + '\n')
		f.close()
	
	def transform_contents(self,value):
		"""
		Return a suitable string representation of
		input
		"""
		if isinstance(value,str):
			return value
		elif isinstance(value,list) or isinstance(x,tuple):
			str_list = [str(v) for v in value]
			return '\t'.join(str_list)
		elif isinstance(value,int):
			return str(value)
		else:
			#not yet implemented, maybe it can be printed
			return value
		
	def texstring(self,new):
		"""
		Output a texstring with the alignment, the dependency
		and the 
		ew = alignment, sentence, dep
		"""
		sentence = '\\subsection*{Sentences}\n%s\n\\noindent %s\n' % (new[1],new[3])
		dep = Dependencies(new[2])
		a = Alignments(new[0], new[1], new[3])
		dstring = '\\subsection*{Parse}\n%s\n' % dep.textree()
		alignment = '\\subsection*{Alignment}\n%s\n' % a.texstring()
		texstring = '\n\n%s\n\n%s\n\n%s\\newpage' % (sentence, dstring, alignment)
		return texstring


class ProcessConstituencies():
	"""
	Subclass adapted for constituencies
	"""


	def score_all_sentences(self, rule_function, probability_function, prob_function_args, label_args, max_length = 40, scorefile = '', treefile = ''):
		raise NotImplementedError
	
	def consistent_labels(self, label_type, max_length = 40):
		"""
		Determines the consistency of a set of alignments with a type of labels
		over the entire corpus.
		"""
		self._reset_pointer()
		sentence_nr = 1
		label_dict = {}
		new = self.next()
		while new:
			print sentence_nr
			sentence_length = len(new[1].split())
			if sentence_length < max_length:
				a = Alignments(new[0],new[1])
				constituencies = Constituencies(new[2][0])
				labels = constituencies.find_labels()
			label_dict = a.consistent_labels(labels, label_dict)
			new = self.next()
			sentence_nr+= 1
		return label_dict

	def all_rules(self,max_length=40):
		raise NotImplementedError

	
	def relation_count(self, max_length):
		"""
		Counts occurences of all labels in the
		constituent parse.
		"""
		raise NotImplementedError
	

	def texstring(self,new):
		"""
		Output a texstring with the alignment, the constituency tree
		and the alignment.
		"""
		raise NotImplementedError


