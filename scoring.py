"""
"""

from dependencies import *
from alignments import *
from nltk import ViterbiParser
from nltk.grammar import *

class Scoring():
	"""
	Class that provides methods for scoring an alignment according
	to a set of preferred relations. The corresponding tree
	is created, spanlabels can be entered to label the nodes
	in the tree.
	"""
	def __init__(self, alignment, sentence, labels = {}):
		"""
		During initialization an alignment, a corresponding
		sentence and a string with dependencies are passed.
		A weighted CFG generating all HATs is created, the rules are
		assigned 'probabilities' according to preferred_relations or
		labels.
		The adapted viterbi parser from the nltk toolkit is
		used to parse the sentence and obtain the score.
		"""
		self.alignment = Alignments(alignment, sentence)
		self.sentence = sentence
		self.labels = labels
		self.tokens = sentence.split()
	
	def grammar(self, rules):
		"""
		Return a weighted grammar (NLTK-style) given
		a generator object with all rules.
		"""
		from nltk import grammar
		# Create a list with productions
		productions = []
		for rule in rules:
			#create list to transform rhs to Nontemrinals
			rhs_list = []
			for rhs in rule.rhs:
				rhs_list.append(Nonterminal(rhs))
			productions.append(WeightedProduction(Nonterminal(rule.lhs), rhs_list,
			prob = rule.probability))
		for rule in self.alignment.lexrules(self.labels):
			productions.append(rule)
		# Transform into a grammar to parse
		startsymbol = "0-"+str(len(self.tokens))
		start = Nonterminal(startsymbol)
		return WeightedGrammar(start,productions)
			
	def parse(self, grammar):
		"""
		Parse the sentence with the given grammar
		using the viterbi parser from the nltk.
		Return the best parse and its score.
		"""
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(self.tokens)
		#return the best parse
		return parses[0]

	def relation_score(self,parse):
		"""
		Return non normalized score of a sentence by
		computing how many rules were used.
		"""
		import math
		probability = parse.prob()
		rules_used = math.log(probability,2)
		return rules_used

	def label_score(self, parse):
		"""
		Return how many of the HATnodes could
		be labelled according to the grammar
		"""
		return parse.prob()

	def score(self, rule_function, prob_function, args):
		productions = rule_function(self.alignment, prob_function, args)
		grammar = self.grammar(productions)
		parse = self.parse(grammar)
		score = parse.prob()
		if prob_function == Rule.probability_spanrels:
			import math
			score = math.log(score,2)/args[1]
		return parse, score


