import copy
import re

class Labels():
	"""
	Class to create different kinds of labels from a set
	of basic labels. Currently, some set of labels are
	computed multiple times to be used in the computation
	of other labels. Class can be made more efficient by storing
	such sets of labels as attributes of the Labels instance.
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
		# find the largest spans to determine which spans should be labelled
		# assume the
		s_max = max([x[1] for x in self.labels.keys()])
		s_min = min([x[0] for x in self.labels.keys()])		
#		#create SAMT labels
		labels = self.SAMT_labels()
		#update with minus labels with 3 variables
		self.minus(2,labels)
		#update with double minus labels with 3 variables
		variables = 3
		self.minus_double(2,labels)
		#Add labels of higher depth until dictionary does not grow anymore
		cur_depth = 4
		old_labels = {}
		while len(old_labels) < len(labels):
			old_labels = copy.deepcopy(labels)
			self.concat(cur_depth,labels)
			self.minus(cur_depth-1,labels)
			self.minus_double(cur_depth-1,labels)
			cur_depth += 1
		return labels		

	def SAMT_labels(self):
		#change this
		"""
		Return SAMT labels based on labels basic
		"""
		labels = copy.deepcopy(self.labels)
 		#update with concat2 labels
		self.concat(2,labels)
		#update with 'minus'-labels
		self.minus(1,labels)
		#update with concat3 labels
		self.concat(3,labels)
		return labels		
			
	def concat(self, depth, o = {}, i = None):
		"""
		Compute all concatenated labels up to inputted depth,
		with basic labels i. Extend input dictionary o with
		the found labels for spans that did not yet exist in o.
		Return o, but also globally modify the dictionary.
		If no output dictionary is given, output all concatenated
		labels. If no input dictionary is given, use self.labels.
		"""
		assert depth >= 0, 'depth of input labels cannot be negative'
		i = i or self.labels
		if i ==0:
			return o
		o.update(i)
		#if depth is 1, return basic labels
		d = 2
		concat_cur = copy.deepcopy(i)
		while d <= depth:
			#Create new labels by combining current concatenated labels with basic labels
			concat_new = {}
			concat_list = [(span1,span2) for span1 in concat_cur for span2 in i if span1[1] == span2[0]]
			for span in concat_list:
				new_span = (span[0][0],span[1][1])
				new_label = '%s+%s' % (concat_cur[span[0]], i[span[1]])
				concat_new[new_span] = new_label
				o[new_span] = o.get(new_span,new_label)
			concat_cur = concat_new
			d += 1
		return o
 	
 	def minus(self, depth, o = {}, i = None):
 		#change this
 		"""
 		Return a dictionary with all labels of the form
 		A1 + A2 + ... An\B and B/A1 + A2 + ... An, where
 		A1, .. An and B in labels.self, or in i if a dictionary
 		is inputted, and n is no larger than depth
 		"""
 		i = i or self.labels
		o.update(i)
 		if depth == 0:
 			return o
 		labels = copy.deepcopy(self.labels)
 		concat = self.concat(depth, labels)
		minus_left = [(span1,span2) for span1 in concat for span2 in i if span1[0] == span2[0] and span1 < span2]
		for span in minus_left:
			new_span = (span[0][1], span[1][1])
#			print new_span
			new_label = '%s\%s' % (concat[span[0]], i[span[1]])
#			print new_label
			o[new_span] = o.get(new_span,new_label)
		minus_right = [(span1,span2) for span1 in i for span2 in concat if span1[1] == span2[1] and span1 < span2]
		for span in minus_right:
			new_span = (span[0][0],span[1][0])
			new_label = '%s/%s' % (i[span[0]], concat[span[1]])
			o[new_span] = o.get(new_span,new_label)
		return o
 	

	def minus_double(self, depth, o = {}, i = None):
		#change this
		"""
		Return a dictionary with all labels of the form
		A\B/C, where B is in self.labels or in i if i is provided,
		and A and C are in A1 + A2 + An where A1.. An are in
		self.labels or i and n <= depth.
		"""
		i = i or self.labels
		o.update(i)
		if depth == 0:
			return o
		concat = self.concat(depth, copy.deepcopy(self.labels))
		spanlist = [(span0,span1,span2) for span0 in concat for span1 in concat for span2 in i if span0[0] == span2[0] and span1[1] == span2[1] and span0[1] < span1[0]]
		for span in spanlist:
			new_span = (span[0][1],span[1][0])
			new_label = '%s\%s/%s' % (concat[span[0]], i[span[2]], concat[span[1]])
			#add new label if the added depth of the minus labels is no larger than depth
			if new_label.count('+') < depth-1:
				o[new_span] = o.get(new_span,new_label)
		return o
 
  	def annotate_span(self, labels):
 		"""
 		Annotate labels with their span, to make the
 		grammar unique.
 		"""
 		for key in labels:
 			span = "-[%s-%s]" % (key[0], key[1])
 			new_label = labels[key] + span
 			labels[key] = new_label
 		return labels
		
		
	
if __name__ == "__main__":
	l = Labels({(1, 2): 'root', (0, 1): 'nsubj', (6, 7): 'PUNCT', (4, 6): 'dobj', (5, 6): 'dobj-h', (0, 6): 'ROOT', (2, 3): 'det', (4, 5): 'det', (3, 4): 'iobj-h', (2, 4): 'iobj'})
#	print l.label_most()
