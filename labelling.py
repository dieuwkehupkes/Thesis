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
		Create a labelling object, with basic labels.
		:param labels:	A dictionary assigning labels to spans
		"""
		self.labels = labels

	def concat(self, depth, o = {}, i = None):
		"""
		Compute all concatenated labels up to inputted depth,
		with basic labels i.
		If an output dictionary o is passed, extend this dictionary
		with the found spans that do not yet have a label in o.
		
		:param depth:	The maximum number of variables in the labels.
		:param o:	An output dictionary with already existing labels.
		:param i:	A dictionary with basic labels to be concatenated.
		"""
		assert depth >= 0, 'depth of input labels cannot be negative'
		i = i or self.labels
		if i ==0:
			return copy.deepcopy(o)
		output = copy.deepcopy(o)
		output.update(i)
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
				output[new_span] = output.get(new_span,new_label)
			concat_cur = concat_new
			d += 1
		return output

 	def minus(self, depth, o = {}, i = None):
 		"""
 		Compute all labels of the form A\B and B/A
 		where B is a basic label, and A a concatenated label that
 		contains no more than depth-1 variables.
 		If an output dictionary o is passed, extend this dictionary
		with the found spans that do not yet have a label in o.	
 		
 		:param depth: The maximum number of variables in the labels.
 		:param o:	An output dictionary that is to be updated with the new labels
 		:param i:	A dictionary with basic labels.
 		"""
 		i = i or self.labels
 		output = copy.deepcopy(o)
 		output.update(i)
 		if depth == 0:
 			return output
 		concat = self.concat(depth, i)
		minus_left = [(span1,span2) for span1 in concat for span2 in i if span1[0] == span2[0] and span1 < span2]
		for span in minus_left:
			new_span = (span[0][1], span[1][1])
#			print new_span
			new_label = '%s\%s' % (concat[span[0]], i[span[1]])
#			print new_label
			output[new_span] = output.get(new_span,new_label)
			if self.label_complexity(output[new_span]) > self.label_complexity(new_label):
				output[new_span] = new_label
		minus_right = [(span1,span2) for span1 in i for span2 in concat if span1[1] == span2[1] and span1 < span2]
		for span in minus_right:
			new_span = (span[0][0],span[1][0])
			new_label = '%s/%s' % (i[span[0]], concat[span[1]])
			output[new_span] = output.get(new_span,new_label)
			if self.label_complexity(output[new_span]) > self.label_complexity(new_label):
				output[new_span] = new_label
		return output

	def minus_double(self, depth, o = {}, i = None):
 		"""
 		Compute all labels of the form A\B/C, where 
 		A is a basic label, and B and C are concatenated
 		labels. The outputted labels have a number of variables
 		that is no higher than depth.
 		If an output dictionary o is passed, extend this dictionary
		with the found spans that do not yet have a label in o.	
 		
 		:param depth: The maximum number of variables in the labels.
 		:param o:	An output dictionary that is to be updated with the new labels
 		:param i:	A dictionary with basic labels.
 		
		Return a dictionary with all labels of the form
		, where B is in self.labels or in i if i is provided,
		and A and C are in A1 + A2 + An where A1.. An are in
		self.labels or i and n <= depth.
		"""
		assert depth >= 0, 'depth of input labels must be positive'
		i = i or self.labels
		output = copy.deepcopy(o)
		output.update(i)
		if depth == 0:
			return output
		concat = self.concat(depth, copy.deepcopy(self.labels))
		spanlist = [(span0,span1,span2) for span0 in concat for span1 in concat for span2 in i if span0[0] == span2[0] and span1[1] == span2[1] and span0[1] < span1[0]]
		for span in spanlist:
			new_span = (span[0][1],span[1][0])
			new_label = '%s\%s/%s' % (concat[span[0]], i[span[2]], concat[span[1]])
			#add new label if the added depth of the minus labels is no larger than depth
			if new_label.count('+') < depth-1:
				output[new_span] = output.get(new_span,new_label)
				if self.label_complexity(output[new_span]) > self.label_complexity(new_label):
					output[new_span] = new_label
		return output

	def SAMT_labels(self):
		"""
		Return all SAMT labels based on the basic
		labels of the object. The order if precedence is as follows:
 		
 		* Basic labels
 		
 		* labels A + B, where A and B are basic labels;
 		
 		* labels A/B or A\B where A and B are basic labels;
 		
 		* labels A + B + C where A,B and C are basic labels;
		"""
 		#update with concat2 labels
 		labels = self.concat(2,self.labels)
		#update with 'minus'-labels
		labels = self.minus(1,labels)
		#update with concat3 labels
		labels = self.concat(3,labels)
		#set SAMT labels as attribute
		self.SAMT = labels
		return labels	


	def label_most(self):
		"""
		Label all spans within the range of labels, following the following rules:
		
		* Labels with a lower depth are always preferred;
		
		* Concatenated labels are preferred over minus and double/minus labels;
		
		* Single minus labels (with concatenated spans) are preferred over double minus labels.
		
		SAMT labels thus have precedence over other labels.
		"""
		# find the largest spans to determine which spans should be labelled
		s_max = max([x[1] for x in self.labels.keys()])
		s_min = min([x[0] for x in self.labels.keys()])		
#		#create SAMT labels
		labels = self.SAMT_labels()
		#update with minus labels with 3 variables
		labels = self.minus(2,labels)
		#update with double minus labels with 3 variables
		labels = self.minus_double(2,labels)
		#Add labels of higher depth until dictionary does not grow anymore
		cur_depth = 4
		old_labels = {}
		while len(old_labels) < len(labels):
			old_labels = copy.deepcopy(labels)
			labels = self.concat(cur_depth,labels)
			labels = self.minus(cur_depth-1,labels)
			labels = self.minus_double(cur_depth-1,labels)
			cur_depth += 1
		return labels		

	
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
	
	def label_complexity(self,label):
		"""
		Return the number of variables in a label.
		"""
		return len(re.split('\\\\|/|\+',label))

		
####################################################################################
#DEMONSTRATION
####################################################################################


def demo():
	i = raw_input("Press enter to go through demo, q can be pressed at any stage to quit the demo.\t")
	if (i == 'q' or i == 'Q'): return
	
	print '\nInitialise a Labelling object with a set of basic Labels: (the example labels are abstracted from the dependency parse for the sentence I give the boy some flowers).'
	if (raw_input("") == 'q' or i == 'Q'): return
	print ">>> l = Labels({(1, 2): 'root', (0, 1): 'nsubj', (4, 6): 'dobj', (5, 6): 'dobj-h', (0, 6): 'ROOT', (2, 3): 'det', (4, 5): 'det', (3, 4): 'iobj-h', (2, 4): 'iobj'}"
	l = Labels({(1, 2): 'root', (0, 1): 'nsubj', (4, 6): 'dobj', (5, 6): 'dobj-h', (0, 6): 'ROOT', (2, 3): 'det', (4, 5): 'det', (3, 4): 'iobj-h', (2, 4): 'iobj'})	
	
	if (raw_input("") == 'q' or i == 'Q'): return

	print '\nCompute all concatenated labels up to depth 2:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.concat(2)'
	print l.concat(2)

	if (raw_input("") == 'q' or i == 'Q'): return
	print 'Compute all concatenated labels up to depth 3:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.concat(3)'
	print l.concat(3)

	if (raw_input("") == 'q' or i == 'Q'): return
	print '\nCompute all minus labels up to depth 2:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.minus(2)'
	print l.minus(2)	

	if (raw_input("") == 'q' or i == 'Q'): return
	print '\nExtend concat(2) with all minus labels:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.minus(2, l.concat(2))'
	print l.minus(2, l.concat(2))	

	if (raw_input("") == 'q' or i == 'Q'): return
	print '\nCompute SAMT labels:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.SAMT_labels()'
	print l.SAMT_labels()

	if (raw_input("") == 'q' or i == 'Q'): return	
	print '\nAnnotate basic labels with their span:'
	if (raw_input("") == 'q' or i == 'Q'): return
	print '>>> l.annotate_span(l.labels)'
	print l.annotate_span(l.labels)
	
	
	if (raw_input("") == 'q' or i == 'Q'): return
	print "End of demonstration\n"
	return



if __name__ == "__main__":
	print "\nA demonstration showing how a ``Labels`` object can be created and how some of the class methods can be used.\n"
	demo()


	

	l = Labels({(1, 2): 'root', (0, 1): 'nsubj', (6, 7): 'PUNCT', (4, 6): 'dobj', (5, 6): 'dobj-h', (0, 6): 'ROOT', (2, 3): 'det', (4, 5): 'det', (3, 4): 'iobj-h', (2, 4): 'iobj'})
#	print l.label_most()
