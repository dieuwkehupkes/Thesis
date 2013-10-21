import pickle
import nltk.grammar

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
		Return the next HAT in the file
		"""
		try:
			#return sentence_nr, root, new_HAT
			return pickle.load(self.HATfile)
		except EOFError:
			return None
			
	def _reset_pointer(self):
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

	def em(self, max_iter, max_length = 40):
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
		raise NotImplementedError
		#Build in some method for measuring the change of two grammars
#		print 'run EM with a maximum of %i iterations' %max_iter
#		i = 1#
#		self.all_rules(HATfile = 'HATs')
#		new_grammar = copy.deepcopy(start_grammar)
#		while i <= max_iter:
#			print "iteration %i" % i
#			new_grammar_dict = self.em_iteration(new_grammar, max_length)
#			i +=1
#		return new_grammar


#	def em_iteration(self, grammar, pickled_HATs, n=1, max_length = 40):
#		"""
#		Assign probabilities to all HATs in the corpus with the
#		current grammar, recompute probabilities and return the
#		new grammar.
#		It is assumed that the HATs are precomputed and pickled into
#		a file in the correct order. Every sentence under max_length should
#		be represented in the file as: [sentence_nr, HAT_dict, root].
#		"""
#		new_grammar = {}
#		self._reset_pointer()
#		f = open(pickled_HATs, 'r')
#		new = self.next()
#		sentence_nr = 1
#		while new:
#			sentence_length = len(new[1].split())
#			# tests if input is as desired, skip if not
#			if sentence_length >= max_length:
#				print 'sentence skipped'
#				pass
#			else:
#				new_alignment = Alignments(new[0], new[1])
#				s_nr, HATdict, root = pickle.load(f)
#				assert sentence_nr == s_nr
#				a.compute_weights(root, new_grammar, computed_HATforest = False, pcfg_dict = {}, labels = {})
#			new_sentence = self.next_sentence()
#			sentence_nr += 1
#		grammar_norm = self.normalise(new_grammar)
#		f.close()
#		return grammar_norm

	def unique_rules(self, step_size, max_length = 40):
		"""
		Go through a file and keep track of growth of 
		the	number of unique rules and total rules when the
		corpus grows.
		"""
		raise NotImplementedError
#		#This function should be moved to process HATs
#		unique_rules = {}
#		unique_total = 0
#		all_rules = {}
#		all_total = 0
#		self._reset_pointer()
#		sentences = 0
#		unique_dict = {}
#		new = self.next()
#		while new:
#			sentence_length = len(new[1].split())
#			if sentence_length >= max_length:
#				pass
#			else:
#				sentences += 1
#				a = Alignments(new[0],new[1])
#				dependencies = Dependencies(new[2],new[1])
#				l = Labels(dependencies.dependency_labels())
#				labels = l.label_most()
#				for rule in a.hat_rules(Rule.uniform_probability,[], labels):
#					lhs = rule.lhs().symbol()
#					rhs = tuple([rule._str(rhs) for rhs in rule.rhs()])
#					if lhs not in all_rules or rhs not in all_rules[lhs]:
#						# lhs --> rhs is not yet in all_rules
#						if lhs in unique_rules and rhs in unique_rules[lhs]:
#							# lhs --> rhs was seen once before, remove from
#							# unique dictionary, add to all_rules dictionary
#							unique_rules[lhs].remove(rhs)
#							unique_total -= 1
#							all_rules[lhs] = all_rules.get(lhs,{})
#							all_rules[lhs].update({rhs:2})
#						else:
#							# this is the first time we have seen lhs --> rhs
#							unique_total +=1
#							all_total += 1
#							unique_rules[lhs] = unique_rules.get(lhs,set([]))
#							unique_rules[lhs].add(rhs)
#					else:
#						# we have seen lhs --> rhs several times before
#						all_rules[lhs][rhs] += 1
#				
#				# if mode stepsize == 0, add to dict
#				if sentences % step_size == 0:
#					unique_dict[sentences] = [all_total, unique_total,float(unique_total)/all_total]
#					print 'Alignments: %i\tAll rules: %i\tUnique rules: %i\tPercentage unique:%f' %(sentences, all_total, unique_total, float(unique_total)/all_total)
#			new = self.next()
#		return unique_dict


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


	def to_WeightedGrammar(self,rule_dict):
		"""
		Transforms a set of rules represented in a
		nested dictionary into a WeightedGrammar object.
		It is assumed that the startsymbol of the grammar is 
		TOP, if this is not the case, parsing with the grammar
		is not possible.
		"""
		#create grammar
		productions = []
		for lhs in rule_dict:
			for rhs in rule_dict[lhs]:
				probability = rule_dict[lhs][rhs]
				rhs_list = list(rhs)
				new_production = nltk.WeightedProduction(lhs,rhs_list,prob=probability)
				productions.append(new_production)
		start = nltk.Nonterminal('TOP')
		return nltk.WeightedGrammar(start,productions)
