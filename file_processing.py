"""
Class for processing sentences, alignments and dependency parses
simultaneously.
"""

from scoring import *
import sys

class ProcessFiles():
	"""
	Brings together all functions by enabling the user
	to apply functions from the other classes to files
	containing alignments, sentences and
	dependency parses.
	"""
	def __init__(self, alignmentfile, sentencefile, dependencyfile, targetfile = False):
		"""
		During initialization the files are loaded for reading.
		"""
		self.dependency_file = open(dependencyfile,'r')
		self.sentence_file = open(sentencefile,'r')
		self.alignment_file = open(alignmentfile,'r')
		if targetfile:
			self.target_file = open(targetfile,'r')
		else:
			self.target_file = False
		self.label_dict = {}
		
	def next(self):
		"""
		Return the next alignment, sentence and dependency_list.
		If the end of one of the files is reached, return False.
		"""
		new_alignment = self.alignment_file.readline()
		new_sentence = self.sentence_file.readline()
		new_dependent = self.dependency_file.readline()
		if self.target_file != False:
			new_target = self.target_file.readline()
		else:
			new_target = ''
		#If end of file is reached, return False
		if new_alignment == '':
			return False
		dependency_list = []
		while new_dependent != '\n' and new_dependent != '':
			dependency_list.append(new_dependent)
			new_dependent = self.dependency_file.readline()
		return new_alignment, new_sentence, dependency_list, new_target
	
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
	
	def score_all_sentences(self, rule_function, probability_function, prob_function_args, label_args, max_length = 40, scorefile = '', treefile = ''):
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
			dependencies = Dependencies(new[2])
			a = Alignments(new[0],new[1])
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				if writeTrees:
					treesf.write("No result, sentence longer than %i words\n" % max_length)
			elif not dependencies.checkroot():
				if writeTrees:
					treesf.write("No result, dependency structure is no tree")
					print "Dependency structure is not a tree"
			elif not a.consistent:
				if writeTrees:
					treesf.write("No result, dependency structure inconsistent with sentence")
					print "Alignments has more words than sentence, skipped"
			else:
				l = dependencies.labels(label_args[0], label_args[1], label_args[2])
				labels = dependencies.annotate_span(l)
				scoring = Scoring(new[0], new[1], labels)
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
				if writeScores:
					scoref.write("s %i\t\tlength: %i\t\tscore: %f\t\trank: %i\n" % (sentence_nr, sentence_length, score, rank))
				if writeTrees:
					treesf.write("%s\n\n" % tree)
				print 'score', score
				parsed_sentences +=1
			sentence_nr += 1
			new = self.next()
		#Make a table of the results
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
		if writeScores:
			scoref.write('\n\nSCORES\n\n------------------------------------------------------\n%s' %results_string)
			scoref.close()
		if writeTrees:
			treesf.close()

	def _reset_pointer(self):
		self.dependency_file.seek(0)
		self.sentence_file.seek(0)
		self.alignment_file.seek(0)
	
	def all_grammar(self,max_length = 40):
		"""
		Creates a dictionary with grammar rules and counts
		in the end, writes all grammar rules to a file
		"""
		self._reset_pointer()
		all_grammar = {}
		sentences = 0
		sentence_nr = 1
		new = self.next()
		while new:
			print sentence_nr
			sentence_length = len(new[1].split())
			dependencies = Dependencies(new[2], new[1])
			a = Alignments(new[0],new[1])
			# tests if input is as desired, skip if not
			if sentence_length >= max_length:
				pass
			else:
				labels = dependencies.label_all()
				scoring = Scoring(new[0], new[1], labels)
				productions = Rule.hat_rules(a, Rule.uniform_probability, [], labels)
				
				grammar = scoring.grammar(productions)
	
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
				dependencies = Dependencies(new[2])
				a = Alignments(new[0],new[1])
				if label_type == "Dependencies":
					labels = dependencies.labels()
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
		

def test_random():
	f = ProcessFiles('Data/en-fr.aligned_manual.100','Data/1-100-final.en','Data/1-100-final.en.dependencies')

def test_tex():
	f = ProcessFiles('Data/en-fr.aligned_manual.100','Data/1-100-final.en','Data/1-100-final.en.dependencies', 'Data/1-100-final.fr')
	f.sample(100,15,True)
