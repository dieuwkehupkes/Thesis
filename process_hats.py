import pickle
import nltk.grammar
import copy

class ProcessHATs():
	"""
	Class with functions that can be applied to a file
	containing pickled precomputed HATs.
	ProcessHATs has functional overlap with the class
	FileProcessing, but is more efficient as it avoids
	recomputing HATforests.
	"""
	def __init__(self,HATfile):
		"""
		Pass the name of the file containing the pickled
		HATs.
		"""
		self.HATfile = open(HATfile, 'r')
	
	def next(self):
		"""
		Return the next item in the file. If no 
		:return [sentence_nr, HATdict, root]
		"""
		try:
			#return sentence_nr, root, new_HAT
			return pickle.load(self.HATfile)
		except EOFError:
			return None
			
	def _reset_pointer(self):
		"""
		Reset the pointer of self.HATfile such that
		the next line to read is the first line.
		"""
		self.HATfile.seek(0)
	
	def normalise(self,rule_dict):
		"""
		Given a nested dictionary that represent rules as follows:
		{lhs : {rhs1 : count, rhs2: count ...}, ....}, return a
		similar nested dictionary with normalised counts
		"""
		normalised_dict = dict({})
		total_lhs = 0
		for lhs in rule_dict:
			normalised_dict[lhs] = {}
			total = 0
			#loop twice through dictionary
			#first to obtain total counts
			for rhs in rule_dict[lhs]:
				total += rule_dict[lhs][rhs]
			# then to adjuct the counts in the
			# new dictionary
			for rhs in rule_dict[lhs]:
				normalised_dict[lhs][rhs] = rule_dict[lhs][rhs]/float(total)
		return normalised_dict

	def unique_rules(self, stepsize):
		"""
		Go through HATcorpus and keep track of the
		percentage of the rules that is unique.
		Store the number of rules and the number of unique
		rules if the number of HATs processed % stepsize is 0
		"""
		unique_dict = {}
		unique_rules, unique_total = {}, 0
		all_rules, all_total = {}, 0
		sentences = 0
		self._reset_pointer()
		new = self.next()
		while new:
			H = HATGrammar(new[2],new[1])
			HATs = H.HATs
			sentences+= 1
			#go through lhs
			for lhs in HATs:
				lhs_plain = H.plain_label(lhs)
				unique_rules[lhs_plain], all_rules[lhs_plain] = set([]), {}
				for rhs in HATs[lhs]:
					rhs_plain = H.plain_label(rhs)
					if len(rhs) == 1:
						#don't take into account lexical rules
						continue
					print '%s --> %s' %(lhs_plain, rhs_plain)
					if rhs_plain in all_rules[lhs_plain]:
						"rule seen twice"
						#rule was seen already, increase counter
						all_rules[lhs_plain][rhs_plain] += 1
						all_total += 1
					elif rhs_plain in unique_rules[lhs_plain]:
						"rule seen once"
						# rule was seen one before, move from
						# unique-rules to all_rules, decrease counter
						# unique rules, add to all rules
						unique_total -= 1
						unique_rules[lhs_plain].remove(rhs_plain)
						all_rules[lhs_plain][rhs_plain] = 2
					else:
						#rule was not seen before, add to unique_rules
						unique_total += 1
						all_total +=1
						unique_rules[lhs_plain].add(rhs_plain)
			if sentences % stepsize == 0:
				update = [all_total, unique_total,float(unique_total)/all_total]
				unique_dict[sentences] = update
				print 'A%i\tAll: %i\tUnique: %i\tPercentage unique:%f' %(sentences, update[0], update[1], update[2])
			new = self.next()
		return unique_dict

	def em(self, max_iter):
		"""
		When passing a grammar represented by a dictionary,
		iteratively assign probabilities to all HATs of the
		corpus and recompute the counts of the grammar with
		relative frequency estimation until convergence or
		until a maximum number iterations is reached.
		Return the new grammar
		:param start_grammar	Grammar represented as a nested dictionary
		:param max_iter			Maximum number of iterations
		:param max_length		Maximum sentence length considered
		"""
		#Build in some method for measuring the change of two grammars
		print 'run EM with a maximum of %i iterations' %max_iter
		i = 1
		grammar = self.initialise_grammar()
		old_grammar = copy.deepcopy(grammar)
		while i <= max_iter:
			new_grammar = {}
			print "iteration %i" % i
			new_grammar = self.em_iteration(old_grammar, new_grammar)
			i +=1
			old_grammar = copy.deepcopy(new_grammar)
		return new_grammar

	def initialise_grammar(self):
		"""
		Initialise a grammar based on all HATs in the corpus
		"""
		init_grammar = {}
		return self.em_iteration(init_grammar, {})

	def em_iteration(self, old_grammar, new_grammar):
		"""
		Assign probabilities to all HATs in the corpus with the
		current grammar, recompute probabilities and return the
		new grammar.
		It is assumed that the HATs are precomputed and pickled into
		a file in the correct order. Every sentence under max_length should
		be represented in the file as: [sentence_nr, HAT_dict, root].
		"""
		new_grammar = {}
		self._reset_pointer()
		new = self.next()
		sentence_nr = 0
		while new:
			sentence_nr += 1
			print 'update grammar for alignment %i' %sentence_nr
			H = HATGrammar(new[2],new[1])
			grammar = H.update_weights(new_grammar, old_grammar)
			new = self.next()
		grammar_norm = self.normalise(new_grammar)
		return grammar_norm


