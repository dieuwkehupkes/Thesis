from dependencies import *

class DependencyTests():
	def spanrelations_test(self):
		"""
		Test if spanrelations are extracted correctly
		from a list of dependencies
		"""
		dependencies = ['nn(President-2, Mr-1)','nsubj(welcome-6, President-2)','nsubj(welcome-6, I-4)','aux(welcome-6, would-5)','root(ROOT-0, welcome-6)','det(action-8, some-7)','dobj(welcome-6, action-8)','prep(action-8, in-9)','det(area-11, this-10)','pobj(in-9, area-11)']
		d = Dependencies(dependencies)
		spanrels = d.spanrelations(interpunction = False)
		manual_spanrels= {(1,2): set([(0,1)]), (5,6): set([(0,2),(3,4),(4,5),(6,11)]), (7,8):set([(6,7),(8,11)]),(8,9): set([(9,11)]), (10,11): set([(9,10)])}
		return spanrels == manual_spanrels

	def labels_test1(self):
		"""
		Test functioning plain labelling for sentence
		'I give the boy some flowers'
		"""
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		man_labels = {(0,1): 'nsubj', (1,2): 'root', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-h', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-h', (0,6): 'ROOT'}
		labels = d.labels()
		return labels == man_labels

	def labels_test2(self):
		"""
		Test functioning deeper labelling for the sentence
		'I give the boy flowers'. Test for test for all
		combinations ldepth = {0,1}, rdepth = {0,1,2},
		and var_max = {0,1,2,3}
		"""
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		man_labels = {(0,1): 'nsubj', (1,2): 'root', (2,3): 'det', (2,4): 'iobj', (3,4): 'iobj-h', (4,5): 'det', (4,6): 'dobj', (5,6): 'dobj-h', (0,6): 'ROOT'}	
		Bool1 = man_labels == d.labels()
		Bool2 = d.labels() == d.labels(0,0,1) == d.labels(0,0,2) == d.labels(0,0,3) == d.labels(0,1,0) == d.labels(0,2,0) == d.labels(1,0,0) == d.labels(1,1,0) == d.labels(1,2,0) == d.labels(1,2,1) == d.labels(1,1,1) == d.labels(1,0,1) == d.labels(0,1,1) == d.labels(0,2,1)
		man_labels[(0,4)] = 'ROOT' + '\\' +'dobj'
		Bool3 = d.labels(0,1,2) == man_labels == d.labels(0,2,2) == d.labels(0,1,2) == d.labels(0,1,3)
		man_labels[(0,2)] = 'ROOT' + '\\' +'iobj+dobj'
		man_labels[(2,6)] = 'iobj+dobj'
		Bool4 = d.labels(0,2,3) == man_labels
		man_labels[(1,4)] = 'nsubj/ROOT' + '\\' +'dobj'
		man_labels[(1,6)] = 'nsubj/ROOT'
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

	def labels_test3(self):
		"""
		Test functionining deeper labelling for the 
		sentence "He lives in a beautiful house".
		Test input tuples: (0,1,2), (1,0,2), (1,1,2).
		"""
		dependencies = ['nsubj(lives-2, He-1)', 'root(ROOT-0, lives-2)', 'prep(lives-2, in-3)', 'det(house-6, a-4)', 'amod(house-6, beautiful-5)', 'pobj(in-3, house-6)']
		d = Dependencies(dependencies)
		man_labels = {(0,1): 'nsubj', (1,2): 'root', (2,6) :'prep', (2,3) : 'prep-h', (3,4) : 'det', (4,5): 'amod', (3,6): 'pobj', (5,6): 'pobj-h', (0,6): 'ROOT'}
		Bool1 = man_labels == d.labels(0,0,1) == d.labels(1,0,1) == d.labels(0,1,1)
		man_labels[(1,6)] = 'nsubj/ROOT'
		man_labels[(4,6)] = 'det/pobj'
		Bool2 = man_labels == d.labels(1,0,2)
		man_labels[(0,2)] = "ROOT" + '\\' + "prep"
		Bool3 = man_labels == d.labels(1,1,2) == d.labels(1,1,3)
		del man_labels[(1,6)]
		del man_labels[(4,6)]
		Bool4 = man_labels == d.labels(0,1,2)
		return Bool1 and Bool2 and Bool3 and Bool4

	def labels_annotation_test(self):
		"Test annotated labels for a manually constructed sentence"
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		man_labels = {(0,1): 'nsubj-[0-1]', (1,2): 'root-[1-2]', (2,3): 'det-[2-3]', (2,4): 'iobj-[2-4]', (3,4): 'iobj-h-[3-4]', (4,5): 'det-[4-5]', (4,6): 'dobj-[4-6]', (5,6): 'dobj-h-[5-6]', (0,6): 'ROOT-[0-6]'}
		labels = d.labels()
		new_labels = d.annotate_span(labels)
		return new_labels == man_labels

	def rr_test(self):
		"""
		Test right branching relations for sentence 'I give the boy some flowers'
		"""
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		relations = d.spanrelations(True,False)
		man_relations = {(1, 2): set([(0, 1), (2, 4), (4, 6)]), (5, 6): set([(4, 5)]), (3, 4): set([(2, 3)]), (1,6): set([(0,1)]), (1,4): set([(4,6)])}
		return relations == man_relations

	def lr_test(self):
		"""
		Test left branching relations for sentence 'I give the boy some flowers'
		"""
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		relations = d.spanrelations(False,True)
		man_relations = {(1, 2): set([(0, 1), (2, 4), (4, 6)]), (5, 6): set([(4, 5)]), (3, 4): set([(2, 3)]), (0,4): set([(4,6)]), (0,2): set([(2,4)])}
		return relations == man_relations

	def allr_test1(self):
		"""
		Test left branching relations for sentence 'I give the boy some flowers'
		"""
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies)
		relations = d.spanrelations(True,True)
		man_relations = {(1, 2): set([(0, 1), (2, 4), (4, 6)]), (5, 6): set([(4, 5)]), (3, 4): set([(2, 3)]), (0,4): set([(4,6)]), (0,2): set([(2,4)]), (1,4): set([(0,1),(4,6)]), (1,6): set([(0,1)])}	
		return relations == man_relations

	def allr_test2(self):
		dependencies = ['det(minutes-2, the-1)','nsubjpass(distributed-13, minutes-2)','prep(minutes-2, of-3)','pobj(of-3, the-4)','amod(the-4, sitting-5)','prep(the-4, on-6)','pobj(on-6, Thursday-7)','num(September-10, 21-9)','nsubjpass(distributed-13, September-10)','aux(distributed-13, have-11)','auxpass(distributed-13, been-12)','root(ROOT-0, distributed-13)']
		d = Dependencies(dependencies)
		relations = d.spanrelations(True,True)
		man_relations = {(8, 13): set([(0, 7), (0,8)]), (5, 6): set([(6, 7),(6,8)]), (10, 13): set([(8, 10),(7,10)]), (9, 10): set([(8, 9), (7,9)]), (2, 3): set([(3, 7),(3,8)]), (3, 5): set([(5, 7),(5,8)]), (1, 2): set([(0, 1), (2, 7),(2,8)]), (12, 13): set([(11, 12), (10, 11), (8, 10), (0, 7), (0,8), (7,10)]), (1, 7): set([(0, 1)]), (3, 4): set([(4, 5), (5, 7),(5,8)]), (0, 2): set([(2, 7),(2,8)]), (11, 13): set([(10, 11)]), (7,13): set([(0,7)]),(1,8):set([(0,1)])}
		for key in man_relations.keys():
			if man_relations[key] != relations[key]:
				print 'key', key
				print 'man', man_relations[key], 'auto', relations[key]
		return relations == man_relations

	def test_all_labels(self):
		"""
		Test for label all function
		"""
		sentence = 'I give the boy some flowers .'
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies, sentence)
		man_labels = {}
		postags = dict(zip([(i,i+1) for i in xrange(7)],['nsubj', 'root','det','iobj-h','det','dobj-h','PUNCT']))
		man_labels.update(postags)
		deplabels = dict(zip([(2,4),(4,6),(0,6)],['iobj','dobj','ROOT']))
		man_labels.update(deplabels)
		compound1 = dict(zip([(0,7),(2,6),(1,4),(0,2),(4,7),(1,3),(3,5),(2,5),(5,7),(0,5),(3,6)],['ROOT+PUNCT','iobj+dobj', 'root+iobj','nsubj+root','dobj+PUNCT','root+det','iobj-h+det','iobj+det','dobj-h+PUNCT','ROOT\dobj-h','iobj-h+dobj']))
		man_labels.update(compound1)
		compound2 = dict(zip([(0,4),(1,6),(1,7)],['ROOT\dobj','nsubj/ROOT','nsubj/ROOT+PUNCT']))
		rest = dict(zip([(2,7),(3,7),(0,3),(1,5)],['iobj+dobj+PUNCT','iobj-h+dobj+PUNCT','nsubj+root+det','root+iobj+det']))
		man_labels.update(rest)
		labels = d.label_all()
		man_labels.update(compound2)
		return labels == man_labels

	def dependencies_test_all(self):
		"""
		Run all dependency tests.
		"""
		return self.spanrelations_test() and self.labels_test1() and self.labels_test2() and self.labels_annotation_test() and self.labels_test3() and self.rr_test() and self.lr_test() and self.allr_test1() and self.allr_test2() and self.test_all_labels()
	
if __name__ == "__main__":
	x = DependencyTests()
	print x.test_all_labels()
#	print x.dependencies_test_all()
