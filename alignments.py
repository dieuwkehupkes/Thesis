"""
Module for processing alignments. This module contains three classes. Running alignments.py
will give a demonstration of te functionality of the classes.
"""

import sys
from implements_grammar import *
from copy import deepcopy
import re
from constituencies import *

class Alignments:
	"""
	A class that represents alignments. Important methods in this class
	compute the monolingual source phrases according to this alignment,
	generate all rules or all maximally recursive rules that are
	associated with the alignment and generate a dictionary representing
	all trees that are generated with this rules in a compact fashion.
	"""
	def __init__(self,links, source, target = ''):
		"""
		Construct a new alignment object with the alignment links
		given by 'links', the sourcesentence given by 'source', and 
		possibly a target sentence 'target'. Construct a set-representation
		of the alignment, and compute a lexical dictionary describing
		the spans of the words.
		
		:param links:	a string of the form '0-1 2-1 ...' representing
						the alignment links. Word numbering starts at 0.
		:param source:	A string representing the source sentence.
		:param target:	A string representing the target sentence.
		
		Class is initialized with a string representation of
		the alignment that starts counting at 0 of the form 
		'0-1 2-1 ...' and the sentence the alignment represents.
		During intialization, a set-representation of the alignment
		is created.
		"""
		self.ts = target
		self.lengthS = len(source.split())
		self.consistent = True
		self.alignment = self.make_set(links)
		self.sentence = source
		self.lex_dict = self.lex_dict()
		self.phrases = False

	def make_set(self,alignment):
		"""
		Return a set with all alignment links, and keep track of 
		the length of source and target sentence.
		Output a warning when alignment and sentence do not have
		the same number of words.
		
		:param alignment:	A string representing the alignment, as was passed during
							initialisation
		"""
		links = alignment.split()
		pos = 0
		lengthT, lengthS = 0, 0
		for link in links:
			link_list = link.split('-')
			source_pos, target_pos = int(link_list[0]), int(link_list[1])
			links[pos] = (source_pos,target_pos)
			if target_pos > lengthT:
				lengthT = target_pos
			if source_pos > lengthS:
				lengthS = source_pos
			pos += 1
		lengthS = lengthS + 1
		self.lengthT = lengthT+1
		if lengthS > self.lengthS:
			#alignment has more links than the sentence, inconsistent
			self.consistent = False
		elif lengthS < self.lengthS:
			print "Caution: sentence does not have the same length as alignment, are there", self.lengthS - lengthS, "unaligned words at the end of the sentence?"
		return set(links)

	def spans(self):
		"""
		Return all a generator with all valid source side 
		spans that are part of a phrase pair, and all one-length
		units that are necessarily part of a tree describing the
		translation.
		Contrary to the convention, also unaligned sequences
		of words are allowed as spans.
		
		Spans are computed using the first shift-reduce algorithm 
		presented in Chang & Gildea (2006). This is not the most
		efficient algorithm to compute phrase pairs.
		"""
		F_links = self._links_fromF()
		E_links = self._links_fromE()
		#Use a shift reduce algorithm to find phrase pairs
		loopList = []
		for y in xrange(0,self.lengthS):
			loopList.append(y)
			for x in reversed(loopList):
				u_xy = self._maxspan((x,y))
				l_xy = self._minspan((x,y))
				f_xy = (F_links[u_xy] - F_links[l_xy-1]) - (E_links[y] - E_links[x-1])
				if f_xy == 0:
					yield (x,y+1)
				else:
					if x == y:
						yield (x,y+1)

	def compute_phrases(self):
		"""
		Return a list with all source phrases of the alignment.
		Similar to Alignments.spans, but returns a list rather
		than a generator, and does not include all one-length units.
		
		:return: A list with all valid source phrases
		"""
		if self.phrases:
			return self.phrases
		phrases = []
		F_links = self._links_fromF()
		E_links = self._links_fromE()		
		loopList = []
		for y in xrange(0,self.lengthS):
			loopList.append(y)
			for x in reversed(loopList):
				u_xy = self._maxspan((x,y))
				l_xy = self._minspan((x,y))
				f_xy = (F_links[u_xy] - F_links[l_xy-1]) - (E_links[y] - E_links[x-1])
				if f_xy == 0:
					phrases.append((x,y+1))
		self.phrases = phrases
		return phrases	

	def _links_fromE(self):
		"""
		Precompute values for the function
		E_c(j) = |{(i',j')\in A | j' =< j}|.
		"""
		E_links = {}
		E_links[-1], E_links[-2] = 0, 0
		E_links[0] = len([(i,j) for (i,j) in self.alignment if i == 0])
		for position in xrange(1,self.lengthS):
			links_from_position = len([(i,j) for (i,j) in self.alignment if i == position])
			E_links[position] = E_links[position-1] + links_from_position
		return E_links

	def _links_fromF(self):
		"""
		Precompute values for the function
		F_c(j) = |{(i',j')\in A | i' =< i}|.
		"""
		F_links = {}
		F_links[-1], F_links[-2] = 0, 0
		F_links[0] = len([(i,j) for (i,j) in self.alignment if j == 0])
		for position in xrange(1,self.lengthT+1):
			links_from_position = len([(i,j) for (i,j) in self.alignment if j == position])
			F_links[position] = F_links[position-1] + links_from_position
		return F_links

	def _minspan(self,(x,y)):
		"""
		Returns the minimum position on the target side
		that are linked to positions [x,y].
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return min(alignment_links)

	def _maxspan(self,(x,y)):
		"""
		Returns the maximum position on the target side
		that are linked to positions [x,y].
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return max(alignment_links)

	def prune_production(self, rule, lex_dict):
		"""
		Replace all leafnodes that do not constitute
		a valid source phrase with the lexical item the
		leafnode dominates.
		
		:type rule: 	a Rule object
		:param lex_dict:	a dictionary with spans as keys, and the corresponding
							lexical items as values.
		
		:return:	a Rule object in which all nodes are either valid
					source spans or lexical items.
		"""
		for i in xrange(len(rule.spans)):
			span = rule.spans[i]
			if span not in self.compute_phrases():
				rule._rhs[i] = lex_dict[span]
		return rule
		
	def rules(self, prob_function, args, labels = {}):
		"""
		Returns a generator with all rules of a PCFG
		uniquely generating all alignment trees. Rule
		probabilities are assigned according to specified
		input probability function, args should contain a list
		of arguments for this function.

		The rules are computed by transforming the alignment into
		a graph whose edges correspond to valid spans and partial
		sets and using the path function of the Node class.
		This function is not as extensively tested as the hat_rules function,
		as it is rarely used for computational issues.
		"""
		# Create nodes for all positions between words
		nodes = [Node(i) for i in xrange(0, self.lengthS + 1)]
		spans = []
		
		# Construct the graph by creating the edges
	#	print 'finding spans'
		for (i,j) in self.spans():
			nodes[i].link_to(nodes[j])
			spans.append((i,j))
	#	print 'finding rules'
		for (i,j) in spans:
			for path in nodes[i].paths_to(nodes[j]):
				if not path or len(path) == 2:
					# No rules possible, or path points to itself
					continue
				# set probability
				rule = Rule((i, j), path, labels)
				prob = prob_function(rule,args)
				yield self.prune_production(rule, self.lex_dict)


	def hat_rules(self, prob_function, args = [], labels = {}):
		#maybe change this to variable number of args with *args
		"""
		Return a generator with all rules of a PCFG
		uniquely generating all *hierarchical* alignment trees. The rules
		are assigned probabilities using the input probability function, args
		are the arguments of these function.

		The rules are computed by transforming the alignment into a set
		of Node objects and links between them that together constitute a
		graph whose edges correspond to valid spans and partial
		sets, and using the shortest_path function of the Node class.
		
		:param prob_function:	A probability function from the Rule class, according to which
								probabilities should be assigned.
		:param args:			The arguments the probability function needs.
		
		:type labels:			A dictionary assigning labels to spans.
		:param labels:			The labels that should be assigned to the spans.
		"""
		# Create nodes for all positions between words
		root_span = (0,self.lengthS)
		self.root_label = labels.get(root_span,None)
		nodes = [Node(i) for i in xrange(0, self.lengthS + 1)]
		spans = []
		
		# Construct the graph by creating the edges
		for (i,j) in self.spans():
			nodes[j].link_to(nodes[i])
			spans.append((i,j))
		for (i,j) in spans:
			for path in nodes[i].shortest_paths_to(nodes[j]):
				if not path or len(path) == 2:
					# No rule possible, or path points to itself
					continue
				rule = Rule((i,j),path, labels)
				# set probability
				prob = prob_function(rule,args)
				yield self.prune_production(rule, self.lex_dict)
	
	def lexrules(self, labels = {}):
		"""
		Returns an generator with the terminal rules
		of the grammar. (i.e., the `lexicon', that tells 
		you the span corresponding to a word).
		If labels are provided for the spans, the rules
		will be labelled accordingly.
		
		:type labels:	A dictionary assigning labels to spans.
		"""
		sent = self.sentence.split()
		length = len(sent)
		for i in xrange(0,len(sent)):
			if (i, i+1) not in self.compute_phrases():
				continue
			else:
				lhs_string = labels.get((i,i+1),str(i) + "-" + str(i+1))
				lhs = nltk.Nonterminal(lhs_string)
				rhs = [sent[i]]
				probability = 1.0
				yield nltk.WeightedProduction(lhs, rhs, prob=probability)
	
	def HAT_dict(self,labels = {}):
		"""
		Transform all HATrules into a dictionary that memory
		efficiently represents the entire forest of HATs.
		As a HAT_dict uniquely represents a HATforest, the labels
		of all spans should be unique avoid amibuity.
	
		:param labels:	A dictionary assigning labels to spans.
		:return:	A dictionary that represents the HATforest, by describing for
					every allowed span what is allowed expansions are. Entries are of
					the form {lhs: [(rhs_11,...,rhs_1m),...,(rhs_n1,...,rhs_nk)]
		"""
		assert len(labels.keys()) == len(set(labels.values())), "Labels are not unique"
		hat_dict = {}
		for rule in self.hat_rules(Rule.uniform_probability,[],labels):
			lhs = rule.lhs().symbol()
			rhs = tuple([rule._str(rhs) for rhs in rule.rhs()])
			hat_dict[lhs] = hat_dict.get(lhs, []) + [rhs]
		for rule in self.lexrules(labels):
			lhs = rule.lhs().symbol()
			rhs = tuple(rule.rhs())
			hat_dict[lhs] = hat_dict.get(lhs, []) + [rhs]
		return hat_dict
			
	def percentage_labelled(self,labels):
		"""
		Output which percentage of the spans in the alignment
		are labelled by the set of inputted labels.
		
		:return:	total, labelled
		"""
		phrases = self.compute_phrases()
		total = len(phrases)
		labelled = 0
		for phrase in phrases:
			if phrase in labels:
				labelled += 1
		return total, labelled
	
	def consistent_labels(self,labels,label_dict):
		"""
		Measures the consistency of the alignment with a dictionary
		that assigns labels to spans.
		Outputs a dictionary with labels, how often
		they occurred in the input set and how often they were preserved.
		Ignore word-labels from dep-parse that end in -h.
		"""
		phrases = self.compute_phrases()
		for span in labels:
			label = labels[span]
			if not re.search('-h$',label) and label != 'root':
				consistent = 0
				if span in phrases:
					consistent = 1
				current = label_dict.get(label,[0,0])
				label_dict[label] = [current[0] + 1, current[1] + consistent]
		return label_dict

	def agreement(self,tree):
		"""
		Output what percentage of the nodes of an inputted tree
		are consistent with the alignment.
		
		:param tree:		An nltk tree object.
		:return:	a float that describes the percentage of the nodes
					of tree that were nodes according to the alignment.
		"""
		t = ConstituencyTree(tree)
		phrases = self.compute_phrases()
		nodes_consistent = t.phrases_consistent(t.tree, 0, phrases)
		nodes_all = t.nr_of_nonterminals()
		return float(nodes_consistent)/nodes_all
	

	def lex_dict(self):
		"""
		Use self.sentence to create a lexical dictionary
		that assigns lexical items to spans.
		
		:return: A dictionary {(0,1) : word1,..,(n-1,n): wordn}
		"""
		lex_dict = {}
		sentence_list = self.sentence.split()
		for i in xrange(len(sentence_list)):
			lex_dict[(i,i+1)] = sentence_list[i]
		return lex_dict
	
	def texstring(self):
		"""
		Generate latexcode that generates a visual representation
		of the alignment.
		"""
		if self.ts == '':
			raise ValueError('cannot create representation without targetstring')
		source_list = self.sentence.split()
		target_list = self.ts.split()
		for link in self.alignment:
			dist = link[0]-link[1]
			if dist >= 0:
				arr = 'dd'+ 'l' * dist
			else:
				arr = 'dd' + 'r' * -dist
			source_list[link[0]] += ' \\ar @{-} [%s]' %arr
		sourcestring = ' & '.join(source_list)
		targetstring = ' & '.join(target_list)
		texstring = '\\scriptsize{\n$\n\\xymatrix@C-2.3pc{\n%s\\\\\\\\\n%s\n}$}' % (sourcestring, targetstring)
		return texstring

