"""
Module for dealing with dependencies.....
"""

import re
import copy

class Dependencies():
	"""
	A class representing the dependencies of a sentence in a dictionary.
	The dependencies are created from a list with dependencies formatted
	like the stanford dependency parses.
	"""

	def __init__(self, dependency_list, sentence = False):
		"""
		Initialize with a list of dependencies represented as a string
		as follows:
		
			reltype(head-pos_head, dependent-pos_dependent)
		
		The first position in the centence is 1. A dictionary will be created
		with entries of the form:

			pos_head: [pos_dependent, reltype]
		"""
		self.dep_list = dependency_list
		self.nr_of_deps = -1
		self.head_pos = None
		self.deps = self.set_dependencies(dependency_list)
		self.set_wordspans()
		self.sentence = self.reconstruct_sentence(sentence)

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
		#set headpos to first head in dependency list if sentence has no head
		if dependency_list and not self.head_pos:
			first_head = int(re.search('(?<=-)[0-9]*(?=, )',dependency_list[0]).group(0))
			self.head_pos = first_head
		return deps

	def checkroot(self):
		"""
		Check if dependencies form a tree by checking coverage
		of the rootnote.
		"""
		if len(self.deps) == 0:
			return True
		rootspan = self.wordspans[self.head_pos]
		for head in self.deps:
			if head < rootspan[0] or head > rootspan[1]:
				return False
			for dependent in self.deps[head]:
				if dependent[0] < rootspan[0] or dependent[0] > rootspan[1]:
					return False
		return True
		
	def find_head_pos(self, relation):
		return int(re.search('(?<=-)[0-9]*(?=, )',relation).group(0))
	
	def find_head(self, relation):
		return re.search('(?<=\().*(?=-[0-9]*,)',relation).group(0)
		
	def find_dependent_pos(self,relation):
		return int(re.search('(?<=-)[0-9]*(?=\)$)', relation).group(0))
	
	def find_dependent(self, relation):
		return re.search('(?<=, ).*(?=-)',relation).group(0)
	
	def find_relationtype(self, relation):
		return re.match('[a-z\_]*(?=\()',relation).group(0)
		
	def reconstruct_sentence(self, sentence):
		"""
		Reconstruct the sentence corresponding to the 
		dependency parse. Output as list.
		"""
		if sentence:
			# If sentence was input or already computed
			# return sentence
			if isinstance(sentence,list):
				pass
			else:
				sentence = sentence.split()
		else:
			# create sentence from dependency parse
			sentence = [''] * (self.wordspans[self.head_pos][1])
			for relation in self.dep_list:
				pos_word = self.find_dependent_pos(relation)
				word = self.find_dependent(relation)
				sentence[pos_word-1] = word
		return sentence
	
	def textree(self):
		"""
		Print string that will generate a dependency tree in
		pdf with package tikz-dependency.
		"""
		textree = '\\begin{dependency}[theme=simple]\n\\begin{deptext}[column sep=.5cm, row sep=.1ex]\n'
		sentence = self.reconstruct_sentence()
		s = '\\&'.join(sentence[1:])+'\\\\\n'
		n = '\\&'.join(map(str,range(len(sentence)))) + '\\\\\n'
		textree = textree + s + n +'\\end{deptext}\n'
		textree = textree + '\\deproot{%s}{}\n' % str(self.head_pos)
		for head in self.deps:
			for dependent in self.deps[head]:
				textree = textree + '\\depedge{%s}{%s}{%s}\n' % (head, dependent[0], dependent[1])
		textree = textree + '\\end{dependency}'
		return textree

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
 
 	def spanrelations(self, rightbranching = False, leftbranching = False, arg_combine = False, interpunction = True):
 		"""
 		Create a dictionary with spanrelations that are 'deeper'
 		than the standard relations in the dependency parse, and allow
 		for stepwise combining a head with its arguments. The latter can
 		be done in different fashions: if 'rightbranching' is true, relations
 		will be included that first combine with the right arguments, and then
 		with the left arguments, and vise versa for leftbranching. If both left-
 		and rightbranching are true, ...... arg_combine specifies whether arguments
 		can combine with each other before combining with the head.
 		If interpunction is set to True, gaps are taken into account in allowed
 		dependency relations returned (i.e., if (0,7) (8,13) is an allowed relation 
 		and (7,8) is a comma, also (0,8) (8,13) and (0,7) (7,13) are added.
 		"""
 		#Create normal span relations
 		spanrels = {}
		for key in self.deps:
			spanrels[(key-1,key)] = set([])
			for dependent in self.deps[key]:
				spanrels[(key-1,key)].add(self.wordspans[dependent[0]])
		#create deeper span relations
		deep_spanrels = copy.deepcopy(spanrels)
		for head in spanrels:
			relations = []
			deplist = self.argument_list(head)
			index_head = deplist.index(head)
			#determine orders in which arguments may be combined
			if leftbranching and rightbranching:
				left = [(i,j,j+1) for i in xrange(len(deplist)-2) for j in xrange(index_head,len(deplist)-1) if j>i ]
				right = [(i+1,j, i) for j in xrange(index_head,len(deplist)) for i in xrange(index_head) if i+1<j]
				relations = left + right
			elif rightbranching:
				right = [ (index_head, i, i+1) for i in xrange(index_head+1, len(deplist)-1)]
				left = [ (i+1, len(deplist)-1, i) for i in xrange(index_head) ]
				relations = right + left
			elif leftbranching:
				left = [ ( i+1, index_head ,i) for i in xrange(index_head-1) ]
				right = [ (0,i,i+1) for i in xrange(index_head, len(deplist)-1) ]
				relations = left + right
			if arg_combine:
				pass
			# add relations to dictionary
			for tuples in relations:
				rel1 = (deplist[tuples[0]][0],deplist[tuples[1]][1])
				rel2 = deplist[tuples[2]]
				deep_spanrels[rel1] = deep_spanrels.get(rel1,set([]))
				deep_spanrels[rel1].add(rel2)
		if interpunction == True:
			return self._gap_account(deep_spanrels)
		else:
			return deep_spanrels
				
	def _gap_account(self, spanrels):
		"""
		Return a new dictionary that accounts for
		possible gaps in the dependency parse.
		For instance, if (5,6) and (7,8) are 
		related, and (6,7) = ',', then add 
		 (5,7) - (7,8) and (5,6) - (6,8)
		"""
		#Add extra spans in the keys
		gap_spanrels = copy.deepcopy(spanrels)
		for head in spanrels:
			for relation in spanrels[head]:
				l,r = relation[0], relation[1]
				if l != 0 and l not in self.wordspans:
					gap_spanrels[head].add((l-1,r))
				if r+1 not in self.wordspans and r+2 in self.wordspans:
					gap_spanrels[head].add((l,r+1))
		for head in spanrels:
			nheads = []
			l,r = head[0], head[1]
			if l!=0 and l not in self.wordspans:
				nheads.append((l-1,r))
			if r+1 not in self.wordspans and r+2 in self.wordspans:
				nheads.append((l,r+1))
			for nhead in nheads:
				gap_spanrels[nhead] = set([])
				for key in gap_spanrels[head]:
					if key[1] <= nhead[0] or key[0] >= nhead[1]:
						gap_spanrels[nhead].add(key)
		return gap_spanrels
	
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
	
	def dependency_labels(self):
		"""
 		Produces standard labels for spans according to the following scheme:
 		
 		* label[(i,i+1)] = HEAD 	iff word i+1 is the head of the sentence
 		
 		* label[(i,j+1)] = rel		iff there is a dependency relation rel(x, y) and wordspan(y) = (i,j+1)
 		
 		* label[(i,i+1)] = rel-head iff there is a dependency relation rel(x,i+1) and word i+1 was not labelled by one of the previous conditions
 		"""
		labels = {}
		#Check if dependencies are nonempty and form a tree
 		if self.deps == {} or not self.checkroot():
 			print 'no labels were created because dependency list was empty or did not form a tree'
 			return labels
 		else:
	 		#manually add label for sentence head and rootspan
	 		head_span = (self.head_pos -1, self.head_pos)
	 		labels[head_span] = 'root'
	 		labels[self.wordspans[self.head_pos]] = 'ROOT'
	  		for head in self.deps:
	 			head_span = (head-1, head)
	 			for dep in self.deps[head]:
	 				dep_span = self.wordspans[dep[0]]
	 				labels[dep_span] = dep[1]
	 				dep_word_span = (dep[0]-1, dep[0])
	 				labels[dep_word_span] = labels.get(dep_word_span, dep[1]+'-h')
	 	#If a sentence is inputted, label unlabelled spans
 		for word_pos in xrange(len(self.sentence)):
 			word_span = (word_pos,word_pos+1)
 			if word_span not in labels:
 				labels[word_span] = self.POStag(self.sentence[word_pos])
 		return labels
 	
 	def SAMT_labels(self):
 		"""
 		Create SAMT-style labels based on the basic dependency labels
 		created in dependency_labels. The order if precedence is as follows:
 		
 		* Basic labels
 		
 		* labels A + B, where A and B are basic labels
 		
 		* labels A/B or A\B where A and B are basic labels
 		
 		* labels A + B + C where A,B and C are basic labels
 		"""
 		#find basic labels
 		labels_basic = self.dependency_labels()
