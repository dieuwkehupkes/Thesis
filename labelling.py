import copy
import re

class Labels():
	"""
	Class to create different kinds of labels from a set
	of basic labels
	"""
	def __init__(self,labels):
		"""
		Initialise with a dictionary with basic labels
		"""
		self.labels = labels

	def label_most(self):
		"""
		Try to label all spans... explain how
		"""
		#create SAMT labels
		SAMT = self.SAMT_labels()
		labels = self.minus_left_and_right(SAMT)
		labels = self.minus_concat(SAMT)
		return labels
		

	def SAMT_labels(self):
		"""
		Return SAMT labels based on labels basic
		"""
		labels = copy.deepcopy(self.labels)
# 		#find 2 concatenated labels
		labels = self.concatenated2(labels)
#		#find 'minus'-labels
		labels = self.minus1(labels)
#		#find 3 concatenated labels
		labels = self.concatenated3(labels)
#		print labels
		return labels		

		concat2 = self.concatenated2()
		minus1 = self.minus1()
		concat3 = self.concatenated3()
		# create a dictionary that has all labels in it
		# in the correct presedence order
		labels = concat3
		labels.update(minus1)
		labels.update(concat2)
		labels.update(self.labels)		
  		return labels
			
	
	def concatenated2(self, o = {}, i = None):
 		"""
 		Return all labels that can be made of the concatenation
 		of self.labels.
 		"""
 		i = i or self.labels
 		concat_list = [(span1,span2) for span1 in i for span2 in i if span1[1] == span2[0]]
   		for span in concat_list:
  			new_label = '%s+%s' % (i[span[0]], i[span[1]])
  			new_span = (span[0][0],span[1][1])
  			o[new_span] = o.get(new_span,new_label)
  		return o
 	
 	def concatenated3(self, o = {}, i = None):
 		"""
 		Update a dictionary labels_o with labels that are a
 		concatenation of three labels of the inputted set of
 		labels, labels_i.
 		"""
 		i = i or self.labels
 		concat_list = [(span1,span2,span3) for span1 in i for span2 in i for span3 in i if span1[1]==span2[0] and span2[1] == span3[0]]
 		for span in concat_list:
 			new_label = '%s+%s+%s' % (i[span[0]],i[span[1]],i[span[2]])
 			new_span = (span[0][0],span[2][1])
 			o[new_span] = o.get(new_span,new_label)
 		return o
 	
 	def minus1(self, o = {}, i = None):
 		"""
 		update a dictionary labels_o with labels that are
 		of the form A\B, or B/A, that refer to a sequence labelled
 		B missing A on the left of right, respectively, 
 		where A and B in the inputted set labels_i. 
 		"""
 		i = i or self.labels
 		minus_list = [(span1,span2) for span1 in i for span2 in i if (span1[0] == span2[0] or span1[1] == span2[1]) and span1 != span2]
 		for span in minus_list:
 			L0,L1 = i[span[0]], i[span[1]]
 			s00,s01,s10,s11 = span[0][0], span[0][1],span[1][0],span[1][1]
			if s01 == s11 and s00 < s10:
				new_span, new_label = (s00,s10), '%s/%s' % (L0, L1)
				o[new_span] = o.get(new_span,new_label)
			elif s00 == s10 and s01 < s11:
				new_span, new_label = (s01,s11), '%s\%s' % (L0, L1)
				o[new_span] = o.get(new_span,new_label)
		return o
 
 	def minus_left_and_right(self, o = {}, i = None):
 		"""
 		Update a dictionary labels_o with labels that are of the
 		form A\B/C, that refer to a sequence labelled B missing an
 		A on the left and a C on the right, where A,B and C are labels
 		in the inputted set labels_i.
 		"""
 		i = i or self.labels
 		spanlist = [(span0,span1,span2) for span0 in i for span1 in i for span2 in i if span0[0] == span2[0] and span1[1] == span2[1] and span0[1] < span1[0]]
 		for span in spanlist:
 			L0,L1,L2 = i[span[0]], i[span[1]], i[span[2]]
			new_span = (span[0][1],span[1][0])
			new_label = '%s\%s/%s' % (L0,L2,L1)
			o[new_span] = o.get(new_span,new_label)
		return o
	
	def minus_concat(self, o = {}, i = None):
		"""
		Update a dictionary o with the labels of the
		form A+B\C and C/A+B, where A, B and C are in i.
		"""
 		i = i or self.labels
 		#make a copy of the input labels to create concatenated labels
 		plain = copy.deepcopy(self.labels)
		concat = self.concatenated2(plain,i)
		#create minus labels with concatenated labels
		labels = self.minus1(o,concat)
		#filter out labels that have a concatenated main label
		l = labels.keys()
		for key in l:
			if re.search('.*\+.*/', labels[key]):
				del labels[key]
			elif re.search("\\\\.*\+.*",labels[key]):
				del labels[key]
		return labels
		
		
		
	
if __name__ == "__main__":
	l = Labels({(1, 2): 'root', (0, 1): 'nsubj', (6, 7): 'PUNCT', (4, 6): 'dobj', (5, 6): 'dobj-h', (0, 6): 'ROOT', (2, 3): 'det', (4, 5): 'det', (3, 4): 'iobj-h', (2, 4): 'iobj'})
	print l.label_all()