class Waypoint:
	"""
	Defines a waypoint in a one-directional path. The class
	Waypoint is used in the representation of paths. Multiple
	paths can be saved more memory efficient as path arrays
	can be shared between paths. As they contain link to other
	Waypoints, Waypoints can represent paths as linked lists.
	"""
	def __init__(self, node, link = None):
		"""
		Create a waypoint object.
		
		:type node:		A Node Object.
		:param node:	The node it represents.
		:type link:		A Waypoint object.
		:param link:	A link to the next waypoint.
		"""
		self.node = node
		self.link = link
		# We can statically calculate length from
		# existing link.
		self.length = 1 if not link else len(link) + 1

	def __len__(self):
		"""
		Return the length of the path.
		"""
		return self.length
	
	def __repr__(self):
		"""
		Unpack the linked list and return the
		path it represents.
		"""
		waypoint = self
		path = [waypoint.node.value]
		while waypoint.link:
			path.append(waypoint.link.node.value)
			waypoint = waypoint.link
		return str(path)

class Node:
	"""
	Defines a node in a directed graph.
	You can add edges from this node to
	other nodes by using link_to. The
	paths_to method calculates all paths
	from this node to the given node.
	The Node class is used to represent alignments as
	graphs.
	"""
	def __init__(self, value):
		"""
		Initializes a new node; value
		can be used for representation
		"""
		self.links = []
		self.value = value
		self.reachable = {}
		self.shortest_paths = {}

	def link_to(self, node):
		"""
		Add a directed edge from this node to
		the given node.
		
		:type node:	A Node object.
		"""
		self.links.append(node)
		
	def remove_link(self,node):
		"""
		Remove the edge to this node, if
		present.
		
		:type node: A Node object.
		"""
		if node in self.links:
			self.links.remove(node)
		

	def paths_to(self, node):
		"""
		Returns a generator that calculates all
		paths to the given node. These paths
		are calculated recursively.
		
		:type node:	a Node object
		"""
		if node == self:
			# Reached our destination, stop searching.
			yield Waypoint(self)
			return

		nid = str(node)
		if nid in self.reachable:
			# Already tracked paths to this point once
			if not self.reachable[nid]:
				# We've previously determined the node to be
				# unreachable from here; cancel search.	
				yield False
			else:
				for path in self.reachable[nid]:
					yield path
			return
		
		# Create a list of paths to this node 	
		paths = []

		# No use searching through links with a larger
		# value than the one we're looking for
		# Important note: this is specific to this algorithm,
		# NOT generic graph search.
		for link in (l for l in self.links if l.value <= node.value):
			for path in link.paths_to(node):
				if path:
					# Yay, we found a path :)
					# Add to known paths and return
					full_path = Waypoint(self, path)
					paths.append(full_path)	
					yield full_path
					
		if paths:
			self.reachable[nid] = paths
		else:
			self.reachable[nid] = False
			yield False
	
	def shortest_paths_to(self,node):
		"""
		Finds all shortest paths from current node
		to node using an adapted Dijkstra algorithm
		starting from the end.
		The function also stores paths that can be
		used for later(i.e paths longer than 1
		from self to intermediate nodes).
		
		:type node:	A Node object.
		"""
		
		if node in self.shortest_paths:
			# already computed the shortest path to this node
			for path in self.shortest_paths[node]:
				yield path
			return
		
		if node.value-self.value == 1:
			#return trivial path
			path = Waypoint(self,Waypoint(node))
			self.shortest_paths[node] = path
			yield path
			return
		
		#initialize
		visited = set([])
		depth = 0
		reachable = {0:set([node])}
		depth_finished = False
		current_paths = {node: [Waypoint(node)]}
		
		while (not depth_finished or self not in visited):
			# search until there are no more nodes at
			# current depth, then move to next deptht
			while len(reachable[depth]) > 0:
				# We start with exploring this distance
				depth_finished = False
				# explore the first closest node
				current_node = reachable[depth].pop()
				# add nodes reachable from current node to
				# next-depth reachable nodes
				reachable[depth+1] = reachable.get(depth+1, set([]))
				for link in (l for l in current_node.links if l.value >= self.value):
					if link not in visited.union(reachable[depth]):
						# this is the shortest path to link
						if not (depth == 0 and link == self):
							# path is not the trivial path
							# add to reachable depth+1 if not already there
							reachable[depth+1].add(link)
							new_path = current_paths.get(link,[])
							for path in current_paths[current_node]:
								new_waypoint = Waypoint(link,path)
								new_path.append(new_waypoint)
							current_paths[link] = new_path
							# store for later use if path is not trivial
							if depth != 0:
								link.shortest_paths[node] = new_path
				visited.add(current_node)
			depth_finished = True
			depth += 1
		for path in current_paths[self]:
			yield path

	def __repr__(self):
		"""
		Return a string representation of the node.
		"""
		return self.__str__()
		
	def __hash__(self):
		"""
		Set the hash representation of the node.
		"""
		return self.value
		
	def __eq__(self, other):
		"""
		Define equality for nodes.
		"""
		if isinstance(other, Node):
			return self.value == other.value
		else:
			return False
		
	def __neq__(self, other):
		"""
		Define non equality for nodes.
		"""
		return (not self.__eq__(other))

	def __str__(self):
		"""
		Return the value of the node as a string.
		"""
		return str(self.value)

