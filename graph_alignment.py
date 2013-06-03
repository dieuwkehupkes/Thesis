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

	def link_to(self, node):
		"""
		Add a directed edge from this node to
		the given node.
		"""
		self.links.append(node)

	def paths_to(self, node):
		"""
		Returns a generator that calculates all
		paths to the given node. These paths
		are calculated recursively.
		"""
#		print "\tsearching path from", self, "to", node
		if node == self:
			# Reached our destination, stop searching.
#			print "reached destination"
			yield [self]
			return

		nid = str(node)
		if nid in self.reachable:
#			print "we already tracked paths from", self, "to", node
			# Already tracked paths to this point once
			if not self.reachable[nid]:
#				print "node was unreachable"
				# Node is unreachable from here, cancel
				# search.
				yield False
			else:
				for path in self.reachable[nid]:
					yield path
			return
		
		self.reachable[nid] = reachable = []
#		print "add", nid, "to reachable. Reachable from", self, '=', self.reachable		

		if len(self.links) == 0:
#			print "no more edges, no path"
			# No more edges; no path
			yield False 

		for link in self.links:
			if link <= node:
				for path in link.paths_to(node):
					if path:
#						print "found a path, add to known paths and return"
						# Yay, we found a path :)
						# Add to known paths and return
						full_path = [self] + path
						reachable.append(full_path)	
#						print self.reachable
						yield full_path
					else:
						self.reachable[nid] = False

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return str(self.value)

class Rule:
	"""
	Defines a rule from one span to a set
	of consecutive spans which's union
	forms it. This is mostly for convenient
	displaying, but in this class also the
	'probabilities' to the rules are assigned.
	"""
	def __init__(self, root, path,span_relations):
		"""
		Initialize a new rule as its root span
		and the path in the graph (consisting
		of an array of nodes) that forms its
		rule.
		"""
		self.root = root
		spans = []

		for i in xrange(0, len(path) - 1):
			spans.append((path[i].value, path[i+1].value))

		self.spans = spans
		self.span_relations = span_relations
		self.probability()

	def probability(self):
		"""
		Compute the probability of a rule given
		the span relations we want to have in
		the rule.
		"""
		probability = 1
		for key in self.span_relations:
			if key in self.spans:
				for dependent in self.span_relations[key]:
					if dependent in self.spans:
						probability = probability * 0.1
		self.probability = "[" + str(probability) + "]"

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		repr_list = (["%sN%s" % (i,j) for (i,j) in self.spans])
		return ("%sN%s -> %s %s" % 
			(self.root[0], self.root[1], " ".join(repr_list), self.probability))
