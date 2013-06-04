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
			headdep = re.findall('-[0-9]*',relation)
			if len(headdep) != 2:
				raise NameError('check line, more than 2 dependencies detected')
			head = int(headdep[0].strip('-'))
			dep = int(headdep[1].strip('-'))
			# Create dictionary entry if it doesn't
			# and add dependency
			deps[head] = deps.get(head,[])
			deps[head].append([dep,rel])
		return deps

	def set_wordspans(self):
		"""
		Compute the span of each word and store it in a
		dictionary with word positions and a tuple that
		represents their span as key and value, respectively.
		"""
		self.wordspans = {}
		#remove the root dependency
		del self.deps[0]
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
		Return a dictionary of dependencies between
		word-positions and word spans. Go through the
		dependency dictionary and replace heads by the
		span that constitutes their position and dependents
		by their wordspan. I.e., if 

			pos_head: [pos_dependent, reltype]

		was in the dependency dictionary, then

			(pos_head-1, pos_head): span(pos_dependent)

		will be in the dictionary returned by this function.
		"""	
		self.set_wordspans()
		spanrels = {}
		for key in self.deps:
			spanrels[(key-1,key)] = []
			for dependent in self.deps[key]:
				spanrels[(key-1,key)].append(self.wordspans[dependent[0]])
		self.spanrels = spanrels
	
	def nr_of_deps(self):
		return self.nr_of_deps
 
	def print_spans(self):
		print self.wordspans, '\n'

	def print_deps(self):
		print self.deps, '\n'





"""
Testing
"""
def test1():
	dependencies = ['nn(growth-2, european-1)','nsubj(inconceivable-4, growth-2)','cop(inconceivable-4, is-3)','root(ROOT-0, inconceivable-4)','prep(inconceivable-4, without-5)','pobj(without-5, solidarity-6)']
	d = Dependencies(dependencies)
	d.get_spanrels()
	print d.wordspans
	print d.spanrels
	print d.nr_of_deps
	#MANUALLY CREATE OUTPUT AND OUTPUT IF IT IS THE SAME AS PROGRAMS OUTPUT

  
