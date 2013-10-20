"""
File_processing is a module for processing sentences, alignments and treestructures.
It brings together the functions from the other classes, enabeling the user to apply the functions
using information from three files containing alingments, sentences and parses.
Explain the different possibilities of the class.
"""

from scoring import *
import sys
from constituencies import *
import pickle

class ProcessFiles():
	"""
	Brings together all functions by enabling the user
	to apply functions from the other classes to files
	containing alignments, sentences and
	dependency parses.
	"""
	def __init__(self, alignmentfile, sentencefile, treefile, targetfile = False):
		"""
		During initialization the files are loaded for reading. Allows to leaf empty
		one of more files if they are not needed for functions that will be used
		"""
		self.tree_file, self.alignment_file, self.target_file, self.sentence_file = False,False,False,False
		if treefile:
			self.tree_file = open(treefile,'r')
		if sentencefile:	
			self.sentence_file = open(sentencefile,'r')
		if alignmentfile:
			self.alignment_file = open(alignmentfile,'r')
		if targetfile:
			self.target_file = open(targetfile,'r')
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
		if self.tree_file:
			self.tree_file.seek(0)
		if self.sentence_file:
			self.sentence_file.seek(0)
		if self.alignment_file:
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
	
	def create_grammar(self,tree_file):
		"""
		Create a grammar from inputted treefile. 
		"""
		grammar_dict = {}
		t = open(tree_file,'r')
		i = 1
		for line in t:
			try:
				tree = nltk.Tree(line)
			except ValueError:
				print 'line %i could not be parsed' % i
				continue
			grammar_dict = self.update_grammar_dict_parse(tree, grammar_dict)
			i +=1
		#normalise grammar
		grammar_norm = self.normalise2(grammar_dict)
		return self.to_WeightedGrammar(grammar_norm)		
	
		
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
		parser.trace(0)
		sentence_nr,parsed_sentences = 1,0
		total_score = 0
		new = self.next()
		while new:
			print "evaluating sentence %i" %sentence_nr
			sentence = new[1]
			sentence_length = len(sentence.split())
			if sentence_length < max_length:
				a = Alignments(new[0],sentence)
				try:
					parse = parser.nbest_parse(sentence.split())[0]
				except:
					scorestr =  "sentence %i could not be parsed" %sentence_nr
					print scorestr
					self.print_function(scorestr+'\n',scoref)
					new = self.next()
					sentence_nr +=1
					continue
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
			scoref.close()


	def em(self, max_iter, max_length = 40):
		"""
		When passing a grammar represented by a dictionary,
		iteratively assign probabilities to all HATs of the
		corpus and recompute the counts of the grammar with
		relative frequency estimation until convergence or
		until a maximum number iterations is reached.
		Return the new grammar
		:param start_grammar	Grammar represented as a nested dictionary
		:param max_iter			Maximum number of iterations
		:param max_length		Maximum sentence length considered
		"""
		#Build in some method for measuring the change of two grammars
		print 'run EM with a maximum of %i iterations' %max_iter
		i = 1#
		self.all_rules(HATfile = 'HATs')
		new_grammar = copy.deepcopy(start_grammar)
		while i <= max_iter:
			print "iteration %i" % i
			new_grammar_dict = self.em_iteration(new_grammar, max_length)
			i +=1
		return new_grammar
		
	
	def em_iteration(self, grammar, pickled_HATs, n=1, max_length = 40):
		"""
		Assign probabilities to all HATs in the corpus with the
		current grammar, recompute probabilities and return the
		new grammar.
		It is assumed that the HATs are precomputed and pickled into
		a file in the correct order. Every sentence under max_length should
		be represented in the file as: [sentence_nr, HAT_dict, root].
		"""
		new_grammar = {}
		self._reset_pointer()
		f = open(pickled_HATs, 'r')
		new = self.next()
		sentence_nr = 1
		while new:
			sentence_length = len(new[1].split())
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				print 'sentence skipped'
				pass
			else:
				new_alignment = Alignments(new[0], new[1])
				s_nr, HATdict, root = pickle.load(f)
				assert sentence_nr == s_nr
				a.compute_weights(root, new_grammar, computed_HATforest = False, pcfg_dict = {}, labels = {})
			new_sentence = self.next_sentence()
			sentence_nr += 1
		grammar_norm = self.normalise2(new_grammar)
		f.close()
		return grammar_norm
	
	def normalise(self,rule_dict):
		"""
		Given a nested dictionary that represent rules as follows:
		{lhs : {rhs1 : count, rhs2: count ...}, ....}, return a
		similar nested dictionary with normalised counts
		"""
		normalised_dict = dict({})
		total_lhs = 0
		for lhs in rule_dict:
			normalised_dict[lhs] = {}
			total = 0
			#loop twice through dictionary
			#first to obtain total counts
			for rhs in rule_dict[lhs]:
				total += rule_dict[lhs][rhs]
			# then to adjuct the counts in the
			# new dictionary
			for rhs in rule_dict[lhs]:
				normalised_dict[lhs][rhs] = rule_dict[lhs][rhs]/float(total)
		return normalised_dict

	
	def to_WeightedGrammar(self,rule_dict):
		"""
		Transforms a set of rules represented in a
		nested dictionary into a WeightedGrammar object.
		It is assumed that the startsymbol of the grammar is 
		TOP, if this is not the case, parsing with the grammar
		is not possible.
		"""
		#create grammar
		productions = []
		for lhs in rule_dict:
			for rhs in rule_dict[lhs]:
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
				labels = dependencies.labels(label_args[0], label_args[1], label_args[2])
