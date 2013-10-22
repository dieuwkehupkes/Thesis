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
		assert spanlist == spanlist_man, "Alignments.spans is not functioning as it should'"
		return True

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
		assert spanlist == spanlist_man, "Alignments.spans is not functioning as it should. Error when generating spans for monotone one-to-one alignment."
		return True


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
		assert spanlist == spanlist_man, "Alignments.spans is not functioning as it should. Error when generating spans for monotone one-to-one alignment with unaligned words"
		return True
	
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
		assert spanlist == spanlist_man, "Alignments.spans is not functioning as it should. Error when generating spans for many-to-many alignment with unaligned words"
		return True

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
		assert score == 1, "Alignment.agreement is not functioning as it should"
		return True
	
	def consistency_test2(self):
		tree = nltk.Tree('(ROOT (NP (NP (NN approval)) (PP (IN of) (NP (DT the) (NNS minutes))) (PP (IN of) (NP (DT the) (JJ previous) (NN sitting)))))')
		sentence = 'approval of the minutes of the previous sitting'
		alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		a = Alignments(alignment,sentence)
		score = a.agreement(tree)
		assert score == 0.8, "Alignment.agreement is not functioning as it should"
		return True
		
	def consistency_test3(self):
		tree = nltk.Tree('(ROOT ( NP ( NP (NN approval )) (PP of the minutes) (PP (IN of) (NP (DT the ) (JJ previous ) (NN sitting ) ))))')
		sentence = 'approval of the minutes of the previous sitting'
		alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		a = Alignments(alignment,sentence)
		score = a.agreement(tree)
		assert score == 1, "Alignment.agreement is not functioning as it should"
		return True
	
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
	
	def alignment_test_all(self):
		return self.spans_test_all() and self.consistency_test1() and self.consistency_test2() and self.consistency_test3() and self.dict_test()
	
if __name__ == "__main__":
	x = AlignmentsTests()
	print x.alignment_test_all()