class HATGrammar():
	"""
	Class that 
	"""
	def __init__(self,HATdict,root):
		"""
		Initialise with a dictionary uniquely representing a HAT
		"""
		self.HATs = HATdict
		self.root = root
	
	def update_weights(self, grammar, external_pcfg = {}):
		"""
		Implicitly assign all HATs in the HATforest a probability,
		normalise, and compute the counts of the rules in them
		through relative frequency estimation.
		Update the inputted grammar with these counts.
		"""
		probabilities = {}
		self.probmass(self.root, external_pcfg = external_pcfg, probs = probabilities)
		self.update(external_pcfg, probabilities, grammar, 1, self.root,)
		return grammar
	
	def probmass(self, head_node, children = (), external_pcfg = {}, probs = {}):
		"""
		Compute the probability mass of all subtrees headed by head_node with
		direct children children (possibly empty), given the input pcfg.
		"""
		nodes = (head_node,)+children
		plain_head, plain_children = self.plain_label(head_node), self.plain_label(children)
		assert len(children) == 0 or children in self.HATs[head_node], 'Head node %s does not have children %s' % (head_node, children)
		#We already computed the value before
		if nodes in probs:
			return probs[nodes]
		#node is a leaf node
		elif head_node not in self.HATs:
			prob = 1
		#compute prob mass of trees headed by head_node children
		elif len(nodes) > 1:
			prob = external_pcfg.get(plain_head,{}).get(plain_children,1)
			assert external_pcfg == {} or plain_children in external_pcfg[plain_head], '%s --> %s    not in external pcfg' %(plain_head, ' '.join(plain_children))
			for child in children:
				prob = prob*self.probmass(child, external_pcfg = external_pcfg, probs =probs)
			probs[nodes] = prob
		#compute prob mass of trees headed by head_node
		else:
			assert len(nodes) == 1
			prob = 0
			for rhs in self.HATs[head_node]:
				prob += self.probmass(head_node, rhs, external_pcfg, probs)
				probs[nodes] = prob
		assert prob > 0, 'probability mass of subtrees headed by %s cannot be 0' %head_node
		return prob


	def update(self, external_pcfg, probs, grammar, p_cur, lhs):
		"""
		Compute the updated counts for a node, given its parent
		and how often this parent occurred in the forest.
		Does not return a grammar, but modifies it globally.
		"""
		if lhs not in self.HATs:
			return
		lhs_plain = self.plain_label(lhs)
		grammar[lhs_plain] = grammar.get(lhs_plain,{})
		for rhs in self.HATs[lhs]:
			rhs_plain = self.plain_label(rhs)
			tup = (lhs,) + rhs
			c_new = p_cur * float(probs[tup])/probs[(lhs,)]
			grammar[lhs_plain][rhs_plain] = grammar[lhs_plain].get(rhs_plain,0) + c_new
			for child in rhs:
				self.update(external_pcfg, probs, grammar, c_new, child)
		return

	def plain_label(self,label):
		"""
		strip the label from the part determining
		its span, to make it uniform
		"""
		if isinstance(label, str):
			return label.split('-[')[0]
		elif isinstance(label,tuple):
			return tuple([self.plain_label(l) for l in label])
		else:
			raise TypeError("unexpected label-type %s: %s" %(label, type(label)))


	def to_WeightedGrammar(self,rule_dict, remove_old = False):
		"""
		Transforms a set of rules represented in a
		nested dictionary into a WeightedGrammar object.
		It is assumed that the startsymbol of the grammar is 
		TOP, if this is not the case, parsing with the grammar
		is not possible.
		If remove_old = True, remove the old grammar during the
		process to save memory.
		"""
		#create grammar
		productions = []
		for lhs in rule_dict:
			total = 0
			for rhs in rule_dict[lhs]:
				probability = rule_dict[lhs][rhs]
				total += probability
				rhs_list = list(rhs)
				new_production = nltk.WeightedProduction(lhs,rhs_list,prob=probability)
				productions.append(new_production)
				if not remove_old: del rule_dict[lhs][rhs]
			assert total == 1.0
			if not remove_old: del rule_dict[lhs]
		start = nltk.Nonterminal('TOP')
		return nltk.WeightedGrammar(start,productions)
