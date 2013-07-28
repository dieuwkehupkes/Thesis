"""
A module for processing alignments.
"""

import nltk
from nltk.grammar import *
from copy import deepcopy

class Alignments:
	"""
	A class that represents alignments. Contains methods to compute
	all spans that have a contiguous translation equivalent source
	side span, and to create CFG's that uniquely generate all
	alignment trees, or all hierarchical alignment trees.
	"""
	def __init__(self,alignment, sentence):
		"""
		Class is initialized with a string representation of
		the alignment that starts counting at 0 of the form 
		'0-1 2-1 ...' and the sentence the alignment represents.
		During intialization, a set-representation of the alignment
		is created.
		"""
		self.lengthS = len(sentence.split())
		self.alignment = self.make_set(alignment)
		self.sentence = sentence

	def make_set(self,alignment):
		"""
		Return a set with all alignment links, and keep track of 
		the length of source and target sentence.
		Output a warning when alignment and sentence do not have
		the same number of words.
		"""
		links = alignment.split()
		pos = 0
		lengthT = 0
		lengthS = 0
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
			print "Alignments has more words than sentence, skipped"
		elif lengthS < self.lengthS:
			print "Caution: sentence does not have the same length as alignment, are there", self.lengthS - lengthS, "unaligned words at the end of the sentence?"
		return set(links)

	def spans(self):
		"""
		Return all a generator with all partial sets and 
		valid source side spans that are part of a phrase pair.
		Contrary to the convention, also unaligned sequences
		of words are allowed as spans.
		
		Spans are computed using a simple version of the
		algorithm presented in Chang & Gildea (2006),
		implementation could be more efficient.
		"""
		phrase_pairs = []
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
					#for number in xrange(x+1,y):
					#	if number in loopList:
					#		loopList.remove(number)
				else:
					if self._partial_set((x,y),E_links):
						yield (x,y+1)

	def _partial_set(self,(x,y),E_links):
		"""
		Compute if [x,y] is a single partial set, which is true iff:
		
		* [x,y] is not a valid span;
		
		* there is at most one aligned word in [x,y]
		
		This function will not check if (x,y) is a valid span, as the function
		is only called from compute_spans if (x,y) is not a valid span.
		"""
		nr_aligned = 0
		for position in xrange(x,y+1):
			if E_links[position] - E_links[position-1] != 0:
				nr_aligned += 1
		if nr_aligned == 1:
			return True
		else:
			return False
			

	def _links_fromE(self):
		"""
		Precompute values for the function
		E_c(j) = |{(i',j')\in A | j' =< j}|
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
		F_c(j) = |{(i',j')\in A | i' =< i}|
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
		that are linked to positions [x,y]
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return min(alignment_links)

	def _maxspan(self,(x,y)):
		"""
		Returns the maximum position on the target side
		that are linked to positions [x,y]
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return max(alignment_links)


	def rules(self, span_relations = {}, labels = {}):
		"""
		Returns a generator with all rules of a PCFG
		uniquely generating all alignment trees. Rule
		probabilities are assigned according to input:
		if span_relation are specified, the probability of
		rule will depend on how many relations it makes true.
		If span_relations are not specified, the rule probability will
		be assigned depending on the label set given. The probability
		of the rule will then be the percentage of all generated nodes
		that can be labelled with one of the provided labels.
		If no labels are provided, the probability of every rule is 1.
		
		span_relations and labels should be given as a dictionary of the
		following form:
		::
			span_relations = {headspan : [depspan_1,...], ....}
			label = {span : label, ....}
		

		The rules are computed by transforming the alignment into
		a graph whose edges correspond to valid spans and partial
		sets and using the path function of the Node class.
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
				# set probability, if span_relations are specified
				# according to how many relations are made true,
				# otherwise, according to how many nodes can be
				# labelled 
				rule = Rule((i, j), path, labels)
				if len(span_relations) != 0:
					prob = rule.probability_spanrels(span_relations)
				elif len(labels) != 0:
					prob = rule.probability_labels()
				else:
					rule.probability = 1
				yield rule


	def hat_rules(self, span_relations = {}, labels = {}):
		"""
		Returns a generator with all rules of a PCFG
		uniquely generating all *hierarchical* alignment trees. Rule
		probabilities are assigned according to input:
		if span_relation are specified, the probability of
		rule will depend on how many relations it makes true.
		If span_relations are not specified, the rule probability will
		be assigned depending on the label set given. The probability
		of the rule will then be the percentage of all generated nodes
		that can be labelled with one of the provided labels.
		If no labels are provided, the probability of every rule is 1.
		
		span_relations and labels should be given as a dictionaries with 
		entries of the following form:
		::
			span_relations = {span : [related_to],...}
			label = {span: label, ....}

		The rules are computed by transforming the alignment into
		a graph whose edges correspond to valid spans and partial
		sets and using the shortest_path function of the Node class.
		"""
		# Create nodes for all positions between words
		nodes = [Node(i) for i in xrange(0, self.lengthS + 1)]
		spans = []
		
		# Construct the graph by creating the edges
		for (i,j) in self.spans():
			nodes[j].link_to(nodes[i])
			spans.append((i,j))
		for (i,j) in spans:
#			print "find spans for (", i, j, ")"
			for path in nodes[i].shortest_paths_to(nodes[j]):
#				print path
				if not path or len(path) == 2:
					# No rule possible, or path points to itself
					continue
				rule = Rule((i,j),path, labels)
				# set probability, if span_relations are specified
				# according to how many relations are made true,
				# otherwise, according to how many nodes can be
				# labelled 
				if len(span_relations) != 0:
					prob = rule.probability_spanrels(span_relations)
				elif len(labels) != 0:
					prob = rule.probability_labels()
				else:
					rule.probability = 1
				yield rule
	

	def lexrules(self, labels = {}):
		"""
		Returns an generator with the terminal rules
		of the grammar. (i.e., the `lexicon', that tells 
		you the span corresponding to a word).
		If labels are provided for the spans, the rules
		will be labelled accordingly. Labels should be given
		in the form of a dictionary formatted as follows:
		::
			label = {span : label ,...}
		"""
		from nltk import tokenize
		sent = self.sentence.split()
		length = len(sent)
		for i in xrange(0,len(sent)):
			lhs_string = labels.get((i,i+1),str(i) + "-" + str(i+1))
			lhs = Nonterminal(lhs_string)
			rhs = [sent[i]]
			probability = 1.0
			yield WeightedProduction(lhs, rhs, prob=probability)


class Waypoint:
	"""
	Defines a waypoint in a one-directional path. This
	allows us to save memory by not having to copy path
	arrays for every path, but represent them as linked
	lists.
	"""
	def __init__(self, node, link = None):
		"""
		Creates a new waypoint, call with the
		node it represents and a link to the
		next waypoint.
		"""
		self.node = node
		self.link = link
		# We can statically calculate length from
		# existing link.
		self.length = 1 if not link else len(link) + 1

	def __len__(self):
		return self.length
	
	def __repr__(self):
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
		"""
		self.links.append(node)
		
	def remove_link(self,node):
		"""
		Remove the edge to this node, if
		present
		"""
		if node in self.links:
			self.links.remove(node)
		

	def paths_to(self, node):
		"""
		Returns a generator that calculates all
		paths to the given node. These paths
		are calculated recursively.
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
		used for later use (i.e paths longer than 1
		from self to intermediate nodes.
		"""
		
#		print 'find shortest paths from', self, 'to', node
		
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
		Set the hash representation of the node..
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
		"""
		self.root = root
		spans = []
			
		waypoint = path
		while waypoint.link:
			spans.append((waypoint.node.value, 
				waypoint.link.node.value))
			waypoint = waypoint.link

		self.spans = spans
		self.labels = labels
		self.rhs()
		self.lhs()
		
	def probability_spanrels(self, span_relations):
		"""
		Compute the probability of a rule according to
		how many span_relations it makes true.
		"""
		probability = 1
		for key in span_relations:
			if key in self.spans:
				for dependent in span_relations[key]:
					if dependent in self.spans:
						probability = probability * 2
		self.probability = probability
	
	def probability_labels(self):
		"""
		Compute the probability of a rule according
		to how many of the nodes it generates can
		be labelled according to a set of given
		labels.
		"""
		probability = 1
		for (i,j) in self.spans:
			if (i,j) in labels:
				continue
			else:
				probability = 0.5 * probability
		self.probability = probability
	
	def uniform_probability(self):
		"""
		Set probability to 1.
		"""
		self.probability = 1
	
	def lhs(self):
		"""
		Create the left hand sides of the rule
		and set as an attribute.
		"""
		lhs = self.labels.get((self.root[0],self.root[1]), "%s-%s" % (self.root[0],self.root[1]))
		self.lhs = lhs
		
	def rhs(self):
		"""
		Create the right hand sight of the rule
		and set as attribute.
		"""
		rhs_list = ([self.labels.get((i,j),"%s-%s" % (i,j)) for (i,j) in self.spans])
		self.rhs = rhs_list

	def __repr__(self):
		"""
		Return a string representation of the rule.
		"""
		return self.__str__()

	def __str__(self):
		"""
		Create a string representation of the rule of the form
		::
			lhs --> rhs1 rhs2 rhs3
		"""
		return ("%s -> %s" % 
			(self.lhs, " ".join(self.rhs)))

