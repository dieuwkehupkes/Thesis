from alignments import *

class NodeTests:
	"""
	Tests functionality of Node class.
	"""
	def path_test_all(self):
		return self.path_test1() and self.path_test2() and self.path_test3()

	def path_test1(self):
		"""
		Test if paths are computed as intended by
		manually constructing a graph with 5 nodes
		and a couple of edges. Output True if correct
		paths are found, False otherwise.
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

	def path_test2(self):
		"""
		Test if shortest paths are computed as intended 
		by manually constructing a graph with 5 nodes
		and a couple of edges. Output True if correct
		paths are found, False otherwise.
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


	def path_test3(self):
		"""
		Test if shortest paths are computed as intended 
		by manually constructing a  fully connected
		graph with 5 nodes. Output True if correct
		paths are found, False otherwise.
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
	
	def worst_case_test(self,nr_of_nodes):
		"""
		Speed test for shortest_paths_to.
		Create a fully connected graph with
		nr_of_nodes nodes and compute the
		shortest_paths between all nodes.
		Output running time.
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
	
if __name__ == "__main__":
	x = NodeTests()
	print x.path_test_all()
	
