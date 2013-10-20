"""
A module for processing alignments.
"""

import sys
from implements_grammar import *
from copy import deepcopy
import re
from constituencies import *

class Alignments:
	"""
	A class that represents alignments. Contains methods to compute
	all spans that have a contiguous translation equivalent source
	side span, and to create CFG's that uniquely generate all
	alignment trees, or all hierarchical alignment trees.
	"""
	def __init__(self,alignment, sentence, targetsentence = ''):
		"""
		Class is initialized with a string representation of
		the alignment that starts counting at 0 of the form 
		'0-1 2-1 ...' and the sentence the alignment represents.
		During intialization, a set-representation of the alignment
		is created.
		"""
		self.ts = targetsentence
		self.lengthS = len(sentence.split())
		self.consistent = True
		self.alignment = self.make_set(alignment)
		self.sentence = sentence
		self.lex_dict = self.lex_dict()
		self.phrases = False

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
#			print "Alignments has more words than sentence, skipped"
			self.consistent = False
		elif lengthS < self.lengthS:
			print "Caution: sentence does not have the same length as alignment, are there", self.lengthS - lengthS, "unaligned words at the end of the sentence?"
		return set(links)

	def spans(self):
		"""
		Return all a generator with all valid source side 
		spans that are part of a phrase pair.
		Contrary to the convention, also unaligned sequences
		of words are allowed as spans.
		
		Spans are computed using a simple version of the
		algorithm presented in Chang & Gildea (2006),
		implementation could be more efficient.
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
		Return a list with all translation admissable
		phrases in the alignment.
		Use an algorithm similar to the one presented in
		Chiang & Gildea (2006)
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

	def prune_production(self, rule, lex_dict):
		"""
		Function that replaces all leafnodes that
		do not constitute a translation unit with the
		lexical item specified by the dictionary, such
		that tree nodes all represent translation units.
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


	def hat_rules(self, prob_function, args, labels = {}):
		#maybe change this to variable number of args with *args
		"""
		Returns a generator with all rules of a PCFG
		uniquely generating all *hierarchical* alignment trees. Rule
		probabilities are assigned according to input probability function.
		Args should specify a list of arguments for this function, currently
		assumes there is only 1 argument.

		The rules are computed by transforming the alignment into
		a graph whose edges correspond to valid spans and partial
		sets and using the shortest_path function of the Node class.
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
		will be labelled accordingly. Labels should be given
		in the form of a dictionary formatted as follows:
		::
			label = {span : label ,...}
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
		Returns a dictionary that uniquely generates the HATforest.
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
		:param tree		An nltk tree object.
		"""
		t = ConstituencyTree(tree)
		phrases = self.compute_phrases()
		nodes_consistent = t.phrases_consistent(t.tree, 0, phrases)
		nodes_all = t.nr_of_nonterminals()
		return float(nodes_consistent)/nodes_all
	
	def compute_weights(self, root, counts = {}, computed_HATforest = False, pcfg_dict = {}, labels = {}):
		"""
		Compute weights of the rules in all HATs of the alignment
		through relative frequency estimation, assuming the total
		probability of all HATs is 1.
		If no external pcfg_dictionary is provided, the probability mass
		will be uniformly distributed over all HATs. Otherwise, HATs will
		be assigned probabilities proportional to the probability they
		receive under the input PCFG.
		If no HAT_dictionary is provided, it will be computed. However,
		if it was already computed earlier, it can be passed as a argument to
		the function to reduce computing times.
		"""
		#set the HAT_dictionary
		if computed_HATforest:
			HAT_dict = computed_HATforest
		else:
			HAT_dict = self.HAT_dict(labels)
		probs = {}
		self.probmass(pcfg_dict, HAT_dict, probs, root)
		self.update(HAT_dict,pcfg_dict, probs, counts, 1, root)
		return counts

	def probmass(self, pcfg_dict, HAT_dict, probs, head_node, children = ()):
		"""
		Compute the probability mass of all subtrees headed by head_node, children
		given the current pcfg.
		"""
		nodes = (head_node,)+children
		plain_head, plain_children = self._plain_label(head_node), self._plain_label(children)
		assert len(children) == 0 or children in HAT_dict[head_node], 'Head node %s does not have children %s' % (head_node, children)
		#We already computed the value before
		if nodes in probs:
			return probs[nodes]
		#node is a leaf node
		elif head_node not in HAT_dict:
			prob = 1
		#compute prob mass of trees headed by head_node children
		elif len(nodes) > 1:
			prob = pcfg_dict.get(plain_head,{}).get(plain_children,1)
			assert pcfg_dict == {} or plain_children in pcfg_dict[plain_head], '%s --> %s    not in external pcfg' %(plain_head, ' '.join(plain_children))
			for child in children:
				prob = prob*self.probmass(pcfg_dict, HAT_dict, probs, child)
			probs[nodes] = prob
		#compute prob mass of trees headed by head_node
		else:
			assert len(nodes) == 1
			prob = 0
			for rhs in HAT_dict[head_node]:
				prob += self.probmass(pcfg_dict, HAT_dict, probs, head_node, rhs)
				probs[nodes] = prob
		assert prob > 0, 'probability mass of subtrees headed by %s cannot be 0' %head_node
		return prob
			
	def update(self, HAT_dict,pcfg_dict, probs, counts, p_cur, lhs):
		"""
		Compute the updated counts for a node, given its parent
		and how often this parent occurred in the forest.
		"""
		if lhs not in HAT_dict:
			return
		counts[lhs] = counts.get(lhs,{})
		for rhs in HAT_dict[lhs]:
			tup = (lhs,) + rhs
			c_new = p_cur * float(probs[tup])/probs[(lhs,)]
			counts[lhs][rhs] = counts[lhs].get(rhs,0) + c_new
			for child in rhs:
				self.update(HAT_dict,pcfg_dict, probs, counts, c_new, child)
		return

	def _plain_label(self,label):
		"""
		strip the label from the part determining
		its span, to make it uniform
		"""
		if isinstance(label, str):
			return label.split('-[')[0]
		elif isinstance(label,tuple):
			return tuple([self._plain_label(l) for l in label])
		else:
			raise TypeError("unexpected label-type: %s" %type(label))	

	def lex_dict(self):
		lex_dict = {}
		sentence_list = self.sentence.split()
		for i in xrange(len(sentence_list)):
			lex_dict[(i,i+1)] = sentence_list[i]
		return lex_dict
	
	def texstring(self):
		"""
		Generate latexcode for displaying the alignment.
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

#Miss in andere file zetten

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
		span_relations is a dictionary that describes
		which nodes should be siblings.
		"""
		probability = 1
		span_relations = span_relations[0]
		for key in span_relations:
			if key in self.spans:
				for dependent in span_relations[key]:
					if dependent in self.spans:
						probability = probability * 2
		self.probability = probability
	
	def probability_labels(self, args):
		"""
		Compute the probability of a rule according
		to how many of the nodes it generates can
		be labelled according to a set of given
		labels.
		"""
		labels = args[0]
		probability = 1
		for (i,j) in self.spans:
			if (i,j) in labels.keys():
				continue
			else:
				probability = probability * 0.5
		self.probability = probability
		return
	
	def uniform_probability(self, args):
		"""
		Set probability to 1.
		"""
		self.probability = 1
	
	def lhs(self):
		return self._lhs
	
	def _lhs(self, labels):
		"""
		Create the left hand sides of the rule
		and set as an attribute.
		"""
		lhs = labels.get((self.root[0],self.root[1]), "%s-%s" % (self.root[0],self.root[1]))
		return Nonterminal(lhs)
	
	def rhs(self):
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

