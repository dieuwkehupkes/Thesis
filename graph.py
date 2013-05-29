"""
Calculates trees of spans in a permutated sentence
using a graph approach.
(Wait, I just realized I'm not responsible for explaining
 this, go ahead Djoek ;-])

Say we have a b c d e
Permutated to c e b d a

So we get:
0 1 2 3 4 5
 c e b d a

Let's represent the spans using the
positions between the words. The valid
spans then are:
[i,i+1]
[0,4]
[0,5]

Now let's model this as a graph, where
the positions between the words are the
vertices. There is a directed edge from
i to j if [i,j] is a valid span.

Every path from 1 to n then corresponds
to a path in the tree that we're looking for.
"""
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
		if node == self:
			# Reached our destination, stop searching.
			yield [self]
			return

		nid = str(node)
		if nid in self.reachable:
			# Already tracked paths to this point once
			if not self.reachable[nid]:
				# Node is unreachable from here, cancel
				# search.
				yield False
			else:
				for path in self.reachable[nid]:
					yield path
			return

		self.reachable[nid] = reachable = []
		
		if len(self.links) == 0:
			# No more edges; no path
			yield False 

		for link in self.links:
			for path in link.paths_to(node):
				if path:
					# Yay, we found a path :)
					# Add to known paths and return
					full_path = [self] + path
					reachable.append(full_path)	

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
	displaying.
	"""
	def __init__(self, root, path):
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

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		repr_list = (["[%s,%s]" % (i,j) for (i,j) in self.spans])
		return ("[%s,%s] -> %s" % 
			(self.root[0], self.root[1], " ".join(repr_list)))

class Words:
	"""
	A class that represents a sentence using a
	list of words. You can calculate all rules
	over permutations using the 'rules' method.
	You just pass in a list of permutations now,
	so this no longer actually contains a class
	context (making it a collection of functions
	really)
	"""

	def spans(self, permutation):
		"""
		Returns a generator with all valid spans 
		from the given permutation. The given
		permutation should of course contain
		all the elements in the current
		word set.

		The given permutation argument is a set
		permutation: a list of lists, where the
		nested lists consist of positions in
		the original string.
		"""

		"""
		Now, using a vaguely brute-force like
		approach, calculate all spans and check
		if they're valid. There aren't actually
		that many spans, so this should still
		be pretty fast.
		"""
		l = len(permutation) + 1
		for i in xrange(0, l):
			for j in xrange(i + 1, l):
				"""
				Flatten the permutations array and select only
				unique items.
				This could actually be achieved in a oneliner,
				but this approach, while more verbose, is clearer
				(and doesn't require allocating an additional list).
				"""
				uniq = set()
				for sublist in permutation[i:j]:
					for item in sublist:
						uniq.add(item)

				span = [item for item in uniq]

				"""
				Now sort the span, and check
				if it is of the form:
				[i, i+1, i+2, i+3, ...]

				If we'd used a sorted set
				this could me made faster with little
				extra effort; unfortunately Python
				doesn't have one built-in.
				"""
				span.sort()
				valid = (span[0] + len(span) - 1) == span[-1]

				if valid:
					yield (i, j)

	def rules(self, permutation):
		"""
		Creates a graph of all valid spans, and
		calculates all paths between span endpoints.

		A generator is returned for all the valid
		rules in the permutation.
		"""
		# Create nodes for all positions between words
		nodes = [Node(i) for i in xrange(0, len(permutation) + 1)]
		spans = []
		
		# Construct the graph by creating the edges
		for (i,j) in self.spans(permutation):
			nodes[i].link_to(nodes[j])
			spans.append((i,j))
	
		for (i,j) in spans:
			for path in nodes[i].paths_to(nodes[j]):
				if not path or len(path) == 2:
					# No rules possible, or path points to itself
					continue
			
				# Build up the rule as list of spans between
				# nodes.
				yield Rule((i, j), path)


def static_test():
	w = Words()
	permutation = [[3], [5], [2], [4], [1]]

	for rule in w.rules(permutation):
		print rule

def static_test_2():
	w = Words()
	permutation = [[i] for i in xrange(0, 40)]
	n = 0

	for rule in w.rules(permutation):
		n += 1
		print "%s"% (rule)

	print "Total of %d rules" % n

def test():
	import random

	n = 10
	permutation = [[random.randint(0, n)] for i in xrange(0, n)]
	w = Words()

	for rule in w.rules(permutation):
		print rule
