from alignments import *

class RuleTests():
	"""
	Testing class for the rule class.
	"""
	def test_rules(self):
		"""
		Test if the correct grammar is generated for
		the sentence 'My dog likes eating sausages',
		with alignment '0-0 1-1 2-2 2-3 3-5 4-4'.
		"""
		alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
		sentence = 'My dog likes eating sausages'
		a1 = Alignments(alignment, sentence)
	#	productions = a1.list_productions([])
		therules = []
		for rule in a1.rules(Rule.probability_spanrels,[{}]):
			therules.append(str(rule))
		rules_man = ['0-5 -> 0-1 1-5','0-5 -> 0-2 2-5', '0-5 -> 0-3 3-5', '0-5 -> 0-1 1-2 2-5', '0-5 -> 0-1 1-3 3-5', '0-5 -> 0-2 2-3 3-5', '0-5 -> 0-3 3-4 4-5', '0-5 -> 0-1 1-2 2-3 3-5', '0-5 -> 0-1 1-3 3-4 4-5', '0-5 -> 0-2 2-3 3-4 4-5', '0-5 -> 0-1 1-2 2-3 3-4 4-5', '1-5 -> 1-2 2-5', '1-5 -> 1-3 3-5', '1-5 -> 1-2 2-3 3-5', '1-5 -> 1-3 3-4 4-5', '1-5 -> 1-2 2-3 3-4 4-5', '2-5 -> 2-3 3-5', '2-5 -> 2-3 3-4 4-5', '0-3 -> 0-1 1-3', '0-3 -> 0-2 2-3', '0-3 -> 0-1 1-2 2-3', '0-2 -> 0-1 1-2', '1-3 -> 1-2 2-3', '3-5 -> 3-4 4-5']
		return set(rules_man) == set(therules)

	def test_hatrules(self):
		"""
		Test if the correct HATgrammar is generated for
		the sentence 'My dog likes eating sausages',
		with alignment '0-0 1-1 2-2 2-3 3-5 4-4'.
		"""
		alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
		sentence = 'My dog likes eating sausages'
		a1 = Alignments(alignment, sentence)
		therules = []
		for rule in a1.hat_rules(Rule.probability_spanrels, [{}]):
			therules.append(str(rule))
		rules_man = ['0-5 -> 0-1 1-5','0-5 -> 0-2 2-5', '0-5 -> 0-3 3-5', '1-5 -> 1-2 2-5', '1-5 -> 1-3 3-5', '2-5 -> 2-3 3-5', '0-3 -> 0-1 1-3', '0-3 -> 0-2 2-3', '0-2 -> 0-1 1-2', '1-3 -> 1-2 2-3', '3-5 -> 3-4 4-5']
		return set(rules_man) == set(therules)
	
	def test_hatrules2(self):
		"""
		Test if the correct HATgrammar is generated for
		the sentence 'My dog likes eating sausages',
		with alignment '0-0 1-1 2-2 2-3 3-5 4-4'.
		"""
		alignment = '0-0 1-1 2-3 3-2 3-4 4-6 5-5'
		sentence = 'My dog also likes eating sausages'
		lex_dict = dict(zip([(0, 1),(1, 2),(2, 3),(3, 4),(4, 5),(5, 6)],['My','dog','also','likes', 'eating', 'sausages']))
		a1 = Alignments(alignment, sentence)
		therules = []
		for rule in a1.hat_rules(Rule.probability_spanrels, [{}]):
			therules.append(str(rule))
		rules_man = ['0-2 -> 0-1 1-2', '2-4 -> 2-3 likes', '1-4 -> 1-2 2-4', '0-4 -> 0-1 1-4', '0-4 -> 0-2 2-4', '4-6 -> 4-5 5-6', '2-6 -> 2-4 4-6', '1-6 -> 1-2 2-6', '1-6 -> 1-4 4-6', '0-6 -> 0-1 1-6', '0-6 -> 0-2 2-6', '0-6 -> 0-4 4-6']
		return set(rules_man) == set(therules)
		
	def test2(self):
		sentence = 'madam president , i shall keep to the subject of the minutes .'
		alignment = '11-16 3-4 2-3 9-12 6-9 8-11 11-14 7-10 12-17 1-2 10-13 11-15 0-0 5-6 4-5 5-5 4-6 5-8 4-7 5-7 4-8 1-1'
		a1 = Alignments(alignment,sentence)
		therules = []
		for rule in a1.hat_rules(Rule.uniform_probability,[{}]):
			therules.append(rule)
		for lexrule in a1.lexrules():
			therules.append(lexrule)
		for rule in therules:
			print rule
		return		

	def rules_test_all(self):
		"""
		Return True if all rule tests return True
		"""
		return self.test_hatrules() and self.test_rules() and self.test_hatrules2()
		
if __name__ == "__main__":
	x = RuleTests()
#	x.test2()
	print x.rules_test_all()
