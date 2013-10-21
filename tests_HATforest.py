from alignments import *
from dependencies import *
from labelling import *
from process_hats import *

class HATsTests():
	"""
	Contains tests for the HATforest class.
	"""
	def probs_test(self):
		"""
		Test the function HATs.probmass()
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		a = Alignments(alignment,sentence)
		HAT_dict = a.HAT_dict(labels)
		probs = {}
		h = HATGrammar(HAT_dict, 'A')
		h.probmass('A', probs = probs)
		assert probs == {('B', 'G', 'D'): 1, ('A', 'F', 'E'): 1, ('3', 'e'): 1, ('2', 'c'): 1, ('0',): 1, ('2',): 1, ('A', '0', 'B'): 2, ('4',): 1, ('A',): 5, ('C',): 2, ('1', 'b'): 1, ('E',): 1, ('G',): 1, ('E', '2', 'D'): 1, ('C', 'F', '2'): 1, ('B', '1', 'E'): 1, ('C', '0', 'G'): 1, ('1',): 1, ('G', '1', '2'): 1, ('3',): 1, ('F', '0', '1'): 1, ('D', '4', '3'): 1, ('0', 'a'): 1, ('B',): 2, ('D',): 1, ('4', 'd'): 1, ('A', 'C', 'D'): 2, ('F',): 1}
		return True

	def update_test(self):
		"""
		Test the function HATs.update()
		"""
		alignment = '0-0 1-1 2-2 4-3 3-4'
		sentence = 'a b c d e'
		labels = dict(zip([(i,i+1) for i in xrange(5)] + [(0,5),(1,5),(0,3),(3,5),(2,5),(0,2),(1,3)],['0','1','2','4','3','A','B','C','D','E','F','G']))
		a = Alignments(alignment,sentence)
		HAT_dict = a.HAT_dict(labels)
		h = HATGrammar(HAT_dict, 'A')
		grammar = {}
		grammar = h.update_weights(grammar)
		man_grammar = {'A': {('F', 'E'): 0.2, ('C', 'D'): 0.4, ('0', 'B'): 0.4}, 'C': {('F', '2'): 0.2, ('0', 'G'): 0.2}, 'B': {('G', 'D'): 0.2, ('1', 'E'): 0.2}, 'E': {('2', 'D'): 0.4}, 'D': {('4', '3'): 1.0}, 'G': {('1', '2'): 0.4}, 'F': {('0', '1'): 0.4}, '1': {('b',): 1.0}, '0': {('a',): 1.0}, '3': {('e',): 1.0}, '2': {('c',): 1.0}, '4': {('d',): 1.0}}
		assert grammar == man_grammar
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
		HAT_dict = a.HAT_dict(labels)
		h = HATGrammar(HAT_dict, 'A')
		grammar = {}
		grammar = h.update_weights(grammar, pcfg_dict)
		assert grammar == {'A': {('F', 'E'): 0.0320855614973262, ('C', 'D'): 0.2994652406417112, ('0', 'B'): 0.6684491978609625}, 'C': {('F', '2'): 0.1711229946524064, ('0', 'G'): 0.1283422459893048}, 'B': {('G', 'D'): 0.641711229946524, ('1', 'E'): 0.026737967914438495}, 'E': {('2', 'D'): 0.05882352941176469}, 'D': {('4', '3'): 0.9999999999999999}, 'G': {('1', '2'): 0.7700534759358287}, 'F': {('0', '1'): 0.2032085561497326}, '1': {('b',): 0.9999999999999999}, '0': {('a',): 0.9999999999999999}, '3': {('e',): 0.9999999999999999}, '2': {('c',): 0.9999999999999999}, '4': {('d',): 0.9999999999999999}}
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
		a = Alignments(alignment, sentence)
		HAT_dict = a.HAT_dict(labels)
		pcfg_dict = {'iobj-h+det': {('iobj-h', 'det'): 0.333}, 'iobj-h+dobj': {('iobj-h', 'dobj'): 0.11904761904761904, ('iobj-h+det', 'dobj-h'): 0.11904761904761904}, 'iobj+det': {('iobj', 'det'): 0.11904761904761904, ('det', 'iobj-h+det'): 0.11904761904761904}, 'ROOT/dobj-h': {('ROOT/dobj', 'det'): 0.11904761904761904, ('nsubj+root', 'iobj+det'): 0.047619047619047616, ('nsubj+root+det', 'iobj-h+det'): 0.047619047619047616, ('nsubj', 'root+iobj+det'): 0.11904761904761904}, 'det': {('the',): 1.0000000000000004, ('some',): 1.0000000000000002}, 'nsubj': {('I',): 1.0}, 'nsubj\\ROOT': {('root', 'iobj+dobj'): 0.11904761904761904, ('root+det', 'iobj-h+dobj'): 0.047619047619047616, ('root+iobj', 'dobj'): 0.047619047619047616, ('root+iobj+det', 'dobj-h'): 0.11904761904761904}, 'dobj': {('det', 'dobj-h'): 0.3333333333333333}, 'ROOT/dobj': {('nsubj+root', 'iobj'): 0.047619047619047616, ('nsubj+root+det', 'iobj-h'): 0.09523809523809523, ('nsubj', 'root+iobj'): 0.09523809523809523}, 'ROOT': {('nsubj+root+det', 'iobj-h+dobj'): 0.09523809523809523, ('nsubj', 'nsubj\\ROOT'): 0.33, ('nsubj+root', 'iobj+dobj'): 0.11904761904761904, ('ROOT/dobj-h', 'dobj-h'): 0.33, ('ROOT/dobj', 'dobj'): 0.11904761904761904}, 'dobj-h': {('flowers',): 1.0}, 'nsubj+root+det': {('nsubj+root', 'det'): 0.11904761904761904, ('nsubj', 'root+det'): 0.11904761904761904}, 'root': {('give',): 1.0000000000000002}, 'iobj+dobj': {('det', 'iobj-h+dobj'): 0.09523809523809523, ('iobj+det', 'dobj-h'): 0.09523809523809523, ('iobj', 'dobj'): 0.047619047619047616}, 'root+iobj': {('root+det', 'iobj-h'): 0.11904761904761904, ('root', 'iobj'): 0.11904761904761904}, 'root+iobj+det': {('root', 'iobj+det'): 0.09523809523809523, ('root+det', 'iobj-h+det'): 0.047619047619047616, ('root+iobj', 'det'): 0.09523809523809523}, 'iobj': {('det', 'iobj-h'): 0.33}, 'root+det': {('root', 'det'): 0.33}, 'iobj-h': {('boy',): 1.0}, 'nsubj+root': {('nsubj', 'root'): 0.33} }
		h = HATGrammar(HAT_dict, 'ROOT-[0-6]')
		grammar = {}
		grammar = h.update_weights(grammar, pcfg_dict)
#		for lhs in counts:
#			for rhs in counts[lhs]:
#				print '%s --> %s\t%f' % (lhs, ' '.join(rhs), counts[lhs][rhs])
		return True
	


	def test_all(self):
		return self.probs_test() and self.update_test() and self.update_test2() and self.grammar_test()


if __name__ == "__main__":
	x = HATsTests()
	print x.test_all()
