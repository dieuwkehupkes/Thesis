from alignments import *

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
		
if __name__ == "__main__":
	x = AlignmentsTests()
	print x.spans_test_all()
