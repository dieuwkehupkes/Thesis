"""
Module containing functionality and speed tests for
other modules, including a test function that indicates
if everything still works as intended.
"""

from graph_alignment import *
from alignments import *
from scoring import *
from file_processing import *


############################3
# Test all

def test_all():
	return path_test_all() and spans_test_all() and scores_test_all() and rules_test_all() and dependencies_test1()



####################################
#Test for graph_alignment

def path_test_all():
	return path_test1() and path_test2() and path_test3()

def path_test1():
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

def path_test2():
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


def path_test3():
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
	
def worst_case_test(nr_of_nodes):
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
	


#######################################3
#Tests rule and alignment


def test_rules():
	"""
	Test if the correct grammar is generated for
	the sentence 'My dog likes eating sausages',
	with alignment '0-0 1-1 2-2 2-3 3-5 4-4'.
	"""
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	sentence = 'My dog likes eating sausages'
	a1 = Alignments(alignment, sentence)
#	productions = a1.list_productions([])
	therules = []
	for rule in a1.rules([]):
		therules.append(str(rule))
	rules_man = ['0-5 -> 0-1 1-5','0-5 -> 0-2 2-5', '0-5 -> 0-3 3-5', '0-5 -> 0-1 1-2 2-5', '0-5 -> 0-1 1-3 3-5', '0-5 -> 0-2 2-3 3-5', '0-5 -> 0-3 3-4 4-5', '0-5 -> 0-1 1-2 2-3 3-5', '0-5 -> 0-1 1-3 3-4 4-5', '0-5 -> 0-2 2-3 3-4 4-5', '0-5 -> 0-1 1-2 2-3 3-4 4-5', '1-5 -> 1-2 2-5', '1-5 -> 1-3 3-5', '1-5 -> 1-2 2-3 3-5', '1-5 -> 1-3 3-4 4-5', '1-5 -> 1-2 2-3 3-4 4-5', '2-5 -> 2-3 3-5', '2-5 -> 2-3 3-4 4-5', '0-3 -> 0-1 1-3', '0-3 -> 0-2 2-3', '0-3 -> 0-1 1-2 2-3', '0-2 -> 0-1 1-2', '1-3 -> 1-2 2-3', '3-5 -> 3-4 4-5']
	return set(rules_man) == set(therules)

def test_hatrules():
	"""
	Test if the correct HATgrammar is generated for
	the sentence 'My dog likes eating sausages',
	with alignment '0-0 1-1 2-2 2-3 3-5 4-4'.
	"""
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	sentence = 'My dog likes eating sausages'
	a1 = Alignments(alignment, sentence)
	therules = []
	for rule in a1.hat_rules():
		therules.append(str(rule))
	rules_man = ['0-5 -> 0-1 1-5','0-5 -> 0-2 2-5', '0-5 -> 0-3 3-5', '1-5 -> 1-2 2-5', '1-5 -> 1-3 3-5', '2-5 -> 2-3 3-5', '0-3 -> 0-1 1-3', '0-3 -> 0-2 2-3', '0-2 -> 0-1 1-2', '1-3 -> 1-2 2-3', '3-5 -> 3-4 4-5']
	return set(rules_man) == set(therules)

def rules_test_all():
	"""
	Return True if all rule tests return True
	"""
	return test_hatrules() and test_rules()


###############################
#Span tests

def span_test1():
	"""
	Test if correct spans are found for
	a monotone alignment with no unaligned words
	"""
	alignment = '0-0 1-1 2-2 3-3 4-4'
	spanlist_man = [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	return spanlist == spanlist_man

def span_test2():
	"""
	Test if correct spans are found for a non 
	monotone many-to-many alignment, with no
	unaligned words on source nor targetside.
	"""
	alignment = '0-5 1-4 1-6 2-3 3-0 3-2 4-1 5-0 5-2'
	spanlist_man = [(0,1), (0,2), (0,3), (1,2), (0,6), (2,3), (2,6), (3,4), (3,6), (4,5),(5,6)]
	spanlist_man.sort()
	s = Alignments(alignment, '0 1 2 3 4 5')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	return spanlist == spanlist_man


def span_test3():
	"""
	Test if correct spans are found for a 
	one-to-one alignment with some
	unaligned words on source and target side
	"""
	alignment = '1-1 2-2 4-4'
#	print 'alignment:', alignment
#	print "\nManually constructed span list:"	
	spanlist_man = [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]
	spanlist_man.sort()
#	print spanlist_man
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	return spanlist == spanlist_man

	
def span_test4():
	"""
	Test if correct spans are found for 
	a non monotone many-to-many alignment with
	unaligned words on both and target side.
	"""
	alignment = '0-2 2-0 0-4 4-4 4-5'
	spanlist_man = [(0,1), (0,2), (0,5), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4), (3,5), (4,5)]
	spanlist_man.sort()
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	return spanlist == spanlist_man

def spans_test_all():
	"""
	Return True if all span tests return True
	"""
	return span_test1() and span_test2() and span_test3() and span_test4()

###########################
#Test scoring class

def score_test1():
	"""
	Test if the correct score is found for sentence
	'my dog likes eating sausage', alignment
	'0-0 1-1 2-2 2-3 3-5 4-4', with dependencies
	'nsubj(likes-3, dog-2)', 'root(ROOT-0, likes-3)',
	'xcomp(likes-3, eating-4)' and 'dobj(eating-4, sausages-5)'.
	"""
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	labels = deps.labels()
	scoring = Scoring(alignment, sentence, relations, labels)
	productions = scoring.alignment.rules(relations,labels)
#	for production in productions:
#		print production
#	productions = scoring.alignment.rules(relations,labels)	
	grammar = scoring.grammar(productions)
	parse = scoring.parse(grammar)
	score = scoring.score(parse)
	return score == 1.0

def score_test2():
	"""
	Test if the correct score is found for sentence
	'european growth is inconceivable without solidarity .'
	with alignment "0-0 1-1 2-2 3-3 4-4 5-5 6-6" and dependencies
	'nn(growth-2, european-1)', 'nsubj(inconceivable-4, growth-2)',
	'cop(inconceivable-4, is-3)', 'root(ROOT-0, inconceivable-4)', 
	'prep(inconceivable-4, without-5)' and 'pobj(without-5, solidarity-6)'
	"""
	sentence = "european growth is inconceivable without solidarity ."
	alignment = "0-0 1-1 2-2 3-3 4-4 5-5 6-6"
	dependencies = ['nn(growth-2, european-1)','nsubj(inconceivable-4, growth-2)','cop(inconceivable-4, is-3)','root(ROOT-0, inconceivable-4)','prep(inconceivable-4, without-5)','pobj(without-5, solidarity-6)']
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	labels = deps.labels()
	scoring = Scoring(alignment, sentence, relations, labels)
	productions = scoring.alignment.rules(relations,labels)
	grammar = scoring.grammar(productions)
	parse = scoring.parse(grammar)
	score = scoring.score(parse)	
	return score == 1.0

def scores_test_all():
	return score_test1() and score_test2()

####################################3
# Test dependency class
def dependencies_test1():
	"""
	Test if correct span relations are extracted
	from a list of dependencies
	"""
	dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)']
	d = Dependencies(dependencies)
	spanrels = d.get_spanrels()
	manual_spanrels= {(1,2): [(0,1)],(5,6): [(0,2),(3,4),(4,5), (6,11)], (7,8):[(6,7),(8,11)],(8,9): [(9,11)], (10,11): [(9,10)]}
	return spanrels == manual_spanrels

def dependencies_test_all():
	return dependencies_test1()




