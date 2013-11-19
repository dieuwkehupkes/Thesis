import sys
import implements_grammar
from dependencies import *
from alignments import *
import nltk
from nltk import ViterbiParser

class Scoring():
	"""
	Class that provides methods for scoring alignments with different
	scoring functions.
	"""
	def __init__(self, alignment, sentence, labels = {}):
		"""
		During initialization an alignment, a corresponding
		sentence and a (possibly empty) set of labels are passed.
		
		string with dependencies are passed.
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
		Transform a rule object to a weighted production.
		
		:type rule:		Rule
		:type return:	nltk.WeightedProduction
		"""
		#create list to transform rhs to Nonterminals
		return WeightedProduction(rule.lhs(), rule.rhs(), prob = rule.probability)
	
	def transform_to_Production(self, rule):
		"""
		Transform rule to Production object (NLTK-style)
		
		:type rule:		Rule
		:type return:	nltk.Production
		"""
		#create list to transform rhs to Nonterminals
		return Production(rule.lhs(), rule.rhs())
	
	def make_lexdict(self):
		"""
		Create a dictionary assigning words to spans.
		
		:return:	A dictionary with entries of the form {span: word}
		"""
		lexdict = {}
		for i in xrange(len(self.tokens)):
			lexdict[(i,i+1)] = self.tokens[i]
		return lexdict
	
	def list_productions(self, rules):
		"""
		Given a generator object with rules, return a list
		with all the productions in it.
		
		:param rules:	A generator with rule objects
		:return:	A list with nltk.Production objects
		"""
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
		
		:return:	An Weighted grammar object with relaxed probability
					conditions.
					
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
		return WeightedGrammar_nn(start,productions), rank
			
	def parse(self, grammar, trace=0):
		"""
		Parse the sentence with the given grammar
		using the nltk viterbi parser.
		Return the best parse and its score.
		
		:param grammar:	the (adapted) WeightedGrammar object to parse with
		:param trace: determines the output of the parser.
		"""
#		print grammar
		parser = ViterbiParser(grammar)
		parser.trace(trace)
		parses = parser.nbest_parse(self.tokens)
		#return the best parse
		return parses[0]

	def score(self, rule_function, prob_function, args, trace=0):
		"""
		Score the sentence with the given rule and probability function.
		
		:param rule_function:	the function to generate rules, choices are
								rule functions from the Alignment class
		:param prob_function:	a probability function from the Rule class.
		:param args:			arguments for the probability function. If probability
								function is Rule.probability_labels, args = [labels],
								if it is Rule.probability spanrels, then args = [spanrels, normalisation_factor], if it is Rule.uniform_probabilility, then args = [].
		:param trace:		determines the amount of output by the parser.
		"""
		productions = rule_function(self.alignment, prob_function, args, self.labels)
		grammar,rank = self.grammar(productions)
		if trace >0:
			print grammar
		parse = self.parse(grammar,trace)
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


####################################################################################
#DEMONSTRATION
####################################################################################


def demo():
	"""
	A demonstration function showing the workings of the scoring class.
	"""
	import os
	print  "\nA demonstration showing how the scoring class can be used. There are 4 demo's available."
	demos = {'1': demo1, '2': demo2, '3':demo3, '4': demo4}
	while 1:
		print "\nPlease choose a demo from demo1, demo2, demo3 or demo4.\n"
#		print "\tdemo1: score according to direct similarity\n"
#		print "\tdemo2: score according to deeper similarity.\n"
#		print "\tdemo3: score according to direct similarity\n"
#		print "\tdemo4: score according to deeper similarity\n"
		valid = 0
		while not valid:
			option = raw_input("Execute one of the demo's by typing its number, or exit by typing 'q'\t")
			if option == 'q': return
			try:
				demos[option]()
				valid = 1
			except KeyError:
				print "This is not a valid option"
	return

