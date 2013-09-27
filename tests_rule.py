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

	def rules_test_all(self):
		"""
		Return True if all rule tests return True
		"""
		return self.test_hatrules() and self.test_rules()
		
if __name__ == "__main__":
	x = RuleTests()
	print x.rules_test_all()
