"""
Module for testing behaviour of Dependency class
"""


def dependencies_test1():
	"""
	Test if correct span relations are extracted
	from a list of dependencies
	"""
	dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)']
	d = Dependencies(dependencies)
	spanrels = d.spanrelations()
	manual_spanrels= {(1,2): [(0,1)],(5,6): [(0,2),(3,4),(4,5), (6,11)], (7,8):[(6,7),(8,11)],(8,9): [(9,11)], (10,11): [(9,10)]}
	return spanrels == manual_spanrels

def labels_test1():
	"""
	Test labelling for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	man_labels = {(0,1): 'nsubj', (1,2): 'head', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-head', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-head', (0,6): 'root'}
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

def rightbranching_relations_test():
	"""
	Test right branching relations for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	relations = d.spanrelations(True,False)
	man_relations = {(1, 2): [(0, 1), (2, 4), (4, 6)], (5, 6): [(4, 5)], (3, 4): [(2, 3)], (1,6): [(0,1)], (1,4): [(4,6)]}
	return relations == man_relations

def leftbranching_relations_test():
	"""
	Test left branching relations for sentence 'I give the boy some flowers'
	"""
	dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
	d = Dependencies(dependencies)
	relations = d.spanrelations(False,True)
	man_relations = {(1, 2): [(0, 1), (2, 4), (4, 6)], (5, 6): [(4, 5)], (3, 4): [(2, 3)], (0,4): [(4,6)], (0,2): [(2,4)]}
	return relations == man_relations

def dependencies_test_all():
	"""
	Run all dependency tests.
	"""
	return dependencies_test1() and labels_test1() and labels_test2() and labels_annotation_test() and labels_test3() and rightbranching_relations_test() and leftbranching_relations_test()
