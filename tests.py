"""
Module containing functionality and speed tests for
other modules, including a test function that indicates
if everything still works as intended.
"""

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
#Tests Rule class


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
	for rule in a1.rules(Rule.probability_spanrels,[{}]):
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
	for rule in a1.hat_rules(Rule.probability_spanrels, [{}]):
		therules.append(str(rule))
	rules_man = ['0-5 -> 0-1 1-5','0-5 -> 0-2 2-5', '0-5 -> 0-3 3-5', '1-5 -> 1-2 2-5', '1-5 -> 1-3 3-5', '2-5 -> 2-3 3-5', '0-3 -> 0-1 1-3', '0-3 -> 0-2 2-3', '0-2 -> 0-1 1-2', '1-3 -> 1-2 2-3', '3-5 -> 3-4 4-5']
	return set(rules_man) == set(therules)

def rules_test_all():
	"""
	Return True if all rule tests return True
	"""
	return test_hatrules() and test_rules()


###############################
#Tests Alignments class

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
"""
Test Scoring Class
"""


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
	nr_of_deps = deps.nr_of_deps
	relations = deps.get_spanrels()
	scoring = Scoring(alignment, sentence, {})
	tree, score = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
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
	nr_of_deps = deps.nr_of_deps
	relations = deps.get_spanrels()
	scoring = Scoring(alignment, sentence, {})
	tree, score = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
	return score == 1.0

def score_test3():
	"""
	"""
	sentence = 'approval of the minutes of the previous sitting'
	alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
	dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)']
	deps = Dependencies(dependencies)
	labels = deps.labels(1,1,3)
	scoring = Scoring(alignment, sentence, labels)
	tree, score = scoring.score(Alignments.hat_rules, Rule.probability_labels, [labels])
	print tree
	print score
#	return score == 1.0
	
def score_test4():
	"""
	"""
	sentence = 'resumption of the session'
	alignment = '3-3 2-2 1-1 0-0'
	dependencies = ['root(ROOT-0, resumption-1)','prep(resumption-1, of-2)','det(session-4, the-3)','pobj(of-2, session-4)']
	deps = Dependencies(dependencies)
	labels = deps.labels(1,1,3)
	scoring = Scoring(alignment, sentence, labels)
	tree, score = scoring.score(Alignments.hat_rules, Rule.probability_labels, [labels])
	print tree
	print score
	return score == 1.0


def scoring_speedtest1(sentence_length):
	"""
	Test for a dummy sentence and monotone alignment 
	with only one dependency relation
	how long it takes to generate a grammar.
	"""
	import time
	time1 = time.time()
	s = [str(i) for i in xrange(sentence_length)]
	sentence = " ".join(s)
	a = [str(i)+'-'+str(i) for i in xrange(sentence_length)]
	alignment = " ".join(a)
	dependencies = ["root(ROOT-0, let-1)"]
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	scoring = Scoring(alignment, sentence, {})
	productions = scoring.alignment.hat_rules(Rule.probability_spanrels, [relations])
	for rule in productions:
		continue
	time2 = time.time()
	print "processing time:", time2-time1
	

def scoring_speedtest2(sentence_length):
	"""
	Test for a dummy sentence and alignment in which
	every target word is aligned to every source word
	with only one dependency relation how long it takes to generate a grammar.
	"""
	import time
	time1 = time.time()
	s = [str(i) for i in xrange(sentence_length)]
	sentence = " ".join(s)
	a = [str(i)+'-'+str(j) for i in xrange(sentence_length) for j in xrange(sentence_length)]
	alignment = " ".join(a)
	dependencies = ["root(ROOT-0, let-1)"]
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	scoring = Scoring(alignment, sentence, {})
	productions = scoring.alignment.hat_rules(Rule.probability_spanrels, [relations])	
	for rule in productions:
		continue
	time2 = time.time()
	print "processing time:", time2-time1


def scores_test_all():
	return score_test1() and score_test2()

####################################
# Test dependency class

"""
Test Dependency class.
"""

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

