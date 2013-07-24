import nltk
from nltk.grammar import *
from copy import deepcopy

class Waypoint:
	"""
	Defines a waypoint in a one-directional path. This
	allows us to save memory by not having to copy path
	arrays for every path.
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
		return self.__str__()
		
	def __hash__(self):
		return self.value
		
	def __eq__(self, other):
		if isinstance(other, Node):
			return self.value == other.value
		else:
			return False
		
	def __neq__(self, other):
		return (not self.__eq__(other))

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
	def __init__(self, root, path,span_relations = {}, labels = {}):
		"""
		Initialize a new rule as its root span
		and the path in the graph (consisting
		of an array of nodes) that forms its
		rule.
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
		self.span_relations = span_relations
		self.rhs()
		self.lhs()
		
	def probability_spanrels(self):
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
			if (i,j) in self.labels:
				continue
			else:
				probability = 0.5 * probability
		self.probability = probability
	
	def uniform_probability(self):
		"""
		Set uniform probability
		"""
		self.probability = 1
	
	def lhs(self):
		lhs = self.labels.get((self.root[0],self.root[1]), "%s-%s" % (self.root[0],self.root[1]))
#		self.lhs = Nonterminal(lhs)
		self.lhs = lhs
		
	def rhs(self):
		rhs_list = ([self.labels.get((i,j),"%s-%s" % (i,j)) for (i,j) in self.spans])
		self.rhs = rhs_list

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		return ("%s -> %s" % 
			(self.lhs, " ".join(self.rhs)))
			


#############################################################################################
#Testing

def test1():
	"""
	Test if all paths are found in a manually
	constructed graph with t nodes
	"""
	#create sample graph
	nodes = [Node(i) for i in xrange(0,5)]
	links = [(0,1),(0,2),(1,2),(1,4),(2,3),(2,4),(3,4),(0,4)]
	for (i,j) in links:
		nodes[i].link_to(nodes[j])
	#find all paths
	path_list = []
	for (i,j) in links:
		paths = nodes[i].paths_to(nodes[j])
		for path in paths:
			path_list.append(str(path))
	man_paths = [[0,1,2,3,4],[0,1,2,4], [0,2,3,4], [0,2,4], [0,1,4],[1,2,3,4],[1,2,4], [0,1,2], [2,3,4], [0,1],[1,2],[2,3],[3,4],[2,4],[0,2],[1,4],[0,4]]
	man_pathlist = [str(i) for i in man_paths]
	return set(path_list) == set(man_pathlist)

def test2():
	"""
	Test if all shortest paths are found in a
	manually constructed graph with 5 nodes
	"""
	#create sample graph
	nodes = [Node(i) for i in xrange(0,5)]
	links = [(0,1),(0,2),(1,2),(1,4),(2,3),(2,4),(3,4),(0,4)]
	for (i,j) in links:
		nodes[j].link_to(nodes[i])
	#find all paths
	path_list = []
	for (i,j) in links:
		paths = nodes[i].shortest_paths_to(nodes[j])
		for path in paths:
			path_list.append(str(path))
	man_paths = [[0,1],[1,2],[2,3],[3,4],[0,1,4], [0,2,4], [0,1,2], [1,2,4],[2,3,4]]
	man_pathlist = [str(i) for i in man_paths]
	return set(path_list) == set(man_pathlist)


def test3():
	"""
	Test if all shortest paths are found
	in a fully conected constructed graph
	with 5 nodes
	"""
	nodes = [Node(i) for i in xrange(0,5)]
	links = [(0,1),(0,2),(0,3),(0,4),(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)]
	for (i,j) in links:
		nodes[j].link_to(nodes[i])
	#find all paths
	path_list = []
	for (i,j) in links:
		paths = nodes[i].shortest_paths_to(nodes[j])
		for path in paths:
			path_list.append(str(path))
	man_paths = [[0,1],[1,2],[2,3],[3,4],[0,1,4],[0,2,4],[0,3,4],[0,1,3],[0,2,3],[1,2,4],[1,3,4], [0,1,2],[1,2,3],[2,3,4]]
	man_pathlist = [str(i) for i in man_paths]
	return set(path_list) == set(man_pathlist)
	
def worst_case_test(nr_of_nodes):
	"""
	Test the worst case running time for
	a graph with n nodes
	"""
	import time
	t1 = time.time()
	nodes = [Node(i) for i in xrange(0,nr_of_nodes)]
	links = [(i,j) for i in xrange(0,nr_of_nodes) for j in xrange(0,nr_of_nodes) if i< j]
	for (i,j) in links:
		nodes[j].link_to(nodes[i])
	path_list = []
	for (i,j) in links:
		paths = nodes[i].shortest_paths_to(nodes[j])
		for path in paths:
			path_list.append(str(path))
	t2 = time.time()
	running_time = t2 - t1
	print 'running time ', running_time

