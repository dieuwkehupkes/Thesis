from dependencies import *
from alignments import *
from graph_alignment import *
from nltk import ViterbiParser
from nltk.grammar import *


class Scoring():
	"""
	Class that provides methods forscoring an alignment according
	to a set of preferred relations. The corresponding tree
	is created, spanlabels can be entered to label the nodes
	in the tree.
	"""
	def __init__(self, alignment, sentence, preferred_relations, labels = {}):
		"""
		During initialization an alignment, a corresponding
		sentence and a string with dependencies is passed.
		A cfg generating all HATs is created, the dependency
		parse is used to score the different rules.
		The adapted viterbi parser from the nltk toolkit is
		used to parse the sentence and obtain the score.
		"""
		self.alignment_initialize(alignment, sentence)
		self.relations = preferred_relations
		self.labels = labels
		self.tokens = sentence.split()

	def alignment_initialize(self, alignment, sentence):
		self.alignment = Alignments(alignment,sentence)
		self.sentence = sentence
	
	def grammar(self, rules):
		"""
		Output grammar productions, given a generator
		object iterating over all the possible rules
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
		Parse the sentence with the viterbi parser
		from the nltk toolkit.
		"""
		parser = ViterbiParser(grammar)
		parser.trace(0)
		parses = parser.nbest_parse(self.tokens)
		#return the best parse
		return parses[0]

	def normalization_factor(self):
		normalization_factor = 0
		for head in self.relations:
			for dependent in self.relations[head]:
				normalization_factor += 1
		return normalization_factor

	def score(self,parse):
		import math
		probability = parse.prob()
		rules_used = math.log(probability,2)
		normalization_factor = self.normalization_factor()
		if normalization_factor != 0:
			score = rules_used/normalization_factor
		else:
			score = 1
		return score

#Tests

def test1():
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	labels = deps.labels()
	scoring = Scoring(alignment, sentence, relations, labels)
	productions = scoring.alignment.rules(relations,labels)
#	for production in productions:
#		print production
#	productions = scoring.alignment.rules(relations,labels)	
	grammar = scoring.grammar(productions)
	parse = scoring.parse(grammar)
	score = scoring.score(parse)
	return score == 1.0

def test2():
	sentence = "european growth is inconceivable without solidarity ."
	alignment = "0-0 1-1 2-2 3-3 4-4 5-5 6-6"
	dependencies = ['nn(growth-2, european-1)','nsubj(inconceivable-4, growth-2)','cop(inconceivable-4, is-3)','root(ROOT-0, inconceivable-4)','prep(inconceivable-4, without-5)','pobj(without-5, solidarity-6)']
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	labels = deps.labels()
	scoring = Scoring(alignment, sentence, relations, labels)
	productions = scoring.alignment.rules(relations,labels)
	grammar = scoring.grammar(productions)
	parse = scoring.parse(grammar)
	score = scoring.score(parse)	
	return score == 1.0

def speed_test1(sentence_length):
	import time
	time1 = time.time()
	s = [str(i) for i in xrange(sentence_length)]
	sentence = " ".join(s)
	a = [str(i)+'-'+str(i) for i in xrange(sentence_length)]
	alignment = " ".join(a)
	dependencies = ["root(ROOT-0,let-1)"]
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	scoring = Scoring(alignment, sentence, relations)
	productions = scoring.alignment.hat_rules(relations)
	for rule in productions:
		continue
	time2 = time.time()
	print "processing time:", time2-time1
	

def speed_test2(sentence_length):
	import time
	time1 = time.time()
	s = [str(i) for i in xrange(sentence_length)]
	sentence = " ".join(s)
	a = [str(i)+'-'+str(j) for i in xrange(sentence_length) for j in xrange(sentence_length)]
	alignment = " ".join(a)
	dependencies = ["root(ROOT-0, let-1)"]
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	scoring = Scoring(alignment,sentence, relations)
	productions = scoring.alignment.hat_rules(relations)
	for rule in productions:
		continue
	time2 = time.time()
	print "processing time:", time2-time1

