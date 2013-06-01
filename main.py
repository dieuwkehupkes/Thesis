import nltk
from get_deprels import *
from graph import *
from nltk import ViterbiParser
from nltk import *
from nltk import grammar
from nltk.grammar import *

class Main():
	"""
	Compute the compositionality score of an alignment
	"""
	def __init__(self, alignment, sentence, depfile):
		self.sentence = sentence
		# Create a dependencies object and extract the span-relations		
		self.dependencies = Dependencies(depfile)
		self.dependencies.get_spanrels()
		# Create an Alignments object, print the cfg rules
		self.alignment = Alignments(alignment,sentence)
		parses = self.parse()
		for parse in parses:		
			evaluation = self.evaluate(parse)
			print evaluation

	def list_rules(self):
		rules = []
		for rule in self.alignment.rules(self.dependencies.spanrels):
			rules.append(str(rule))
		for rule in self.alignment.lexrules():
			rules.append(str(rule))
		return rules

	
	def parse(self):
		from nltk import grammar	
		tokens = self.sentence.split()
		sentence_length = len(tokens)
		startsymbol = "0N"+str(sentence_length)
		start = Nonterminal(startsymbol)
		rules = self.list_rules()
		productions = parse_grammar(rules,grammar.standard_nonterm_parser,probabilistic=True, encoding=None)[1]
		grammar = WeightedGrammar(start,productions)
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(tokens)
		return parses

	def evaluate(self,parse):
		import math
		probability = parse.prob()
		rules_used = - math.log10(probability)
		normalization_factor = self.dependencies.nr_of_deps
		score = rules_used/normalization_factor
		return score


def test():
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	depfile = 'dep_parse'
	Main(alignment, sentence,depfile)


