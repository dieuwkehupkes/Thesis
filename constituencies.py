import re

class Constituencies():
	"""
	A class representing a constuency tree from a sentence.
	Object is a flat object, is mainly used to view the
	hierarchical structure of a sentence via labels
	"""
	def __init__(self, treestring, sentence= False):
		"""
		Initialise with a string representation of a constituency tree
		The Constituency object is a 
		"""
		self.tree = self.tree_repr(treestring)
		self.treestring = treestring
		self.sentence = sentence
		self.labels = {}
		
	def reconstruct_sentence(self):
		if self.sentence:
			return sentence
		else:
			lexicals = re.findall('\([^\(\)]*\)',self.treestring)
			words = []
			for l in lexicals:
				lex_item = re.search('(?<= ).*?(?=\))',l).group(0)
				words.append(lex_item)
			return ' '.join(words)
	
	def tree_repr(self, string_tree):
		tree_repr = []
		if '(' not in string_tree:
			tree_repr = string_tree.strip()
		else:
			tag = re.search('(?<=\().*?(?= \()',string_tree)
			if tag:
				tree_repr.append(tag.group(0))
			for child in self.children(string_tree):
				tree_repr.append(self.tree_repr(child))
		return tree_repr
	
	def children(self,string_tree):
		"""
		Find children of the inputted string
		"""
		children = []
		if len(re.findall('\(',string_tree)) == 1:
			# no nested children present
			tag = re.search('(?<=\().* ', string_tree).group(0)
			children.append(tag)
			lex_item = re.search('(?<= ).*(?=\))', string_tree).group(0)
			children.append(lex_item)
		else:
			#find all children
			child, brackets, record = '', 0, False
			for symbol in string_tree[1:]:
				if symbol == '(':
					brackets += 1
					record = True
				elif symbol == ')':
					brackets -= 1
				if record == True:
					child += symbol
				if child and brackets == 0:
					children.append(child)
					child = ''
					record = False
		return children

	def find_label(self,tree,startpos):
		"""
		Compute the word span of a tree, and assign
		a label to it in a dictionary
		"""
		if not isinstance(tree,list):
			raise ValueError("Input is no tree represented as a list")
		label = tree[0]
		if isinstance(tree[1],str):
			span = (startpos,startpos+1)
		else:
			children = tree[1:]
			span_cur = self.find_label(tree[1],startpos)
			for i in xrange(1,len(children)):
				span_cur = self.find_label(tree[1+i],span_cur[1])
			span = (startpos,span_cur[1])
		self.labels[span] = label
		return span
	
	def find_labels(self):
		"""
		Compute the labels for the wordspans, that together
		represent the hierarchial constituency structure
		of the sentence.
		Return the dictionary
		"""
		self.find_label(self.tree,0)
		return self.labels


def test():
	tree = '(ROOT (NP (NP (NN resumption)) (PP (IN of) (NP (DT the) (NN session)))))'
	x = Constituencies(tree)
	print x.find_labels()
#	print x.tree
	

test()