# 		#find 2 concatenated labels
		labels = copy.deepcopy(labels_basic)
		labels = self.update_concatenated_labels2(labels_basic,labels)
#		#find 'minus'-labels
		labels = self.update_minus_labels(labels_basic,labels)
#		#find 3 concatenated labels
		labels = self.update_concatenated_labels3(labels_basic,labels)
  		return labels		
  			
 	def update_concatenated_labels2(self,labels_i,labels_o):
 		"""
 		Update a dictionary labels_o with all labels
 		that are a concatenation of two labels
 		in the inputted set of input labels labels_i.
 		"""
 		concat_list = [(span1,span2) for span1 in labels_i for span2 in labels_i if span1[1] == span2[0]]
   		for span in concat_list:
   			
  			new_label = '%s+%s' % (labels_i[span[0]], labels_i[span[1]])
  			new_span = (span[0][0],span[1][1])
  			labels_o[new_span] = labels_o.get(new_span,new_label)
  		return labels_o
 	
 	def update_concatenated_labels3(self,labels_i,labels_o):
 		"""
 		Update a dictionary labels_o with labels that are a
 		concatenation of three labels of the inputted set of
 		labels, labels_i.
 		"""
 		concat_list = [(span1,span2,span3) for span1 in labels_i for span2 in labels_i for span3 in labels_i if span1[1]==span2[0] and span2[1] == span3[0]]
 		for span in concat_list:
 			new_label = '%s+%s+%s' % (labels_i[span[0]],labels_i[span[1]],labels_i[span[2]])
 			new_span = (span[0][0],span[2][1])
 			labels_o[new_span] = labels_o.get(new_span,new_label)
 		return labels_o
 	
 	def update_minus_labels(self,labels_i,labels_o):
 		"""
 		update a dictionary labels_o with labels that are
 		of the form A\B, or B/A, that refer to a sequence labelled
 		B missing A on the left of right, respectively, 
 		where A and B in the inputted set labels_i. 
 		"""
 		minus_list = [(span1,span2) for span1 in labels_i for span2 in labels_i if (span1[0] == span2[0] or span1[1] == span2[1]) and span1 != span2]
 		for span in minus_list:
 			L0,L1 = labels_i[span[0]], labels_i[span[1]]
 			s00,s01,s10,s11 = span[0][0], span[0][1],span[1][0],span[1][1]
			if s01 == s11 and s00 < s10:
				new_span, new_label = (s00,s10), '%s/%s' % (L0, L1)
				labels_o[new_span] = labels_o.get(new_span,new_label)
			elif s00 == s10 and s01 < s11:
				new_span, new_label = (s01,s11), '%s\%s' % (L0, L1)
				labels_o[new_span] = labels_o.get(new_span,new_label)
		return labels_o
 
 	
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
 		
 		If ldepth = rdepth = max, labels for all spans are produced, using the function label_all()
 		"""
 		#first create standard labels:
 		if ldepth == rdepth == max_var == 'max':
 			return self.label_all()
 		else:
 			ldepth, rdepth, max_var = int(ldepth), int(rdepth), int(max_var)
 		
 		labels = self.dependency_labels()
 		if max_var == 1 or (ldepth == 0 and rdepth ==0):
 			return labels
 		
 		#loop through labels again to find compound labels  
 		for head in self.deps:
 			head_span = (head-1, head)
 			deplist = self.argument_list(head_span)
 			#Compute index head and nr of right and left dependents
 			index_head = deplist.index(head_span)
 			nr_left = index_head
 			nr_right = len(deplist) - 1 - index_head
 			for left in [i for i in xrange(0, ldepth+1) if i < max_var and i<= nr_left]:
 				for right in [j for j in xrange(rdepth+1) if left+j < max_var and j <= nr_right]:
 					if left == 0:
 						new_label = labels.get(self.wordspans[head],'root')
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

	def percentage_SAMT(self):
		"""
		Return how many spans were labelled with an SAMT label
		and how many spans there were in total.
		"""
		s_length = len(self.sentence)
		all_spans = [(i,j+1) for i in xrange(s_length) for j in xrange(s_length) if j>=i]
		labelled_spans = self.SAMT_labels()
		return len(all_spans), len(labelled_spans)

	def label_all(self):
		"""
		Labels are generated for all spans, as described in Zollman (2011).
		Precedence: +, /, \. As we want to have labels for all spans, uglier
		combined labels are generated if no other label is available.
		If no sentence is attached, words not included in the 
		dependency parse will not get a label.
		
		If the numbering of the dependency parse and the sentence are
		out of sync due to different tokenization, return None.
		"""
		s_length = len(self.sentence)
		# Create a set with all spans, and initialise labels
		unlabelled = set([(i,j+1) for i in xrange(s_length) for j in xrange(s_length) if j>=i])
 		labels = self.dependency_labels()
 		for word_span in labels:
 			try:
 				unlabelled.remove(word_span)
 			except KeyError:
 				"Dependency parse and sentence out of sync due to different tokenization"
 				return None
 		# create compound labels with operator +
		for spans in [(span1,span2) for span1 in labels.keys() for span2 in labels.keys() if span1 != span2]:
			if spans[0][1] == spans[1][0]:
				new_span = (spans[0][0],spans[1][1])
				new_label = '%s+%s' % (labels[spans[0]], labels[spans[1]])
				labels[new_span] = labels.get(new_span,new_label)
				unlabelled = unlabelled - set([new_span])				
		#create compound labels with operators / and \
		for spans in [(span0,span1) for span1 in labels.keys() for span0 in labels.keys() if (span0 != span1 and span1[0]<=span0[0] and span1[1] >= span0[1])]:
			L0, L1 = labels[spans[0]],labels[spans[1]]
			s00,s01,s10,s11 = spans[0][0],spans[0][1],spans[1][0],spans[1][1]
			if '+' in L0:
				L0 = '[%s]' % L0
			if '+' in L1:
				L1 = '[%s]' % L1
			if s01 == s11:
				new_span, new_label = (s10,s00), '%s\%s' % (L1, L0)
			elif s00 == s10:
				new_span, new_label = (s01,s11), '%s/%s' % (L0, L1)
			labels[new_span] = labels.get(new_span,new_label)					
			unlabelled = unlabelled - set([new_span])
		i = 0
		max_iter = len(unlabelled)*len(unlabelled)
		while unlabelled and i < max_iter:
			i +=1
			new_span = unlabelled.pop()
			new_label = self.find_label(new_span,labels)
			if new_label:
				labels[new_span] = new_label
			else:
				unlabelled.add(new_span)
		if unlabelled:
			print 'not for every span a label was found'
			for item in unlabelled:
				labels[item] = 'FAIL'
 		return labels
 	
 	def find_label(self,span,labels):
 		"""
 		Find a new label by summing two
 		already existing labels
 		"""
 		#Weet niet zo goed of dit echt is geimplementeerd zoals ik wil
 		s0,s1 = span[0],span[1]
 		for splitpoint in xrange(s0+1,s1):
 			span1, span2 = (s0,splitpoint), (splitpoint,s1)
 			if span1 in labels and span2 in labels:
 				s1, s2 = labels[span1], labels[span2]
 				if '/' in s1 or '\\' in s1:
 					s1 = '(%s)' %s1
 				if '/' in s2 or '\\' in s2:
 					s2 = '(%s)' %s2
				return '%s+%s' % (s1,s2)
 		else:
 			return None
 	
 	def branching_factor(self,b_dict):
		"""
		Update a dictionary with counts for different
		branching factors with the branching factors
		of the nodes in the current dependency tree.
		"""
 		for head in self.deps:
 			b_factor = len(self.deps[head])
 			b_dict[b_factor] = b_dict.get(b_factor,0)+1
 		return b_dict
 			
 	
 	def POStag(self, word):
 		if word in ("'",",",".",':',';','.'):
 			tag = 'PUNCT'
 		else:
 			tag = 'NOTAG'
 		return tag
 		
	
	def argument_list(self,head_span):
		"""
		return a list with spans of the head and
		its arguments
		"""
		deplist = [head_span]
		head = head_span[1]
		for dep in self.deps[head]:
			dep_span = self.wordspans[dep[0]]
			deplist.append(dep_span)
		deplist.sort()
		return deplist

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
 		"""
 		Update an inputted dictionary with
 		the labels from dependency object.
 		"""
 		for key in self.deps:
 			for dependent in self.deps[key]:
 				label = dependent[1]
 				label_dict[label] = label_dict.get(label,0) + 1
 		return label_dict
 
	def print_spans(self):
		print self.wordspans, '\n'

	def print_deps(self):
		print self.deps, '\n'
	
def demo():
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	print 'Sentence: I give the boy some flowers'
	print 'Dependencies: nsubj(give-2, I-1), root(ROOT-0, give-2), det(boy-4, the-3), iobj(give-2, boy-4), det(flowers-6, some-5), dobj(give-2, flowers-6)\n'
	print 'Word spans:'
	d = Dependencies(dependencies)
	d.print_labels(d.wordspans)

"""
Testing
"""

def test():
	"""
	Test right branching relations for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	print d.branching_factor({1:4,2:3,3:2})
	man_relations = {(1, 2): [(0, 1), (2, 4), (4, 6)], (5, 6): [(4, 5)], (3, 4): [(2, 3)], (1,6): [(0,1)], (1,4): [(4,6)], (0,4): [(4,6)], (0,2): [(2,4)]}

def test1():
	dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)']
	d = Dependencies(dependencies)
	print d.reconstruct_sentence()
	return

def test2():
	sentence = 'madam president , i shall keep to the subject of the minutes .'
	dependencies = ['ccomp(keep-6, madam-1)','dobj(madam-1, president-2)','nsubj(keep-6, i-4)','aux(keep-6, shall-5)','root(ROOT-0, keep-6)','prep(keep-6, to-7)','det(subject-9, the-8)','pobj(to-7, subject-9)','prep(subject-9, of-10)','det(minutes-12, the-11)','pobj(of-10, minutes-12)']
	d = Dependencies(dependencies)
	print d.textree()
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
