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
 		Create a dictionary that assigns labels to spans
 		according to their dependency relation. The labels
 		are annotated with the span they are modifying
 		"""
 		labels = {}
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				span_dependent = self.wordspans[dependent[0]]
 				span_string = "-[%s,%s]" % (span_dependent[0], span_dependent[1])
 				labels[span_dependent] = dependent[1]+span_string
 		return labels
 	
 	def pure_labels(self):
 		"""
  		Create a dictionary that assigns labels to spans
 		according to their dependency relation.
 		"""
 		labels = {}
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				span_dependent = self.wordspans[dependent[0]]
 				labels[span_dependent] = dependent[1]
 		return labels	
 	
 	
 	def samt_labels(self):
 		"""
 		Create a dictionary that assigns labels to spans
 		according to their dependency relations, but also
 		assigns labels to spans forming conjunctions of
 		relations
 		"""
 		labels = self.pure_labels()
 		for head in self.deps:
 			print head
 			word_span = (head-1,head)
 			labels[word_span] = labels.get(word_span, 'ROOT')
 			head_span = self.wordspans[head]
 			head_label = labels.get(head_span, 'ROOT')
 			dep_list = [word_span]
 			for dependent in self.deps[head]:
 				dep_span = self.wordspans[dependent[0]]
 				dep_list.append(dep_span)
 			dep_list.sort()
 			begin, end = dep_list[0][0], dep_list[-1][1]
 			# Locate position head
			head_pos = dep_list.index(word_span)
			#create all labels with \ and /
			root_label = str(head_label)
			cur_label = root_label
			left_emitted = []
			for i in xrange(head_pos+1):
				right_emitted = []
				for j in reversed(xrange(head_pos+1, len(dep_list))):
					begin_span, end_span = dep_list[i][0],dep_list[j][1]
					samt_span = (begin_span, end_span)
					labels[samt_span] = labels.get(samt_span, cur_label)
					right_emitted.append(labels[dep_list[j]])
					#update concatenated labels
					r_label = '+'.join(reversed(right_emitted))
					l_label = '+'.join(left_emitted)					
					if i > 0:
						labels[(begin,begin_span)] = labels.get((begin,begin_span), l_label)
						labels[(dep_list[j][0], end)] = labels.get((dep_list[j][0],end), r_label)
					#update label for the next span
					if i == 0:
						cur_label = l_label + root_label + "/" + r_label
					else:
						cur_label = l_label + "\\" + root_label + "/" + r_label
				left_emitted.append(labels[dep_list[i]])
			return labels					

	def print_labels(self,labels):
		for key in labels:
			print key, ':\t', labels[key]
 		
 	
 	def label_count(self):
 		label_count = {}
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				label = dependent[1]
 				label_count[label] = label_count.get(label,0) + 1
 		return label_count
 
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
	print d.deps
	manual_spanrels= {(1,2): [(0,1)],(5,6): [(0,2),(3,4),(4,5), (6,11)], (7,8):[(6,7),(8,11)],(8,9): [(9,11)], (10,11): [(9,10)]}
	print "Program output matches manual output spanrels: ", spanrels == manual_spanrels
	comp_spanrels = d.get_comp_spanrels()
	manual_comp_spanrels = {(5,6): [(0,2), (6,11)], (7,8):[(8,11)],(8,9): [(9,11)]}
	print "Program output matches manual output comp_spanrels: ", comp_spanrels == manual_comp_spanrels
	print d.label_count()
#	print d.labels()

def test2():
	"labels"
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
#	print d.deps
	labels = d.samt_labels()
	d.print_labels(labels)



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