class Rule:
	"""
	Defines a rule from one span to a set
	of consecutive spans which's union
	forms it.
	
	A string representation is provided for convenient
	displaying.
	"""
	def __init__(self, root, path, labels = {}):
		"""
		Initialize a new rule as its root span
		and the path in the graph (consisting
		of an array of nodes) that it produces.
		Labels can be provided to annotate the spans
		of a rule.
		
		:param root:	The rootspan of the node.
		:type path:		A Waypoint.
		:type labels:	A dictionary assigning labels to spans.
		"""
		self.root = root
		spans = []
			
		waypoint = path
		while waypoint.link:
			spans.append((waypoint.node.value, 
				waypoint.link.node.value))
			waypoint = waypoint.link

		self.spans = spans
		self._rhs = self._rhs(labels)
		self._lhs = self._lhs(labels)
	
	def rank(self):
		"""
		Return the rank of a rule.
		"""
		return len(self.spans)
	
	def probability_spanrels(self, span_relations):
		"""
		Compute the probability of a rule according to
		how many span_relations it makes true.
		
		:param span_relations:	A list containing a dictionary
								which describes which
								spanrelations are desired.
		"""
		probability = 1
		span_relations = span_relations[0]
		for key in span_relations:
			if key in self.spans:
				for dependent in span_relations[key]:
					if dependent in self.spans:
						probability = probability * 2
		self.probability = probability
	
	def probability_labels(self, labels):
		"""
		Compute the probability of a rule according
		to how many of the nodes it generates can
		be labelled according to a set of given
		labels.
		
		:param labels:	A list containing a dictionary that
						assigns labels to spans.
		"""
		labels = labels[0]
		probability = 1
		for (i,j) in self.spans:
			if (i,j) in labels.keys():
				continue
			else:
				probability = probability * 0.5
		self.probability = probability
		return
	
	def uniform_probability(self, args = []):
		"""
		Set probability to 1.
		"""
		self.probability = 1
	
	def lhs(self):
		"""
		Return the left hand side of the rule.
		
		:type return:	nltk.Nonterminal object.
		"""
		return self._lhs
	
	def _lhs(self, labels):
		"""
		Create the left hand sides of the rule
		and set as an attribute.
		"""
		lhs = labels.get((self.root[0],self.root[1]), "%s-%s" % (self.root[0],self.root[1]))
		return Nonterminal(lhs)
	
	def rhs(self):
		"""
		Return the right hand side of the rule.
		
		:type return:	a tuple with nltk.Nonterminal objects
		"""
		return self._rhs
	

	def _rhs(self,labels):
		"""
		Create the right hand sight of the rule
		and set as attribute.
		"""
		rhs_list = ([labels.get((i,j),"%s-%s" % (i,j)) for (i,j) in self.spans])
		return [nltk.Nonterminal(rhs) for rhs in rhs_list]

	def __eq__(self,other):
		if isinstance(other, self.__class__):
			return self.rhs == other.rhs and self.lhs == other._lhs
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)	

	def __repr__(self):
		"""
		Return a string representation of the rule.
		"""
		return self.__str__()

	def _str(self,rhs):
		if isinstance(rhs, nltk.Nonterminal):
			return rhs.symbol()
		else:
			return str(rhs)

	def __str__(self):
		"""
		Create a string representation of the rule of the form
		::
			lhs --> rhs1 rhs2 rhs3
		"""
		return ("%s -> %s" % 
			(self.lhs().symbol(), " ".join([self._str(rhs) for rhs in self.rhs()])))


