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
#			print "next rule"
			#create list to transform rhs to Nontemrinals
			rhs_list = []
			for rhs in rule.rhs:
				rhs_list.append(Nonterminal(rhs))
			productions.append(WeightedProduction(Nonterminal(rule.lhs), rhs_list,
			prob = rule.probability))
#			print "created weighted production for", rule
#		print 'loop ended'
		for rule in self.alignment.lexrules(self.labels):
#			print "get to lexrules"
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
			score = 0
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
	grammar = scoring.grammar(productions)
	parse = scoring.parse(grammar)
	score = scoring.score(parse)
	print "Obtained correct score for sentence:", score == 1.0

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
	
	print "Obtained correct score for sentence:", score == 1.0

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

def speed_testt():
	sentence = "let us ensure , Mr President , Commissioner , that this time we really do learn the lesson , even after the media hype and the shock of this House have died down ."
	alignment = "0-0 1-0 1-1 2-9 3-10 4-11 4-12 5-13 6-14 7-15 7-17 8-18 10-2 11-3 13-4 14-23 15-5 15-6 16-21 17-21 17-22 18-19 21-26 22-29 23-32 24-30 27-7 28-8 29-31 31-32 32-32 33-33"
	dependencies = ["root(ROOT-0, let-1)","nsubj(ensure-3, us-2)","ccomp(let-1, ensure-3)","nn(President-6, Mr-5)","dobj(ensure-3, President-6)","appos(President-6, Commissioner-8)","mark(learn-16, that-10)","det(time-12, this-11)","nsubj(learn-16, time-12)","nsubj(do-15, we-13)","advmod(do-15, really-14)","rcmod(time-12, do-15)","ccomp(ensure-3, learn-16)","det(lesson-18, the-17)","dobj(learn-16, lesson-18)","advmod(died-32, even-20)","mark(died-32, after-21)","det(hype-24, the-22)","nn(hype-24, media-23)","nsubj(died-32, hype-24)","cc(hype-24, and-25)","det(shock-27, the-26)","conj(hype-24, shock-27)","prep(shock-27, of-28)","det(House-30, this-29)","pobj(of-28, House-30)","aux(died-32, have-31)","advcl(ensure-3, died-32)","prt(died-32, down-33)"]
	deps = Dependencies(dependencies)
	relations = deps.get_spanrels()
	print 'create scoring object'
	scoring = Scoring(alignment, sentence, relations)
#	for span in scoring.alignment.spans():
#		print span
	print 'create productions'
	productions = scoring.alignment.hat_rules(relations)
	for rule in productions:
		continue
	print 'finished'