def labels_test1():
	"""
	Test labelling for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj', (1,2): 'head', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-head', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-head', (0,6): 'root'}
	print d.labels()
	labels = d.labels()
	return labels == man_labels

def labels_test2():
	"""
	Test for labelling the sentence 'I give the boy flowers',
	test for all combinations ldepth = {0,1}, rdepth = {0,1,2},
	and var_max = {0,1,2,3}
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj', (1,2): 'head', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-head', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-head', (0,6): 'root'}	
	Bool1 = man_labels == d.labels()
	Bool2 = d.labels() == d.labels(0,0,1) == d.labels(0,0,2) == d.labels(0,0,3) == d.labels(0,1,0) == d.labels(0,2,0) == d.labels(1,0,0) == d.labels(1,1,0) == d.labels(1,2,0) == d.labels(1,2,1) == d.labels(1,1,1) == d.labels(1,0,1) == d.labels(0,1,1) == d.labels(0,2,1)
	man_labels[(0,4)] = 'root' + '\\' +'dobj'
	Bool3 = d.labels(0,1,2) == man_labels == d.labels(0,2,2) == d.labels(0,1,2) == d.labels(0,1,3)
	man_labels[(0,2)] = 'root' + '\\' +'iobj+dobj'
	man_labels[(2,6)] = 'iobj+dobj'
	Bool4 = d.labels(0,2,3) == man_labels
	man_labels[(1,4)] = 'nsubj/root' + '\\' +'dobj'
	man_labels[(1,6)] = 'nsubj/root'
	labels = d.labels(1,2,3)
	Bool5 = man_labels == labels
	del man_labels[(0,2)]
	del man_labels[(2,6)]
	Bool6 = man_labels == d.labels(1,1,3)	
	del man_labels[(1,4)]
	Bool7 = man_labels == d.labels(1,2,2) == d.labels(1,1,2)
	del man_labels[(0,4)]
	Bool8 = man_labels == d.labels(1,0,2) == d.labels(1,0,3)
	return Bool1 and Bool2 and Bool3 and Bool4 and Bool5 and Bool6 and Bool7 and Bool8

def labels_test3():
	"""
	Test labelling for the sentence "He lives in a beautiful house".
	Test input tuples: (0,1,2), (1,0,2), (1,1,2)
	"""
	dependencies = ['nsubj(lives-2, He-1)', 'root(ROOT-0, lives-2)', 'prep(lives-2, in-3)', 'det(house-6, a-4)', 'amod(house-6, beautiful-5)', 'pobj(in-3, house-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj', (1,2): 'head', (2,6) :'prep', (2,3) : 'prep-head', (3,4) : 'det', (4,5): 'amod', (3,6): 'pobj', (5,6): 'pobj-head', (0,6): 'root'}
	Bool1 = man_labels == d.labels(0,0,1) == d.labels(1,0,1) == d.labels(0,1,1)
	man_labels[(1,6)] = 'nsubj/root'
	man_labels[(4,6)] = 'det/pobj'
	Bool2 = man_labels == d.labels(1,0,2)
	man_labels[(0,2)] = "root" + '\\' + "prep"
	Bool3 = man_labels == d.labels(1,1,2) == d.labels(1,1,3)
	del man_labels[(1,6)]
	del man_labels[(4,6)]
	Bool4 = man_labels == d.labels(0,1,2)
	return Bool1 and Bool2 and Bool3 and Bool4

def labels_annotation_test():
	"Test annotated labels for a manually constructed sentence"
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj-[0-1]', (1,2): 'head-[1-2]', (2,3): 'det-[2-3]', (2,4): 'iobj-[2-4]', (3,4): 'iobj-head-[3-4]', (4,5): 'det-[4-5]', (4,6): 'dobj-[4-6]', (5,6): 'dobj-head-[5-6]', (0,6): 'root-[0-6]'}
	labels = d.labels()
	new_labels = d.annotate_span(labels)
	return new_labels == man_labels

def dependencies_test_all():
	"""
	Run all dependency tests.
	"""
	return dependencies_test1() and labels_test1() and labels_test2() and labels_annotation_test() and labels_test3()
	
	
	
	
	
	
	

