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
				span = (startpos,startpos+1)
			else:
				span = self.root_span(child,cur_startpos)
			cur_startpos = span[1]
		return (startpos, span[1])

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