#				labels = dependencies.annotate_span(l)
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

	def branching_factor(self, max_length):
		"""
		Compute the average branching factor of all head nodes
		of the dependency parses or the corpus.
		Can be restricted to a sentence length.
		"""
		self._reset_pointer()
		sentence_nr = 1
		branching_dict = {}
		new = self.next()
		while new:
			#consistency check
			dependencies = Dependencies(new[2])
			#check if dependency tree is a tree
			if not dependencies.checkroot():
				print "dependencies form no tree, skipped"
				new = self.next()
				sentence_nr+=1
				continue
			
			if len(new[1].split()) < max_length:
				branching_dict = dependencies.branching_factor(branching_dict)
			
			sentence_nr+= 1
			new = self.next()
		return branching_dict

	def percentage_labelled(self,max_length, label_type):
		"""
		Compute the percentage of the spans in the dictionary
		that is labelled by
		"""
		self._reset_pointer()
		sentence_nr = 1
		total = 0
		total_labelled = 0
		new = self.next()
		while new:
#			print sentence_nr
			if len(new[1].split()) < max_length:
				dependencies = Dependencies(new[2], new[1])
				if dependencies.checkroot():
					alignment = Alignments(new[0], new[1])
					labels = label_type(dependencies)
					percentage = alignment.percentage_labelled(labels)
					total += percentage[0]
					total_labelled += percentage[1]
			sentence_nr += 1
			new = self.next()
		return total, total_labelled
				

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

		
	def select_best_rules(self,productions,n, rules):
		"""
		Create a dictionary with the productions with the best scores.
		"""
		raise NotImplementedError

	def em(self, max_iter, max_length = 40):
		"""
		When passing a grammar represented by a dictionary,
		iteratively assign probabilities to all HATs of the
		corpus and recompute the counts of the grammar with
		relative frequency estimation until convergence or
		until a maximum number iterations is reached.
		Return the new grammar
		:param start_grammar	Grammar represented as a nested dictionary
		:param max_iter			Maximum number of iterations
		:param max_length		Maximum sentence length considered
		"""
		#Build in some method for measuring the change of two grammars
		print 'run EM with a maximum of %i iterations' %max_iter
		i = 1#
		grammar = self.all_rules(HATfile = 'HATs')
		while i <= max_iter:
			sentence_nr = 1
			new_grammar = copy.deepcopy(grammar)
			print "iteration %i" % i
			HATs = open('HATs','r')
			while 1:
				try:
					#this is very ugly, see if you can change this
					a = Alignments('0-0','1')
					s_nr, root, new_HAT = pickle.load(HATs)
					print 'iteration %i, sentence %i' %(i, s_nr)
					a.compute_weights(root, new_grammar, new_HAT, grammar)
				except (EOFError):
					HATs.close()
					break
			grammar = copy.deepcopy(self.normalise(new_grammar))
			i +=1
		return grammar

	def unique_rules(self, step_size, max_length = 40):
		"""
		Go through a file and keep track of growth of 
		the	number of unique rules and total rules when the
		corpus grows.
		"""
		unique_rules = {}
		unique_total = 0
		all_rules = {}
		all_total = 0
		self._reset_pointer()
		sentences = 0
		unique_dict = {}
		new = self.next()
		while new:
			sentence_length = len(new[1].split())
			if sentence_length >= max_length:
				pass
			else:
				sentences += 1
				a = Alignments(new[0],new[1])
				dependencies = Dependencies(new[2],new[1])
				l = Labels(dependencies.dependency_labels())
				t1 = time.time()
				labels = l.label_most()
				t2 = time.time()
				print 'labelling time: ', t2-t1
				for rule in a.hat_rules(Rule.uniform_probability,[], labels):
					lhs = rule.lhs().symbol()
					rhs = tuple([rule._str(rhs) for rhs in rule.rhs()])
					if lhs not in all_rules or rhs not in all_rules[lhs]:
						# lhs --> rhs is not yet in all_rules
						if lhs in unique_rules and rhs in unique_rules[lhs]:
							# lhs --> rhs was seen once before, remove from
							# unique dictionary, add to all_rules dictionary
							unique_rules[lhs].remove(rhs)
							unique_total -= 1
							all_rules[lhs] = all_rules.get(lhs,{})
							all_rules[lhs].update({rhs:2})
						else:
							# this is the first time we have seen lhs --> rhs
							unique_total +=1
							all_total += 1
							unique_rules[lhs] = unique_rules.get(lhs,set([]))
							unique_rules[lhs].add(rhs)
					else:
						# we have seen lhs --> rhs several times before
						all_rules[lhs][rhs] += 1
				
				# if mode stepsize == 0, add to dict
				if sentences % step_size == 0:
					unique_dict[sentences] = [all_total, unique_total,float(unique_total)/all_total]
					print 'Alignments: %i\tAll rules: %i\tUnique rules: %i\tPercentage unique:%f' %(sentences, all_total, unique_total, float(unique_total)/all_total)
			new = self.next()
		return unique_dict
				
				
	def all_rules(self, HATfile=False, max_length = 40):
		"""
		Creates a dictionary with all the rules of all HATs of
		the entire corpus.
		If a HATfile is provided, pickle all HAT grammars for further use,
		together with their root label and their sentence number.
		"""
		#not yet uvaluated on real data
		all_rules = {}
		self._reset_pointer()
		f = HATfile
		if f:
			f = open(HATfile,'w')
		sentence_nr = 1
		new = self.next()
		while new:
			sentence_length = len(new[1].split())
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				pass
			else:
				sentence = new[1]
				dependencies = Dependencies(new[2], sentence)
				a = Alignments(new[0],sentence)
				l = Labels(dependencies.dependency_labels())
				labels = l.label_most()
				labels = l.annotate_span(labels)
				if not labels:
					print 'sentence skipped because of inconsistency with dependency parse'
					new = self.next()
					sentence_nr +=1
					continue
				print "updating grammar for", sentence_nr
				root = labels[(0,sentence_length)]
				HAT_dict = a.HAT_dict(labels)
				#put HAT grammar in a file
				if f:
					pickle.dump([sentence_nr,root,HAT_dict],f)
				#update weights for HATforest
				a.compute_weights(root, all_rules, computed_HATforest = HAT_dict, labels = labels)
			new = self.next()
			sentence_nr +=1
		if f:
			f.close()
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


class ProcessConstituencies(ProcessFiles):
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


	def branching_factor(self, max_length=40):
		"""
		Compute the average branching factor of all head nodes
		of the dependency parses or the corpus.
		Can be restricted to a sentence length.
		"""
		self._reset_pointer()
		sentence_nr = 1
		branching_dict = {}
		new = self.next()
		while new:
			#consistency check
			try:
				constituencies = ConstituencyTree(new[2][0])
			except ValueError:
				print "parse %i is not a tree, skipped" % sentence_nr
				sentence_nr +=1
				new = self.next()
				continue
			except IndexError:
				print "parse %i is not a tree, skipped" % sentence_nr
				sentence_nr +=1
				new = self.next()
				continue
		
			if len(new[1].split()) < max_length and constituencies:
				branching_dict = constituencies.branching_factor(branching_dict)
			
			sentence_nr+= 1
			new = self.next()
		return branching_dict
	
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


#x = ProcessDependencies('Data/en-fr.aligned_manual.100','Data/1-100-final.en','Data/1-100-final.en.dependencies')
#print x.unique_rules(10)