####################################################################################
#DEMONSTRATION
####################################################################################


def demos():
	"""
	A demonstration function showing the workings of the alignments class
	"""
	import os
	print  "\nA demonstration showing how an ``Alignments`` object can be created and how some of the class methods can be used. There are 3 demo's available."
	demos = {'1': demo_basic, '2': demo_basic2, '3':HAT_demo}
	while 1:
		print "\n\nPlease choose a demo from the following options:\n"
		print "\tdemo1: basic functions for alignment 0-0 1-1 2-2."
		print "\tdemo2: basic functions for alignment 0-0 1-2 2-1 2-3 3-4."
		print "\tdemo3: demonstration of generating HATgrammars.\n"
		valid = 0
		while not valid:
			option = raw_input("Execute one of the demo's by typing its number, or exit by typing 'q'\t")
			if option == 'q': return
			try:
				demos[option]()
				valid = 1
			except KeyError:
				print "This is not a valid option"
	return

def demo_basic():
	"""
	Demonstration 1, basic monotone one-to-one alignment.
	"""
	if raw_input("\nDemo1\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if (raw_input("\nCreate an Alignments object ") == 'q'): return
	a = Alignments('0-0 1-1 2-2', 'I am happy')
	print ">>> a = Alignments('0-0 1-1 2-2', 'I am happy','Ik ben gelukkig')\n"
	if (raw_input("") == 'q'): return

	if (raw_input("As this is a monotone alignment, all spans are translation equivalent ") == 'q'): return
	print "\n>>> a.compute_phrases()\n", a.compute_phrases()
	if (raw_input("") == 'q'): return
	
	if (raw_input("Phrases can also be returned in a generator object ") == 'q'): return
	print ">>> phrases = a.spans()"
	phrases = a.spans()
	print ">>> phrases\n", phrases

	if (raw_input("") == 'q'): return
	if (raw_input(">>> for phrase in phrases:\n ...\tprint phrase\n") == 'q'): return	
	if (raw_input("") == 'q'): return			
	for phrase in phrases:
		print phrase

	if raw_input("") == 'q': return
	if raw_input("Compute a lexical dictionary") == 'q': return
	print ">>> a.lex_dict"
	print  a.lex_dict
	
	if raw_input("\nEnd of demo1\n\n") == 'q': return
	import os
	os.system('clear')
	return
	

def demo_basic2():
	"""
	Demonstration 2. Simple one-to-many alignment.
	"""
	if raw_input("\nDemo2\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if (raw_input("\nCreate an Alignments object ") == 'q'): return
	a = Alignments('0-0 1-2 2-1 2-3 3-4', 'I am not happy')
	print ">>> a = Alignments('0-0 1-2 2-1 2-3 3-4', 'I am not happy', 'Je ne suis pas heureux')\n"
	if (raw_input("") == 'q'): return
	
	if (raw_input("Find spans with a translation equivalent ") == 'q'): return
	print "\n>>> a.compute_phrases()\n", a.compute_phrases()
	if (raw_input("") == 'q'): return
	
	if raw_input("") == 'q': return
	if raw_input("Compute a lexical dictionary") == 'q': return
	print ">>> a.lex_dict"
	print a.lex_dict
	
	if raw_input("\nEnd of demo2\n\n") == 'q': return
	import os
	os.system('clear')


def HAT_demo():
	"""
	Demonstration 3. Simple one to many alignment, HATfunctionality.
	"""
	if raw_input("\nDemo3\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	a = Alignments('0-0 1-2 2-1 2-3 3-4', 'I also like French', 'Ik houd ook van Frans')
	print ">>> a = Alignments('0-0 1-2 2-1 2-3 3-4', 'I also like French', 'Ik houd ook van Frans')\n"
	if (raw_input("") == 'q'): return
	if raw_input("Make a generator with the possible minimal expansions of all rules, give the all the same weight") == 'q': return
	rules = a.hat_rules(Rule.uniform_probability)
	print ">>> rules = a.hat_rules(Rule.uniform_probability)\n>>> rules\n", rules
	if (raw_input("") == 'q'): return
	if (raw_input("Print the rules:") == 'q'): return
	if (raw_input(">>> for rule in rules:\n ...\tprint rule\n") == 'q'): return		
	for rule in rules:
		print rule	
	if (raw_input("") == 'q'): return
	
	if raw_input("If labels are provided, the rules will be labelled with these labels:") == 'q': return
	labels = {(0,1): 'a', (1,2): 'b', (2,3): 'c', (3,4): 'd', (1,3): 'A', (1,4): 'B', (0,3): 'C', (0,4): 'S'}
	rules = a.hat_rules(Rule.uniform_probability, labels = labels)
	print ">>> labels = {(0,1): 'a', (1,2): 'b', (2,3): 'c', (3,4): 'd', (1,3): 'A', (0,4): 'S'}"
	print ">>> rules = a.hat_rules(Rule.uniform_probability, labels = labels)"
	print ">>> for rule in rules\n...\tprint rule\n"
	for rule in rules:
		print rule
	if (raw_input("") == 'q'): return
	
	if raw_input("HATs can also be represented as a dictionary") == 'q': return
	HAT_dict = a.HAT_dict()
	print ">>> HAT_dict =  a.HAT_dict()"
	print ">>> HAT_dict\n", HAT_dict
	if (raw_input("") == 'q'): return
	if raw_input("\nThis HAT_dict contains the same set of rules as we generated earlier, but also the lexical rules.") == 'q': return
	if (raw_input("") == 'q'): return
	print ">>> for lhs in HAT_dict:\n...\tfor rhs in HAT_dict[lhs]:\n...\t\t	print '%s --> %s' %(lhs, ' '.join(rhs))"
	for lhs in HAT_dict:
		for rhs in HAT_dict[lhs]:
			print '%s --> %s' %(lhs, ' '.join(rhs))
	
	if (raw_input("") == 'q'): return
	if raw_input("\nEnd of demo3\n\n") == 'q': return
	import os
	os.system('clear')

if __name__ == "__main__":
	demos()
