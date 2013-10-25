from labelling import *

class LabelsTests():
	"""
	Class to test functionality of the class Labels
	"""
	def test_all(self):
		return self.concat_test() and self.minus_test() and self.minus_double_test() and self.SAMT_test()
	
	def base_test(self):
		labels = dict(zip([(i,i+1) for i in xrange(11)] + [(0,6),(6,8),(8,11),(6,11),(0,11)],['a','b','c','d','e','f','g','h','i','j','k','A','B','C','D','E']))
		return Labels(labels)
		
	def concat_test(self):
		"""
		Test Labels.concat for different depths.
		"""
		l = self.base_test()
		labels = copy.deepcopy(l.labels)
		c1 = l.concat(1)
		assert c1 == labels, 'concat(1) does not produce correct output'
		c2 = l.concat(2)
		labels.update(dict(zip([(i,i+2) for i in xrange(6)] + [(7,9),(8,10),(9,11),(0,7),(5,8),(6,9),(7,11),(5,11),(0,8)],['a+b','b+c','c+d','d+e','e+f','f+g','h+i','i+j','j+k','A+g','f+B','B+i','h+C','f+D','A+B'])))
		assert c2 == labels, 'concat(2) does not produce correct output'
		c3 = l.concat(3)
		labels.update(dict(zip([(i,i+3) for i in xrange(5)] + [(7,10),(0,9),(4,8),(5,9),(6,10),(4,11)],['a+b+c','b+c+d','c+d+e','d+e+f','e+f+g','h+i+j','A+B+i','e+f+B','f+B+i','B+i+j','e+f+D'])))
		assert c3 == labels, 'concat(3) does not produce correct output'
		c4 = l.concat(4)
		labels.update(dict(zip([(i,i+4) for i in xrange(4)]+[(3,8),(4,9),(5,10),(3,11),(0,10)],['a+b+c+d','b+c+d+e','c+d+e+f','d+e+f+g','d+e+f+B','e+f+B+i','f+B+i+j','d+e+f+D','A+B+i+j'])))
		assert c4 == labels, 'concat(4) does not produce correct output'
		c5 = l.concat(5)
		labels.update(dict(zip([(0,5),(1,6),(2,7),(2,8),(3,9),(4,10),(2,11)],['a+b+c+d+e','b+c+d+e+f','c+d+e+f+g','c+d+e+f+B','d+e+f+B+i','e+f+B+i+j','c+d+e+f+D'])))
		assert c5 == labels, 'concat(5) does not produce correct output'
		c6 = l.concat(6)
		labels.update(dict(zip([(1,7),(1,8),(1,11),(2,9),(3,10)],['b+c+d+e+f+g','b+c+d+e+f+B','b+c+d+e+f+D','c+d+e+f+B+i','d+e+f+B+i+j'])))
		assert c6 == labels, 'concat(6) does not produce correct output'
		c7 = l.concat(7)
		labels.update({(1,9):'b+c+d+e+f+B+i',(2,10): 'c+d+e+f+B+i+j'})
		assert c7 == labels, 'concat(7) does not produce correct output'
		c8 = l.concat(8)
		labels.update({(1,10):'b+c+d+e+f+B+i+j'})
		assert labels == c8, 'concat(8) does not produce correct output'
		c9 = l.concat(9)
		assert labels == c9
		return True

	def minus_test(self):
		"""
		Test Labels.minus for different depths
		"""
		l = self.base_test()
		labels = copy.deepcopy(l.labels)
		m0 = l.minus(0)
		assert m0 == labels, 'minus(0) does not produce correct output'
		m1 = l.minus(1)
		labels.update(dict(zip([(0,5),(1,6),(8,10),(9,11),(7,11),(6,10),(1,11),(0,10),(0,8)],['A/f','a\A','C/k','i\C','g\D','D/k','a\E','E/k','E/C'])))
		assert m1 == labels, 'minus(1) does not produce correct output'
		m2 = l.minus(2)
		labels.update(dict(zip([(2,6),(0,4),(6,9),(0,7),(2,11),(0,9)],['a+b\A','A/e+f','D/j+k','E/h+C','a+b\E','E/j+k'])))
		assert m2 == labels, 'minus(2) does not produce correct output'
		m3 = l.minus(3)
		labels.update(dict(zip([(3,6),(0,3),(3,11)],['a+b+c\A', 'A/d+e+f','a+b+c\E'])))
		assert m3 == labels, 'minus(3) does not produce correct output'
		m4 = l.minus(4)
		labels.update({(4,6):'a+b+c+d\A',(0,2):'A/c+d+e+f',(4,11):'a+b+c+d\E'})
		assert m4 == labels, 'minus(4) does not produce correct output'
		m5 = l.minus(5)
		labels.update({(5,11):'a+b+c+d+e\E'})
		assert m5 == labels, 'minus(5) does not produce correct output'
		m6 = l.minus(6)
		assert m6 == labels, 'minus(6) does not produce correct output'		
		return True
	
	def minus_double_test(self):
		"""
		Test Labels.minus_double for different depths
		"""
		l = self.base_test()
		labels = copy.deepcopy(l.labels)
		m0 = l.minus_double(0)
		assert m0 == labels, 'minus_double(0) does not produce correct output'
		m1 = l.minus_double(2)
		labels.update(dict(zip([(1,5),(1,10),(1,8),(7,10),(6,10),(1,6),(8,10)],['a\A/f','a\E/k','a\E/C','g\D/k','A\E/k','a\E/D','B\D/k'])))
		assert m1 == labels, 'minus_double(2) does not produce correct output'
		m3 = l.minus_double(3)
		labels.update(dict(zip([(2,10), (6, 9), (2, 6), (2, 8), (1, 4), (1, 9), (1, 7), (2, 5), (7, 9)],['a+b\E/k','A\E/j+k','a+b\E/D','a+b\E/C','a\A/e+f','a\E/j+k','a\E/h+C','a+b\A/f','g\D/j+k'])))
		assert m3 == labels, 'minus_double(3) does not produce correct output'
		return True
	
	def SAMT_test(self):
		"""
		Test Labels.SAMT
		"""
		l = self.base_test()
		SAMT = l.SAMT_labels()
		labels = dict(zip([(i,i+1) for i in xrange(11)] + [(0,6),(6,8),(8,11),(6,11),(0,11)],['a','b','c','d','e','f','g','h','i','j','k','A','B','C','D','E']))
		labels.update(dict(zip([(i,i+2) for i in xrange(6)] + [(7,9),(8,10),(9,11),(0,7),(5,8),(6,9),(7,11),(5,11),(0,8)],['a+b','b+c','c+d','d+e','e+f','f+g','h+i','i+j','j+k','A+g','f+B','B+i','h+C','f+D','A+B'])))
		labels.update(dict(zip([(0,5),(1,6),(6,10),(1,11),(0,10)],['A/f','a\A','D/k','a\E','E/k'])))
		labels.update(dict(zip([(i,i+3) for i in xrange(5)] + [(7,10),(0,9),(4,8),(5,9),(4,11)],['a+b+c','b+c+d','c+d+e','d+e+f','e+f+g','h+i+j','A+B+i','e+f+B','f+B+i','e+f+D'])))
		assert labels == SAMT, 'SAMT function does not produce correct output'
		return True				
	
	def label_all_test(self):
		"""
		Test Labels.label_most()
		"""
		l = self.base_test()
		labels = l.label_most()
		return True
			
if __name__ == "__main__":
	x = LabelsTests()
#	x.label_all_test()
	print x.test_all()
