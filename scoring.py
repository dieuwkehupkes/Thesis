"""
"""
import sys
import implements_grammar
from dependencies import *
from alignments import *
import nltk
from nltk import ViterbiParser

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
	
	def transform_to_WeightedProduction(self, rule):
		"""
		Transform rule to WeightedProduction object (NLTK-style)
		"""
		#create list to transform rhs to Nonterminals
		rhs_list = []
		for rhs in rule.rhs:
			rhs_list.append(Nonterminal(rhs))
		return WeightedProduction(Nonterminal(rule.lhs), rhs_list, prob = rule.probability)
	
	def transform_to_Production(self, rule):
		"""
		Transform rule to Production object (NLTK-style)
		"""
		#create list to transform rhs to Nonterminals
		rhs_list = []
		for rhs in rule.rhs:
			rhs_list.append(Nonterminal(rhs))
		return Production(Nonterminal(rule.lhs), rhs_list)
	
	
	def make_lexdict(self):
		"""
		Create a dictionary assigning words to spans.
		"""
		lexdict = {}
		for i in xrange(len(self.tokens)):
			lexdict[(i,i+1)] = self.tokens[i]
		return lexdict
	
	def list_productions(self, rules):
		productions = []
		lex_dict = self.make_lexdict()
		for rule in rules:
			p_rule = self.alignment.prune_production(rule, lex_dict)
			productions.append(self.transform_to_Production(p_rule))
		for rule in self.alignment.lexrules(self.labels, False):
			productions.append(rule)
		return productions
	
	def grammar_rank(self,rules):
		"""
		Determine the maximum rank of a set of rules.
		"""
		rank = 0
		for rule in rules:
			if rule.rank() > rank:
				rank = rule.rank()
		return rank
	
	def grammar(self, rules):
		"""
		Return a weighted grammar (NLTK-style) and its rank
		given a generator object with all rules.
		"""
		# Create a list with productions
		productions = []
		rank = 0
		for rule in rules:
			if rule.rank() > rank:
				rank = rule.rank()
			productions.append(self.transform_to_WeightedProduction(rule))
		for rule in self.alignment.lexrules(self.labels):
			productions.append(rule)
		# Transform into a grammar to parse
		startsymbol = self.labels.get((0,len(self.tokens)), "0-"+str(len(self.tokens)))
		start = Nonterminal(startsymbol)
		return WeightedGrammar(start,productions), rank
			
	def parse(self, grammar):
		"""
		Parse the sentence with the given grammar
		using the viterbi parser from the nltk.
		Return the best parse and its score.
		"""
#		print grammar
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(self.tokens)
		#return the best parse
		return parses[0]

	def score(self, rule_function, prob_function, args):
		"""
		Score, args are arguments for prob_function.
		Thus: if probfunction = Rule.probability_labels, then args
		should be [labels], if it is Rule.probability_spanrels then
		args should be [spanrels, normalization_factor]
		"""
		productions = rule_function(self.alignment, prob_function, args, self.labels)
		grammar,rank = self.grammar(productions)
		parse = self.parse(grammar)
		score = parse.prob()
		if prob_function == Rule.probability_spanrels:
			import math
			if args[1] != 0:
				score = math.log(score,2)/args[1]
			else:
				score = 1
		elif prob_function == Rule.probability_labels:
			import math
			score = 1/score
			if parse.nr_of_nonterminals != 0:
				score = 1- math.log(score,2)/parse.nr_of_nonterminals()
			else:
				score = 0
		return parse, score, rank


