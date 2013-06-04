from graph_alignment import *

class Alignments:
	"""
	A class that represents alignments. A string that represents
	an alignment in the usual form is passed, during initialization
	the corresponding set representation is generated. Methods are
	provided for computing all allowed spans, and generating a CFG
	that uniquely generates all hierarchical alignment trees*.
	"""
	def __init__(self,alignment, sentence):
		"""
		Represent the alignment as a set. Input is a
		string representation of the alignment, like '0-1 2-1 ...'
		Counting starts from 0
		"""
		self.lengthS = len(sentence.split())	#maybe use tokenize for this
		self.alignment = self.make_set(alignment)
		self.sentence = sentence
		#make check for consistency sentence and alignment

	def make_set(self,alignment):
		"""
		Return a set with all alignment links,
		and keep track of the length of source
		and target language
		"""
		links = alignment.split()
		pos = 0
		lengthT = 0
		lengthS = 0
		for link in links:
			link_list = link.split('-')
			source_pos, target_pos = int(link_list[0]), int(link_list[1])
			links[pos] = (source_pos,target_pos)
			if target_pos > lengthT:
				lengthT = target_pos
			if source_pos > lengthS:
				lengthS = source_pos
			pos += 1
		lengthS = lengthS + 1
		self.lengthT = lengthT+1
		if lengthS > self.lengthS:
			print "Alignments has more words than sentence, skipped"
