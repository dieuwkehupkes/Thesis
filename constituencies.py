import re
import nltk.tree

class ConstituencyTree():
	"""
	A class representing a constuency tree from a sentence.
	Object is a flat object, is mainly used to view the
	hierarchical structure of a sentence via labels
	"""
	def __init__(self, tree, sentence= False):
		"""
		Initialise with a string representation of a constituency tree. 
		Transform to a nested list representation of the tree.
		"""
		if isinstance(tree, nltk.Tree):
			self.tree = tree
		else:
			self.tree = nltk.Tree(tree)
		self.sentence = sentence
		self.labels = {}
	
	def reconstruct_sentence(self):
		if self.sentence:
			return sentence
		else:
			return ' '.join(self.tree.leaves())
	
	def root_span(self,subtree,startpos):
		"""
		Recursively compute the span a node covers
		"""
		cur_startpos = startpos
		for child in subtree:
			if isinstance(child,str):
				span = (cur_startpos,cur_startpos+1)
			else:
				span = self.root_span(child,cur_startpos)
			cur_startpos = span[1]
		root_span = (startpos, span[1])
		return root_span

	def nr_of_nonterminals(self):
		"""
		Return the number of nonterminals in the tree
		"""
		return len(self.tree.treepositions()) - len(self.tree.leaves())

	def phrases_consistent(self, subtree, startpos, phrase_list):
		"""
		Return the number of non-terminal nodes in the tree
		that occur in the provided list of phrases.
		"""
		nr_consistent = 0
		#Add one if rootnode is in phraselist
		if self.root_span(subtree,startpos) in phrase_list:
			nr_consistent+=1
		cur_startpos = startpos
		for child in subtree:
			if isinstance(child,str):
				cur_startpos += 1
			else:
				nr_consistent += self.phrases_consistent(child, cur_startpos, phrase_list)
				cur_startpos = self.root_span(child,cur_startpos)[1]
		return nr_consistent
	
	def branching_factor(self,branching_dict = {}):
		"""
		Return a dictionary that summaries the different 
		branching factors of the trees. If initialised with
		a dictionary, update this dictionary with the
		valeus of the current tree.
		"""
		b_factor = len(self.tree)
		if b_factor == 1 or b_factor ==0:
			if isinstance(self.tree,str) or len(self.tree) ==0 or isinstance(self.tree[0],str):
				#instance is a terminal or a pre terminal
				return branching_dict
			else:
				#instance is a higher node in the tree that expands unary
				print self.tree
				branching_dict[1] = branching_dict.get(1,0)+1
				return ConstituencyTree(self.tree[0]).branching_factor(branching_dict)
		else:
			#update dict with branching factor
			branching_dict[b_factor] = branching_dict.get(b_factor, 0) +1
			#update dictionary with branching factor of all the children
			for child in self.tree:
				if isinstance(child,str):
					return branching_dict
				else:
					branching_dict = ConstituencyTree(child).branching_factor(branching_dict)
		return branching_dict
