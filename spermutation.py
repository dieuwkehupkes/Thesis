class SetPermutation:
	"""
	A class representing set-permutations. Methods are
	provided for computing all phrases allowed according
	to the permutation
	"""
	def __init__(self,alignment):
		"""
		Represent the alignment as a set
		"""
		self.alignment = self.make_set(alignment)
		phrase_pairs = self.compute_phrasepairs()
		print phrase_pairs

	def make_set(self,alignment):
		"""
		Return a set with all alignment links,
		and keep track of the length of source
		and target language
		"""
		links = alignment.split()
		lengthS = 0
		lengthT = 0
		pos = 0
		for link in links:
			link_list = link.split('-')
			source_pos, target_pos = int(link_list[0]), int(link_list[1])
			if source_pos > lengthS:
				lengthS = source_pos
			if target_pos > lengthT:
				lengthT = target_pos
			links[pos] = (source_pos,target_pos)
			pos += 1
		self.lengthS = lengthS
		self.lengthT = lengthT
		return links

	def compute_phrasepairs(self):
		phrase_pairs = []
		F_links = self.links_fromF()
		E_links = self.links_fromE()
		#Use a shift reduce algorithm to find phrase pairs
		loopList = [0]
		for y in xrange(1,self.lengthS+1):
			loopList.append(y)
			#print loopList
			for x in reversed(loopList):
				u_xy = self.maxspan((x,y))
				#print 'u',str((x,y)), '= ', u_xy
				l_xy = self.minspan((x,y))
				#print 'l',str((x,y)), '= ', l_xy
				f_xy = (F_links[u_xy] - F_links[l_xy-1]) - (E_links[y] - E_links[x-1])
				#print "f",x,y, "=", f_xy
				if f_xy == 0:
					phrase_pairs.append((x+1,y+1))
					for number in xrange(x+1,y+1):
				#		print number
						if number in loopList:
							loopList.remove(number)
		return phrase_pairs
					
	def links_fromE(self):
		"""
		Precompute values for the function
		E_c(j) = |{(i',j')\in A | j' =< j}|
		
		"""
		E_links = {}
		E_links[-1] = 0
		E_links[0] = len([(i,j) for (i,j) in self.alignment if i == 0])
		for position in xrange(1,self.lengthS+1):
			links_from_position = len([(i,j) for (i,j) in self.alignment if i == position])
			E_links[position] = E_links[position-1] + links_from_position
		return E_links

	def links_fromF(self):
		"""
		Precompute values for the function
		F_c(j) = |{(i',j')\in A | i' =< i}|
		"""
		F_links = {}
		F_links[-1] = 0
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
		return min([j for (i,j) in self.alignment if (i >= x and  i <= y)])

	def maxspan(self,(x,y)):
		"""
		Returns the maximum position on the target side
		that are linked to positions [x,y]
		"""
		return max([j for (i,j) in self.alignment if (i >= x and  i <= y)])

	def minspant(self,(x,y),(u,v)):
		"""
		Compute the value of
		l(x,y) = min{j | (i,j)\in A, i\in [x,y]} from the value
		previously computed values for l(x,y)
		"""
		if not (y == v and u > x):
			raise ValueError("span "+str([x,y])+"can not be computed from "+str([u,v]))
			
		
	def is_phrasepair(span):
		"""
		Given a span [i,j] with i the left most
		element of the span and j the right most,
		check if [i,j] is a valid phrase pair
		"""
		#check if the input has the correct form
		if not isinstance(x,list):
			raise TypeError("Input span is not a list")
		elif not len(x) == 2:
			raise ValueError("Input span should be a list containing two elements")
		phrasepair_test = 1


def test():
	alignment = '0-5 1-4 1-6 2-3 3-0 3-2 4-1 5-0 5-2'
	s = SetPermutation(alignment)
		