#			raise ValueError("Alignments has more words than sentence")
		elif lengthS < self.lengthS:
			print "Caution: sentence does not have the same length as alignment, are there", self.lengthS - lengthS, "unaligned words at the end of the sentence?"
		return set(links)

	def spans(self):
		"""
		Compute phrase pairs as. Could be more efficient
		by making use of previously computed values for
		functions. Basic idea taken from Chang & Gildea.
		Returns a generator with valid spans and partial
		sets.
		"""
		phrase_pairs = []
		F_links = self.links_fromF()
		E_links = self.links_fromE()
		#Use a shift reduce algorithm to find phrase pairs
		loopList = []
		for y in xrange(0,self.lengthS):
			loopList.append(y)
			for x in reversed(loopList):
				u_xy = self.maxspan((x,y))
				l_xy = self.minspan((x,y))
				f_xy = (F_links[u_xy] - F_links[l_xy-1]) - (E_links[y] - E_links[x-1])
				if f_xy == 0:
					yield (x,y+1)
					#for number in xrange(x+1,y):
					#	if number in loopList:
					#		loopList.remove(number)
				else:
					if self.partial_set((x,y),E_links):
						yield (x,y+1)

	def partial_set(self,(x,y),E_links):
		"""
		Compute if [x,y] is a partial set, which is true iff:
		- [x,y] is not a valid span;
		- there is at most one aligned word in [x,y]
		This function will not check if (x,y) is a valid span, as the function
		is only called from compute_spans if (x,y) is not a valid span.
		"""
		nr_aligned = 0
		for position in xrange(x,y+1):
			if E_links[position] - E_links[position-1] != 0:
				nr_aligned += 1
		if nr_aligned == 1:
			return True
		else:
			return False
			

	def links_fromE(self):
		"""
		Precompute values for the function
		E_c(j) = |{(i',j')\in A | j' =< j}|
		
		"""
		E_links = {}
		E_links[-1], E_links[-2] = 0, 0
		E_links[0] = len([(i,j) for (i,j) in self.alignment if i == 0])
		for position in xrange(1,self.lengthS):
			links_from_position = len([(i,j) for (i,j) in self.alignment if i == position])
			E_links[position] = E_links[position-1] + links_from_position
		return E_links

	def links_fromF(self):
		"""
		Precompute values for the function
		F_c(j) = |{(i',j')\in A | i' =< i}|
		"""
		F_links = {}
		F_links[-1], F_links[-2] = 0, 0
		F_links[0] = len([(i,j) for (i,j) in self.alignment if j == 0])
		for position in xrange(1,self.lengthT+1):
			links_from_position = len([(i,j) for (i,j) in self.alignment if j == position])
			F_links[position] = F_links[position-1] + links_from_position
		return F_links

	def minspan(self,(x,y)):
		"""
		Returns the minimum position on the target side
		that are linked to positions [x,y]
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return min(alignment_links)

	def maxspan(self,(x,y)):
		"""
		Returns the maximum position on the target side
		that are linked to positions [x,y]
		"""
		alignment_links = [j for (i,j) in self.alignment if (i >= x and  i <= y)]
		if alignment_links == []:
			return -1
		else:
			return max(alignment_links)


	def rules(self, span_relations):
		"""
		Creates a graph of all valid spans, and
		calculates all paths between span endpoints.

		A generator is returned for all the valid
		rules in the permutation.
		"""
		# Create nodes for all positions between words
		nodes = [Node(i) for i in xrange(0, self.lengthS + 1)]
		spans = []
		
		# Construct the graph by creating the edges
		print 'finding spans'
		for (i,j) in self.spans():
			nodes[i].link_to(nodes[j])
			spans.append((i,j))
		print 'finding rules'
		for (i,j) in spans:
			for path in nodes[i].paths_to(nodes[j]):
				if not path or len(path) == 2:
					# No rules possible, or path points to itself
					continue
			
				# Build up the rule as list of spans between
				# nodes.
				yield Rule((i, j), path,span_relations)


	def lexrules(self):
		"""
		Returns an iterator with the terminal rules
		of the grammar (i.e. that tells you the span
		corresponding to a word)
		"""
		from nltk import tokenize
		sent = self.sentence.split()	#maybe use the tokenize function for this
		length = len(sent)
		for i in xrange(0,len(sent)):
			rulestr = str(i) + "N" + str(i+1) + " -> '" + sent[i] + "' [1.0]"
			yield rulestr	

	def list_rules(self,spanrels):
		rules = []
		for rule in self.rules(spanrels):
			rules.append(str(rule))
		for rule in self.lexrules():
			rules.append(str(rule))
		return rules


"""
Testing functions for different kinds of alignments.
"""

def test():
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	sentence = 'My dog likes eating sausages'
	a1 = Alignments(alignment, sentence)
	#for span in a1.spans():
	#	print span
	therules = []
	for rule in a1.rules([]):
		therules.append(str(rule))
	rules_man = ['0N5 -> 0N1 1N5 [1]','0N5 -> 0N2 2N5 [1]', '0N5 -> 0N3 3N5 [1]', '0N5 -> 0N1 1N2 2N5 [1]', '0N5 -> 0N1 1N3 3N5 [1]', '0N5 -> 0N2 2N3 3N5 [1]', '0N5 -> 0N3 3N4 4N5 [1]', '0N5 -> 0N1 1N2 2N3 3N5 [1]', '0N5 -> 0N1 1N3 3N4 4N5 [1]', '0N5 -> 0N2 2N3 3N4 4N5 [1]', '0N5 -> 0N1 1N2 2N3 3N4 4N5 [1]', '1N5 -> 1N2 2N5 [1]', '1N5 -> 1N3 3N5 [1]', '1N5 -> 1N2 2N3 3N5 [1]', '1N5 -> 1N3 3N4 4N5 [1]', '1N5 -> 1N2 2N3 3N4 4N5 [1]', '2N5 -> 2N3 3N5 [1]', '2N5 -> 2N3 3N4 4N5 [1]', '0N3 -> 0N1 1N3 [1]', '0N3 -> 0N2 2N3 [1]', '0N3 -> 0N1 1N2 2N3 [1]', '0N2 -> 0N1 1N2 [1]', '1N3 -> 1N2 2N3 [1]', '3N5 -> 3N4 4N5 [1]']
	print "Rules found by program match manually found rules:", set(rules_man) == set(therules)

def test1():
	"""
	Test for a monotone alignment with no
	unaligned words
	"""
	alignment = '0-0 1-1 2-2 3-3 4-4'
	print 'alignment: ', alignment
	print "\nManually constructed span list:"	
	spanlist_man = [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]
	print spanlist_man
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	print "\nSpan list constructetd by program:"
	print spanlist
	print "\nEqual: ", spanlist == spanlist_man

def test2():
	"""
	Test for a no monotone many-to-many alignment,
	no unaligned words on source nor targetside.
	"""
	alignment = '0-5 1-4 1-6 2-3 3-0 3-2 4-1 5-0 5-2'
	print 'alignment: ', alignment
	print "\nManually constructed span list:"	
	spanlist_man = [(0,1), (0,2), (0,3), (1,2), (0,6), (2,3), (2,6), (3,4), (3,6), (4,5),(5,6)]
	spanlist_man.sort()
	print spanlist_man
	s = Alignments(alignment, '0 1 2 3 4 5')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	print "\nSpan list constructetd by program:"
	print spanlist
	print "\nEqual: ", spanlist == spanlist_man


def test3():
	"""
	Test for a one-to-one alignment with some
	unaligned words
	"""
	alignment = '1-1 2-2 4-4'
	print 'alignment:', alignment
	print "\nManually constructed span list:"	
	spanlist_man = [(0,1), (0,2), (0,3), (0,4), (0,5), (1,2), (1,3), (1,4), (1,5), (2,3), (2,4), (2,5), (3,4), (3,5), (4,5)]
	spanlist_man.sort()
	print spanlist_man
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	print "\nSpan list constructetd by program:"
	print spanlist
	print "\nEqual: ", spanlist == spanlist_man

	
def test4():
	"""
	Test for a no monotone many-to-many alignment,
	with aligned words on both and target side.
	"""
	alignment = '0-2 2-0 0-4 4-4 4-5'
	print 'alignment: ', alignment
	print "\nManually constructed span list:"	
	spanlist_man = [(0,1), (0,2), (0,5), (1,2), (1,3), (1,4), (2,3), (2,4), (3,4), (3,5), (4,5)]
	spanlist_man.sort()
	print spanlist_man
	s = Alignments(alignment, '0 1 2 3 4')
	spans = s.spans()
	spanlist = []	
	for span in spans:
		spanlist.append(span)
	spanlist.sort()
	print "\nSpan list constructed by program:"
	print spanlist
	print "\nEqual: ", spanlist == spanlist_man

