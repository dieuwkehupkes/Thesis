"""
Module for dealing with dependencies.....
"""

import re

class Dependencies():
	"""
	A class representing the dependencies of a sentence in a dictionary.
	The dependencies are created from a list with dependencies formatted
	like the stanford dependency parses.
	"""

	def __init__(self, dependency_list):
		"""
		Initialize with a list of dependencies represented as a string
		as follows:
		
			reltype(head-pos_head, dependent-pos_dependent)
		
		The first position in the centence is 1. A dictionary will be created
		with entries of the form:

			pos_head: [pos_dependent, reltype]
		"""
		self.nr_of_deps = -1
		self.deps = self.set_dependencies(dependency_list)
		self.set_wordspans()

	def set_dependencies(self,dependency_list):
		"""
		Read in a file and create a dictionary
		with its dependencies using regular expressions.
		"""
		deps = {}
		for relation in dependency_list:
			self.nr_of_deps += 1
			# Find the type of relation
			rel = re.match('[a-z\_]*(?=\()',relation).group(0)
			# Find head and dependent
			head = int(re.search('(?<=-)[0-9]*(?=, )',relation).group(0))
			dep = int(re.search('(?<=-)[0-9]*(?=\)$)', relation).group(0))
			# Set head position and create
			#dictinary entries
			if head == 0:
				self.head_pos = dep
			else:
				deps[head] = deps.get(head,[])
				deps[head].append([dep,rel])
		return deps

	def comp_score(self):
		"""
		Returns the percentage of words that is head
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

			(pos_head-1, pos_head): span[pos_dependent]

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
 
	
 	def labels(self, ldepth = 0, rdepth = 0, max_var = 1):
 		"""
 		When ran without any variables, produces standard labels for spans
 		according to the following scheme:
 		
 		* label[(i,i+1)] = HEAD 	iff word i+1 is the head of the sentence
 		
 		* label[(i,j+1)] = rel		iff there is a dependency relation rel(x, y) and wordspan(y) = (i,j+1)
 		
 		* label[(i,i+1)] = rel-head iff there is a dependency relation rel(x,i+1) and word i+1 was not labelled by one of the previous conditions
 		
		
 		Parameters can be used to indicate that compound labels should be
 		found. ldepth indicates the depth on the left, rdepth indicates the depth
 		on the right, and max_var indicates how many variables should maximally
 		be used. E.g, ldepth = 1 means that Y/X is allowed, while Y+Z/X is not,
 		if max_var is 2, Y/X and X\Y. X+Y is only constructed if there is a Z such that
 		X+Y/Z or Z\X+Y. 'Normal' labels are prefered over compound labels.
 		"""
 		#first create standard labe ls:
 		labels = {}
 		#In case input is 0,0,0 no labels are preferred:
 		if ldepth == rdepth == 0:
 			return labels
 		#manually add label for head
 		head_span = (self.head_pos -1, self.head_pos)
 		labels[head_span] = 'head'
 		labels[self.wordspans[self.head_pos]] = 'root'
 		for head in self.deps:
# 			print 'head', head
# 			head_span = (head-1, head)
 			for dep in self.deps[head]:
# 				print 'dep', dep
 				dep_span = self.wordspans[dep[0]]
 				labels[dep_span] = dep[1]
 				dep_word_span = (dep[0]-1, dep[0])
 				labels[dep_word_span] = labels.get(dep_word_span, dep[1]+'-head')
 		if max_var == 1 or (ldepth == 0 and rdepth ==0):
 			return labels
 		#loop through labels again to find compound labels  		
 		for head in self.deps:
 			head_span = (head-1, head)
 			deplist = [head_span]
 			for dep in self.deps[head]:
	 			dep_span = self.wordspans[dep[0]]
 				deplist.append(dep_span)
 			deplist.sort()	
 			#Compute index head and nr of right and left dependents
 			index_head = deplist.index(head_span)
 			nr_left = index_head
 			nr_right = len(deplist) - 1 - index_head
 			for left in [i for i in xrange(0, ldepth+1) if i < max_var and i<= nr_left]:
 				for right in [j for j in xrange(rdepth+1) if left+j < max_var and j <= nr_right]:
# 					print 'maxvar= ', max_var, 'left+right= ' ,left, right
 					if left == 0:
 						new_label = labels[self.wordspans[head]]
 						left_index = deplist[0][0]
 					else:
 						left_index = deplist[left-1][1]
 						compound_left = '+'.join([labels[deplist[k]] for k in xrange(left)])
 						compound_span = (deplist[0][0],left_index)
 						labels[compound_span] = labels.get(compound_span, compound_left)
 						new_label = compound_left + "/" + labels[self.wordspans[head]]
 					if right == 0:
 						right_index = deplist[-1][1]
 					else:
 						right_index = deplist[-right][0]
						compound_right = '+'.join([labels[deplist[l]] for l in xrange(-right,0)])
						compound_span = (right_index,deplist[-1][1])
						labels[compound_span] = labels.get(compound_span, compound_right)
						new_label = new_label + '\\' + compound_right
					#Set new label in dictionary
					labelled_span = (left_index, right_index)
					labels[labelled_span] = labels.get(labelled_span, new_label)
 		return labels

 	def annotate_span(self, labels):
 		"""
 		Annotate labels with their span, to make the
 		grammar unique.
 		"""
 		for key in labels:
 			span = "-[%s-%s]" % (key[0], key[1])
 			new_label = labels[key] + span
 			labels[key] = new_label
 		return labels

	def print_labels(self,labels):
		"""
		Print out the contents of a dictionary
		in a nice format.
		"""
		for key in labels:
			print key, ':\t', labels[key]
 		
 	
 	def update_labels(self,label_dict):
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				label = dependent[1]
 				label_dict[label] = label_dict.get(label,0) + 1
 		return label_dict
 
	def print_spans(self):
		print self.wordspans, '\n'

	def print_deps(self):
		print self.deps, '\n'
		

"""
Testing
"""

def test():
	"""
	Test labelling for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj', (1,2): 'head', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-head', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-head', (0,6): 'root', (0,2) :'root' + '\\' +'iobj+dobj', (0,4): 'root' + '\\' +'dobj', (1,4): 'nsubj/root' + '\\' +'dobj', (1,6): 'nsubj/root', (2,6): 'iobj+dobj'}
	labels = d.labels(1,2,4)
	print d.labels(0,0,0)
	print set(man_labels.keys()) - set(labels.keys())
	print set(labels.keys()) - set(man_labels.keys())
	return labels == man_labels


def test1():
	dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)']
	d = Dependencies(dependencies)
	print d.deps
	return

def test2():
	sentence = 'madam president , i shall keep to the subject of the minutes .'
	dependencies = ['ccomp(keep-6, madam-1)','dobj(madam-1, president-2)','nsubj(keep-6, i-4)','aux(keep-6, shall-5)','root(ROOT-0, keep-6)','prep(keep-6, to-7)','det(subject-9, the-8)','pobj(to-7, subject-9)','prep(subject-9, of-10)','det(minutes-12, the-11)','pobj(of-10, minutes-12)']
	d = Dependencies(dependencies)
	labels = d.labels(2,2,3)
	print d.print_labels(labels)
#	d.print_labels(labels), '\n'

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
