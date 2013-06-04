from get_deprels import *
from alignments import *
from graph_alignment import *
from nltk import ViterbiParser
from nltk.grammar import *

"""
Something weird happens when you do two tests in a row
"""

class Scoring():
	"""
	Compute the compositionality score of an alignment.
	"""
	def __init__(self, alignment, sentence, depfile):
		"""
		During initialization an alignment, a corresponding
		sentence and a string with dependencies is passed.
		A cfg generating all HATs is created, the dependency
		parse is used to score the different rules.
		The adapted viterbi parser from the nltk toolkit is
		used to parse the sentence and obtain the score.
		"""
		self.alignment_initialize(alignment, sentence)
		self.dependencies_initialize(depfile)
		parses = []
		for parse in self.parse():
			print parse
			parses.append(parse)
		self.score = self.score(parses[0])

	def alignment_initialize(self, alignment, sentence):
		self.alignment = Alignments(alignment,sentence)
		self.sentence = sentence

	def dependencies_initialize(self, depfile):
		self.dependencies = Dependencies(depfile)
		self.dependencies.get_spanrels()

	def parse(self):
		from nltk import grammar
		#create a nonterminal symbol
		tokens = self.sentence.split()
		startsymbol = "0N"+str(len(tokens))
		start = Nonterminal(startsymbol)
		#create the production rules for parsing, this could be faster, change later
		self.list_rules(self.dependencies.spanrels)
		self.test_rules()
		rules = self.alignment.list_rules(self.dependencies.spanrels)
		productions = parse_grammar(rules,grammar.standard_nonterm_parser,probabilistic=True, encoding=None)[1]
	#	print productions
		grammar = WeightedGrammar(start,productions)
		#Create the parser and parse the sentences		
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(tokens)
		return parses

	def list_rules(self,spanrels):
		print "nt-rules"
		for rule in self.alignment.rules(spanrels):
			print rule
		print "lexical rules"
		for rule in self.alignment.lexrules():
			print rule


	def score(self,parse):
		import math
		probability = parse.prob()
		rules_used = - math.log10(probability)
		normalization_factor = self.dependencies.nr_of_deps
		score = rules_used/normalization_factor
		return score


def test1():
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	depfile = 'dep_parse'
	scoring = Scoring(alignment, sentence, depfile)
	print scoring.score
	print "Obtained correct score for sentence:", scoring.score == 1.0

def test2():
	sentence = "european growth is inconceivable without solidarity ."
	alignment = "0-0 1-1 2-2 3-3 4-4 5-5 6-6"
	depfile = 'dep_parse2'
	scoring1 = Scoring(alignment, sentence, depfile)
	print scoring.score

