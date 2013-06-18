# -*- coding: utf-8 -*-
import re

class Dependencies():
	"""
	A class representing the dependencies of a sentence in a dictionary.
	The dependencies are created from a file with dependencies as outputed
	by the Stanford dependency parser, i.e. every line will contain a
	dependency of the form:

		reltype(head-pos_head, dependent-pos_dependent)

	The first position in the sentence is 1.
	"""

	def __init__(self, dependency_list):
		"""
		Initializes a dictionary with the dependencies
		from an inputed list of dependencies. Entries
		of the dictionary will be of the form:

			pos_head: [pos_dependent, reltype]
		"""
		self.nr_of_deps = -1
		self.deps = self.set_dependencies(dependency_list)
		self.set_wordspans()

	def set_dependencies(self,dependency_list):
		"""
		Read in a file and create a dictionary
		with its dependencies
		"""
		deps = {}
		for relation in dependency_list:
			self.nr_of_deps += 1
			# Find the type of relation
			relb = re.match('[a-z\_]*\(',relation)
			rel = relb.group(0).strip('(')
			# Find head and dependent
			headdep = re.findall('-[0-9]*[0-9]',relation)
			if len(headdep) != 2:
				raise NameError('check line, more than 2 dependencies detected')
			head = int(headdep[0].strip('-'))
			dep = int(headdep[1].strip('-'))
			# Create dictionary entry if it doesn't
			# and add dependency
			deps[head] = deps.get(head,[])
			deps[head].append([dep,rel])
		#remove the root dependency
		del deps[0]
		return deps

	def comp_score(self):
		"""
		Returns the number of words that is head
		of another word, thereby giving a measure of
		the level of compositionality of the parse
		"""
		nr_heads = len(self.deps.keys())
		comp_score = nr_heads/float(self.nr_of_deps+1)
		return comp_score

	def set_wordspans(self):
		"""
		Compute the span of each word and store it in a
		dictionary with word positions and a tuple that
		represents their span as key and value, respectively.
		"""
		self.wordspans = {}
		for key in self.deps:
			self.get_span(key)

	def get_span(self,key):
		"""
		Recursively compute the span of a word. 
		The span of a word is constituted by the minimum and
		maximum position that can be reached from the word by
		following the directed dependency arrows. The spans are
		left exclusive and right inclusive. I.e. if positions
		i and j are the minimum and maximum positions that can
		be reached from a word, its span will be [i-1,j]. Every
		word necessarily spans itself, a word at position i
		without dependents will thus have span [i-1,i].
		The dependency from root to head of the sentence is not
		considered.
		"""
		if self.wordspans.has_key(key):
			# span of this word already computed
			return self.wordspans[key]
		elif not self.deps.has_key(key):
			#The word has no dependents
			self.wordspans[key] = (key-1,key)
			return (key -1,key)
		elif self.deps.has_key(key):
			# make a list with its dependents
			deplist = [(key-1,key)]
			for item in self.deps[key]:
				deplist.append(self.get_span(item[0]))
			self.wordspans[key] = (min(min(deplist)),max(max(deplist)))
			return self.wordspans[key]

	def get_spanrels(self):
		"""
		Create a dictionary of dependencies between
		word-positions and word spans. Go through the
		dependency dictionary and replace heads by the
		span that constitutes their position and dependents
		by their wordspan. I.e., if 

			pos_head: [pos_dependent, reltype]

		was in the dependency dictionary, then

			(pos_head-1, pos_head): span(pos_dependent)

		will be in the dictionary returned by this function.
		"""	
		spanrels = {}
		for key in self.deps:
			spanrels[(key-1,key)] = []
			for dependent in self.deps[key]:
				spanrels[(key-1,key)].append(self.wordspans[dependent[0]])
		return spanrels
 
 	def get_comp_spanrels(self):
 		"""
 		Create a dictionary of dependencies between word positions
 		and word spans. Go through the dependency dictionary, but
 		select only the relations that display compositionality
 		(i.e. no relations between words)
 		"""
		comp_spanrels = {}
		for key in self.deps:
			comp_spanrels[(key-1,key)] = []
			for dependent in self.deps[key]:
				if dependent[0] in self.deps:
					comp_spanrels[(key-1,key)].append(self.wordspans[dependent[0]])
					has_compositionality = True
			# Check if any relations are stored
			if comp_spanrels[(key-1,key)] == []:
				del comp_spanrels[(key-1,key)]
		return comp_spanrels
		
 	def labels(self):
 		"""
 		Create a dictionary that assigns labels to spans,
 		According to their dependency relation.
 		"""
 		labels = {}
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				span_dependent = self.wordspans[dependent[0]]
 				span_string = "-[%s,%s]" % (span_dependent[0], span_dependent[1])
 				labels[span_dependent] = dependent[1]+span_string
 		return labels
 		
 
	def print_spans(self):
		print self.wordspans, '\n'

	def print_deps(self):
		print self.deps, '\n'
		

"""
Testing
"""

def test1():
	dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)]']
	d = Dependencies(dependencies)
	spanrels = d.get_spanrels()
	manual_spanrels= {(1,2): [(0,1)],(5,6): [(0,2),(3,4),(4,5), (6,11)], (7,8):[(6,7),(8,11)],(8,9): [(9,11)], (10,11): [(9,10)]}
	print "Program output matches manual output spanrels: ", spanrels == manual_spanrels
	comp_spanrels = d.get_comp_spanrels()
	manual_comp_spanrels = {(5,6): [(0,2), (6,11)], (7,8):[(8,11)],(8,9): [(9,11)]}
	print "Program output matches manual output comp_spanrels: ", comp_spanrels == manual_comp_spanrels
	print d.labels()

def print_scores():
	dependencies = 'Data/europarl-v7.dependencies.head100'
	scores = open('Testing/europarl-v7.dependencies.head100.compositionality_score', 'w')
	deps = open(dependencies, 'r')
	new_line = deps.readline()
	total_score = 0
	nr_of_deps = 0
	while new_line != '':
		nr_of_deps += 1
		dependency_list = []
		while new_line != '\n':
			dependency_list.append(new_line)
			new_line = deps.readline()
		d = Dependencies(dependency_list)
		score = d.comp_score()
		total_score += score
		scores.write(str(score) +'\n')
		new_line = deps.readline()
	scores.close()
	print nr_of_deps
	print total_score/nr_of_deps

def analyse_test1():
	dependencies = ['nsubj(up-3, it-1)','cop(up-3, is-2)','root(ROOT-0, up-3)','prep(up-3, to-4)','det(States-7, the-5)','nn(States-7, Members-6)','pobj(to-4, States-7)','cc(States-7, and-8)','det(Community-10, the-9)','conj(States-7, Community-10)','aux(take-12, to-11)','xcomp(up-3, take-12)','det(initiatives-15, the-13)','amod(initiatives-15, necessary-14)','nsubj(achieve-17, initiatives-15)','aux(achieve-17, to-16)','xcomp(take-12, achieve-17)','dobj(achieve-17, this-18)']
	d = Dependencies(dependencies)
	print d.comp_score()
