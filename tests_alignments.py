from alignments import *
from dependencies import *

class AlignmentsTests():
	"""
	Tests Alignments Module
	"""
	def span_test1(self):
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

	def span_test2(self):
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


	def span_test3(self):
		"""
		Test if correct spans are found for a 
		one-to-one alignment with some
		unaligned words on source and target side
		"""
		alignment = '1-1 2-2 4-4'
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
	
	def span_test4(self):
		"""
		Test if correct spans are found for 
		a non monotone many-to-many alignment with
		unaligned words on both and target side.
		"""
		alignment = '0-2 2-0 0-4 4-4 4-5'
		spanlist_man = [(0,1), (0,5), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4), (4,5)]
		spanlist_man.sort()
		s = Alignments(alignment, '0 1 2 3 4')
		spans = s.spans()
		spanlist = []	
		for span in spans:
			spanlist.append(span)
		spanlist.sort()
		return spanlist == spanlist_man

	def spans_test_all(self):
		"""
		Return True if all span tests return True
		"""
		return self.span_test1() and self.span_test2() and self.span_test3() and self.span_test4()
	
	def consistency_test1(self):
		tree = nltk.Tree('(ROOT (NP (NP (NN resumption)) (PP (IN of) (NP (DT the) (NN session)))))')
		sentence = 'resumption of the session'
		alignment = '0-0 1-1 2-2 3-3'
		a = Alignments(alignment,sentence)
		score = a.agreement(tree)
		return score == 1
	
	def consistency_test2(self):
		tree = nltk.Tree('(ROOT (NP (NP (NN approval)) (PP (IN of) (NP (DT the) (NNS minutes))) (PP (IN of) (NP (DT the) (JJ previous) (NN sitting)))))')
		sentence = 'approval of the minutes of the previous sitting'
		alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		a = Alignments(alignment,sentence)
		score = a.agreement(tree)
		return score == 0.8
		
	def consistency_test3(self):
		tree = nltk.Tree('(ROOT ( NP ( NP (NN approval )) (PP of the minutes) (PP (IN of) (NP (DT the ) (JJ previous ) (NN sitting ) ))))')
		sentence = 'approval of the minutes of the previous sitting'
		alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		a = Alignments(alignment,sentence)
		score = a.agreement(tree)
		return score == 1
	
	def dict_test(self):
		"""
		Test the function Alignments.HAT_dict()
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		a = Alignments(alignment,sentence)
		hat_dict = a.HAT_dict(labels)
		assert hat_dict == {'A': [('0', 'B'), ('F', 'E'), ('C', 'D')], 'C': [('0', 'G'), ('F', '2')], 'B': [('1', 'E'), ('G', 'D')], 'E': [('2', 'D')], 'D': [('4', '3')], 'G': [('1', '2')], 'F': [('0', '1')], '1': [('b',)], '0': [('a',)], '3': [('e',)], '2': [('c',)], '4': [('d',)]}, 'HAT dictionary not correctly created'
		return True
	
	def prob_function_test(self):
		"""
		Test the function Alignments.probmass()
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		a = Alignments(alignment,sentence)
		HAT_dict = a.HAT_dict(labels)
		probs = {}
		a.probmass({}, HAT_dict, probs, 'A')
		assert probs == {('B', 'G', 'D'): 1, ('A', 'F', 'E'): 1, ('3', 'e'): 1, ('2', 'c'): 1, ('0',): 1, ('2',): 1, ('A', '0', 'B'): 2, ('4',): 1, ('A',): 5, ('C',): 2, ('1', 'b'): 1, ('E',): 1, ('G',): 1, ('E', '2', 'D'): 1, ('C', 'F', '2'): 1, ('B', '1', 'E'): 1, ('C', '0', 'G'): 1, ('1',): 1, ('G', '1', '2'): 1, ('3',): 1, ('F', '0', '1'): 1, ('D', '4', '3'): 1, ('0', 'a'): 1, ('B',): 2, ('D',): 1, ('4', 'd'): 1, ('A', 'C', 'D'): 2, ('F',): 1}
		return True
	
	def update_test(self):
		"""
		Test the function Alignments.update()
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		a = Alignments(alignment,sentence)
		counts = a.compute_weights('A', labels = labels)
		assert counts == {'A': {('F', 'E'): 0.2, ('C', 'D'): 0.4, ('0', 'B'): 0.4}, 'C': {('F', '2'): 0.2, ('0', 'G'): 0.2}, 'B': {('G', 'D'): 0.2, ('1', 'E'): 0.2}, 'E': {('2', 'D'): 0.4}, 'D': {('4', '3'): 1.0}, 'G': {('1', '2'): 0.4}, 'F': {('0', '1'): 0.4}, '1': {('b',): 1.0}, '0': {('a',): 1.0}, '3': {('e',): 1.0}, '2': {('c',): 1.0}, '4': {('d',): 1.0}}
		return True
	
	def update_test2(self):
		"""
		Test the function Alignments.update() with input PCFG
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		pcfg_dict = {'A': {('0','B'): 0.5, ('C','D'): 0.2, ('F','E'): 0.3}, 'B': {('G','D'):0.8, ('1','E'):0.25}, 'C': {('0','G'):0.4, ('F','2'):0.8}, 'D': {('4','3'):0.1}, 'E': {('2','D'):0.1}, 'F': {('0','1'):0.5}, 'G': {('1','2'):0.75}, '0':{('a',):1}, '1': {('b',):1}, '2':{('c',):1}, '3': {('e',):1}, '4': {('d',):1}}
		a = Alignments(alignment,sentence)
		counts = a.compute_weights('A', counts = {}, pcfg_dict = pcfg_dict, labels = labels)
		assert counts == {'A': {('F', 'E'): 0.0320855614973262, ('C', 'D'): 0.2994652406417112, ('0', 'B'): 0.6684491978609625}, 'C': {('F', '2'): 0.1711229946524064, ('0', 'G'): 0.1283422459893048}, 'B': {('G', 'D'): 0.641711229946524, ('1', 'E'): 0.026737967914438495}, 'E': {('2', 'D'): 0.05882352941176469}, 'D': {('4', '3'): 0.9999999999999999}, 'G': {('1', '2'): 0.7700534759358287}, 'F': {('0', '1'): 0.2032085561497326}, '1': {('b',): 0.9999999999999999}, '0': {('a',): 0.9999999999999999}, '3': {('e',): 0.9999999999999999}, '2': {('c',): 0.9999999999999999}, '4': {('d',): 0.9999999999999999}}
