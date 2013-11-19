import re
import copy
from labelling import *

class Dependencies():
	"""
	A class representing the dependencies of a sentence in a dictionary.
	The dependencies are created from a list with dependencies formatted
	like the stanford dependency parses.
	"""

	def __init__(self, dependency_list, sentence = False):
		"""
		Create a Dependencies object, based on the passed dependency list.
		If no sentence is passed, the sentence is reconstructed from the
		dependency list, leaving gaps for items that were not included.
		
		:param dependency_list:	A list with dependencies of the form 
								reltype(head-pos_head, dependent-pos_dependent)
								min(pos-dependent) = 1
		:return:	A dictionaries with entries of the form	pos_head: [pos_dependent, reltype]
		"""
		self.dep_list = dependency_list
		self.nr_of_deps = -1
		self.head_pos = None
		self.deps = self.set_dependencies(dependency_list)
		self.set_wordspans()
		self.sentence = sentence

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
		"""
		Find the position of the head of a dependency relation
		using a regular	expression.
		"""
		return int(re.search('(?<=-)[0-9]*(?=, )',relation).group(0))
	
	def find_head(self, relation):
		"""
		Find the head word of a dependency relation using a regular
		expression.
		"""
		return re.search('(?<=\().*(?=-[0-9]*,)',relation).group(0)
		
	def find_dependent_pos(self,relation):
		"""
		Find the position of the dependent of a dependency relation
		using a regular	expression.
		"""
		return int(re.search('(?<=-)[0-9]*(?=\)$)', relation).group(0))
	
	def find_dependent(self, relation):
		"""
		Find the depending word of a dependency relation using a regular
		expression.
		"""
		return re.search('(?<=, ).*(?=-)',relation).group(0)
	
	def find_relationtype(self, relation):
		"""
		Find the type of a dependency relation using a
		regular expression.
		"""
		return re.match('[a-z\_]*(?=\()',relation).group(0)
		
	def reconstruct_sentence(self):
		"""
		Reconstruct the sentence corresponding to the 
		dependency parse.
		
		:return:	a list with the words of the sentence.
		"""
		if self.sentence:
			# If sentence was input or already computed
			# return sentence
			if isinstance(self.sentence,list):
				pass
			else:
				sentence = self.sentence.split()
		else:
			# create sentence from dependency parse
			try:
				sentence = [''] * (self.wordspans[self.head_pos][1])
			except KeyError:
				return ''
			for relation in self.dep_list:
				pos_word = self.find_dependent_pos(relation)
				word = self.find_dependent(relation)
				sentence[pos_word-1] = word
		self.sentence = sentence
		return self.sentence
	
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
 
 	def spanrelations(self, rightbranching = False, leftbranching = False, interpunction = True):
 		"""
 		Create a dictionary with spanrelations that are 'deeper' than the standard 
 		relations in the dependency parse, such that stepwise combining head and
 		arguments is allowed. Parameters rightbranching, leftbranching and interpunction
 		describe how exactly arguments and heads are allowed to combine.
 		
 		:param rightbranching:	allow an argument to combine with the arguments one by one,
 								giving preference to arguments to the right.
 		:param leftbranching:	allow an arguments to combine with the head one by one,
 								giving preference to arguments to the left.
 		:param interpunction:	Take gaps in the dependency parse into account, by adding
 								extra relations in which the gap is already combined
 								with one of its left or right adjacing units.
 		
 		If both left- and rightbranching are true, all combination orders are allowed.
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
		 
		:param spanrels: a dictionary that describes which spanrelations are desired.
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
 			#No labels are created because dependency list is empty or does not form a tree
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
	 	sentence = self.reconstruct_sentence()
 		for word_pos in xrange(len(sentence)):
 			word_span = (word_pos,word_pos+1)
 			if word_span not in labels:
 				labels[word_span] = self.POStag(sentence[word_pos])
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
 		labels = Labels(labels_basic)
 		return labels.SAMT_labels()
 
	def label_all(self):
		"""
		Label all spans of the sentence.
		"""
		labels_basic = self.dependency_labels()
		labels = Labels(labels_basic)
		return labels.label_most()
	
	def labels(self, label_type = 'basic'):
		"""
		Return labels of given type.
		
		:type label_type:	str.
		:param type:	describes which label_type should be used. Options: all, basic or SAMT.
		
		The default labeltype is basic.
		"""
		if label_type == None:
			return {}
		elif label_type == 'basic':
			return self.dependency_labels()
		elif label_type == 'SAMT':
			return self.SAMT_labels()
		elif label_type == 'all':
			return self.label_all()
		else:
			raise ValueError("%s is no valid labeltype" %label_type)


	def percentage_SAMT(self):
		"""
		Compute how many spans were labelled by
		an SAMT label.
		:return:	number of spans, number of labelled spans
		"""
		s_length = len(self.sentence)
		all_spans = [(i,j+1) for i in xrange(s_length) for j in xrange(s_length) if j>=i]
		labelled_spans = self.SAMT_labels()
		return len(all_spans), len(labelled_spans)


	def branching_factor(self,b_dict = {}):
		"""
		Compute the branching factor of all nodes in the
		dependency tree. If an input dictionary is given,
		update the branching factors in the dictionary with
		the newly found branching factors.
		"""
 		for head in self.deps:
 			b_factor = len(self.deps[head])
 			b_dict[b_factor] = b_dict.get(b_factor,0)+1
 		return b_dict
 			
 	
 	def POStag(self, word):
 		"""
 		Find a postag for a word.
 		"""
 		if word in ("'",",",".",':',';','.'):
 			tag = 'PUNCT'
 		elif word == '-':
 			tag = 'DASH'
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
		"""
		Displaying function. Print all
		word_spans of of the dependency parse.
		"""
		print self.wordspans, '\n'

	def print_deps(self):
		"""
		Displaying function. Print all the
		dependency relations in the dependency
		parse.
		"""
		print self.deps, '\n'


####################################################################################
#DEMONSTRATION
####################################################################################

def demo():
	"""
	A demonstration of how the Dependencies class can be used.
	"""
	i = raw_input("\nPress enter to go through demo, q can be pressed at any stage to the quit demo.\t")
	if (i == 'q' or i == 'Q'): return

	print "\n>>> s =  I give the boy some flowers"
	print ">>> dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']"	
	#dependencies
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	
	if (raw_input("") == 'q' or i == 'Q'): return

	print "Create a dependency object:\n>>>d = Dependencies(dependencies)\n"
	d = Dependencies(['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)'])

	if (raw_input("") == 'q' or i == 'Q'): return
	print "During initialisation, information about the dependency parse was computed:"

	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.nr_of_deps\n", d.nr_of_deps

	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.head_pos\n", d.head_pos

	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.deps\n", d.deps
	
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.wordspans\n", d.wordspans

	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.sentence\n", d.sentence, '\n'

	if (raw_input("") == 'q' or i == 'Q'): return
	print "Different types of labels can be computed, that label spans of the sentence, for instance:\n"
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.labels('basic')\n", d.labels('basic'), '\n'
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.labels('SAMT')\n", d.labels('SAMT'), '\n'

	if (raw_input("") == 'q' or i == 'Q'): return
	print "the labels can be annotated with their span:\n"

	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.annotate_span(d.labels('basic'))\n", d.annotate_span(d.labels('basic'))

	if (raw_input("") == 'q' or i == 'Q'): return
	print "\nDifferent types of spanrelations can be computed, for instance:\n"
	if (raw_input("") == 'q' or i == 'Q'): return
	print "The most basic spanrelations:"
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.spanrelations(False,False,True)\n", d.spanrelations(False,False,True),'\n'
	if (raw_input("") == 'q' or i == 'Q'): return
	print "deeper spanrelations:"
	if (raw_input("") == 'q' or i == 'Q'): return	
	print ">>> d.spanrelations(True,True,True)\n",d.spanrelations(True,True,True)
	
	if (raw_input("") == 'q' or i == 'Q'): return
	print '\n\nThe branching factor of the nodes in the dependency relations can be computed, as well as its compositionality level.'
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.branching_factor()\n", d.branching_factor()
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> d.comp_score()\n", d.comp_score(), '\t(Half the nodes have a dependent)'

	if (raw_input("") == 'q' or i == 'Q'): return

	print "\nThis is the end of the demonstration.\n"
	
if __name__ == "__main__":
	print  "\nA demonstration showing how a ``Dependencies`` object can be created and how some of the class methods can be used."
	demo()