def demo1():
	"""
	Score the sentence 'My dog likes eating sausage', with alignment '0-0 1-1 2-2 2-3 3-5 4-4' according to its direct similarity with the dependency parse. 
	"""
	if raw_input("\nDemo1\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if raw_input("") == 'q': return
	print ">>> sentence = 'my dog likes eating sausage'"
	if raw_input("") == 'q': return
	print ">>> alignment = '0-0 1-1 2-2 2-3 3-5 4-4'"
	if raw_input("") == 'q': return
	print ">>> dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']"
	if raw_input("") == 'q': return
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']
	print ">>> deps = Dependencies(dependencies)"
	if raw_input("") == 'q': return
	print ">>> nr_of_deps = deps.nr_of_deps"
	if raw_input("") == 'q': return
	print ">>> relations = deps.spanrelations()"
	deps = Dependencies(dependencies)
	relations = deps.spanrelations()
	nr_of_deps = deps.nr_of_deps
	scoring = Scoring(alignment, sentence, {})
	if raw_input("") == 'q': return
	print ">>> relations\n", relations
	if raw_input("") == 'q': return
	print ">>> tree, score, rank = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])"
	if raw_input("") == 'q': return
	tree, score, rank = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
	print "\n>>> tree\n", tree
	print "\n>>> score\n", score
	print "\n>>> rank\n", rank
	print "End of Demo 1"
	return


def demo2():
	"""
	Score the sentence 'My dog likes eating sausage', with alignment '0-0 1-1 2-2 2-3 3-5 4-4' according to its dependency parse, deeper similarity. 
	"""
	if raw_input("\nDemo2\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if raw_input("") == 'q': return
	print ">>> sentence = 'my dog likes eating sausage'"
	if raw_input("") == 'q': return
	print ">>> alignment = '0-0 1-1 2-2 2-3 3-5 4-4'"
	if raw_input("") == 'q': return
	print ">>> dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']"
	if raw_input("") == 'q': return
	sentence = 'my dog likes eating sausage'
	alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
	dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']
	print ">>> deps = Dependencies(dependencies)"
	if raw_input("") == 'q': return
	print ">>> nr_of_deps = deps.nr_of_deps"
	if raw_input("") == 'q': return
	print ">>> relations = deps.spanrelations(True, True)"
	deps = Dependencies(dependencies)
	relations = deps.spanrelations(True, True)
	nr_of_deps = deps.nr_of_deps
	scoring = Scoring(alignment, sentence, {})
	if raw_input("") == 'q': return
	print ">>> relations\n", relations
	if raw_input("") == 'q': return
	print ">>> tree, score, rank = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])"
	if raw_input("") == 'q': return
	tree, score, rank = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
	print "\n>>> tree\n", tree
	print "\n>>> score\n", score
	print "\n>>> rank\n", rank
	print "End of demo 2"
	return
	
def demo3():
	"""
	Score the sentence 'approval of the minutes of the previous sitting', with alignment '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7' according to its direct similarity with the dependency parse. 
	"""
	if raw_input("\nDemo3\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if raw_input("") == 'q': return
	print ">>> sentence = 'approval of the minutes of the previous sitting'"
	if raw_input("") == 'q': return
	print ">>> alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'"
	if raw_input("") == 'q': return
	print ">>> dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)']"
	if raw_input("") == 'q': return
	sentence = 'approval of the minutes of the previous sitting'
	alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
	dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)']
	print ">>> deps = Dependencies(dependencies)"
	if raw_input("") == 'q': return
	print ">>> nr_of_deps = deps.nr_of_deps"
	if raw_input("") == 'q': return
	print ">>> relations = deps.spanrelations()"
	deps = Dependencies(dependencies)
	relations = deps.spanrelations()
	nr_of_deps = deps.nr_of_deps
	scoring = Scoring(alignment, sentence, {})
	if raw_input("") == 'q': return
	print ">>> relations\n", relations
	if raw_input("") == 'q': return
	print ">>> tree, score, rank = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])"
	if raw_input("") == 'q': return
	tree, score, rank = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
	print "\n>>> tree\n", tree
	print "\n>>> score\n", score
	print "\n>>> rank\n", rank
	print "End of demo 3"
	return

def demo4():
	"""
	Score the sentence 'approval of the minutes of the previous sitting', with alignment '5-6 4-5 3-4 3-2 2-1 6
	"""
	if raw_input("\nDemo4\n\nPress enter to go through demo, q can be pressed at any stage to quit the demo.\t") == 'q': return
	
	if raw_input("") == 'q': return
	print ">>> sentence = 'approval of the minutes of the previous sitting'"
	if raw_input("") == 'q': return
	print ">>> alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'"
	if raw_input("") == 'q': return
	print ">>> dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)'']"
	if raw_input("") == 'q': return
	sentence = 'approval of the minutes of the previous sitting'
	alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
	dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)']
	print ">>> deps = Dependencies(dependencies)"
	if raw_input("") == 'q': return
	print ">>> nr_of_deps = deps.nr_of_deps"
	if raw_input("") == 'q': return
	print ">>> relations = deps.spanrelations(True, True)"
	deps = Dependencies(dependencies)
	relations = deps.spanrelations(True, True)
	nr_of_deps = deps.nr_of_deps
	scoring = Scoring(alignment, sentence, {})
	if raw_input("") == 'q': return
	print ">>> relations\n", relations
	if raw_input("") == 'q': return
	print ">>> tree, score, rank = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])"
	if raw_input("") == 'q': return
	tree, score, rank = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
	print "\n>>> tree\n", tree
	print "\n>>> score\n", score
	print "\n>>> rank\n", rank
	print "End van demo 4."
	return

if __name__ == "__main__":
	demo()