#		for lhs in counts:
#			for rhs in counts[lhs]:
#				print '%s --> %s\t%f' % (lhs, ' '.join(rhs), counts[lhs][rhs])
		return True
	
	def grammar_test(self):
		"""
		Test function for Alignments.compute_weights with span adjusted labels.
		"""
		sentence = 'I give the boy some flowers'
		alignment = '0-0 1-1 2-2 3-3 4-4 5-5'
		dependencies = ['nsubj(give-2, I-1)','root(ROOT-0, give-2)','det(boy-4, the-3)','iobj(give-2, boy-4)','det(flowers-6, some-5)','dobj(give-2, flowers-6)']
		d = Dependencies(dependencies, sentence)
		l = Labels(d.dependency_labels())
		labels = l.label_most()
		labels = l.annotate_span(labels)
		pcfg_dict = {'iobj-h+det': {('iobj-h', 'det'): 0.333}, 'iobj-h+dobj': {('iobj-h', 'dobj'): 0.11904761904761904, ('iobj-h+det', 'dobj-h'): 0.11904761904761904}, 'iobj+det': {('iobj', 'det'): 0.11904761904761904, ('det', 'iobj-h+det'): 0.11904761904761904}, 'ROOT/dobj-h': {('ROOT/dobj', 'det'): 0.11904761904761904, ('nsubj+root', 'iobj+det'): 0.047619047619047616, ('nsubj+root+det', 'iobj-h+det'): 0.047619047619047616, ('nsubj', 'root+iobj+det'): 0.11904761904761904}, 'det': {('the',): 1.0000000000000004, ('some',): 1.0000000000000002}, 'nsubj': {('I',): 1.0}, 'nsubj\\ROOT': {('root', 'iobj+dobj'): 0.11904761904761904, ('root+det', 'iobj-h+dobj'): 0.047619047619047616, ('root+iobj', 'dobj'): 0.047619047619047616, ('root+iobj+det', 'dobj-h'): 0.11904761904761904}, 'dobj': {('det', 'dobj-h'): 0.3333333333333333}, 'ROOT/dobj': {('nsubj+root', 'iobj'): 0.047619047619047616, ('nsubj+root+det', 'iobj-h'): 0.09523809523809523, ('nsubj', 'root+iobj'): 0.09523809523809523}, 'ROOT': {('nsubj+root+det', 'iobj-h+dobj'): 0.09523809523809523, ('nsubj', 'nsubj\\ROOT'): 0.33, ('nsubj+root', 'iobj+dobj'): 0.11904761904761904, ('ROOT/dobj-h', 'dobj-h'): 0.33, ('ROOT/dobj', 'dobj'): 0.11904761904761904}, 'dobj-h': {('flowers',): 1.0}, 'nsubj+root+det': {('nsubj+root', 'det'): 0.11904761904761904, ('nsubj', 'root+det'): 0.11904761904761904}, 'root': {('give',): 1.0000000000000002}, 'iobj+dobj': {('det', 'iobj-h+dobj'): 0.09523809523809523, ('iobj+det', 'dobj-h'): 0.09523809523809523, ('iobj', 'dobj'): 0.047619047619047616}, 'root+iobj': {('root+det', 'iobj-h'): 0.11904761904761904, ('root', 'iobj'): 0.11904761904761904}, 'root+iobj+det': {('root', 'iobj+det'): 0.09523809523809523, ('root+det', 'iobj-h+det'): 0.047619047619047616, ('root+iobj', 'det'): 0.09523809523809523}, 'iobj': {('det', 'iobj-h'): 0.33}, 'root+det': {('root', 'det'): 0.33}, 'iobj-h': {('boy',): 1.0}, 'nsubj+root': {('nsubj', 'root'): 0.33} }
		a = Alignments(alignment,sentence)
		counts = a.compute_weights('ROOT-[0-6]', pcfg_dict = pcfg_dict, labels = labels)
		for lhs in counts:
			for rhs in counts[lhs]:
				print '%s --> %s\t%f' % (lhs, ' '.join(rhs), counts[lhs][rhs])
		return counts	
	
	
	def alignment_test_all(self):
		return self.spans_test_all() and self.consistency_test1() and self.consistency_test2() and self.consistency_test3() and self.dict_test() and self.prob_function_test() and self.update_test() and self.update_test2()
	
if __name__ == "__main__":
	x = AlignmentsTests()
#	x.update_test2()
	print x.alignment_test_all()
#	x.grammar_test()
	
	

