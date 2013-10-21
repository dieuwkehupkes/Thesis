from tests_dependencies import *
from tests_node import *
from tests_scoring import *
from tests_alignments import *
from tests_rule import *
from tests_labelling import *
from tests_HATforest import *

#create testing objects for all classes and print outcome

class Tests():
	def test_all(self):
		d = DependencyTests()
		n = NodeTests()
		s = ScoreTests()
		a = AlignmentsTests()
		r = RuleTests()
		l = LabelsTests()
		h = HATsTests()
		print '\nDependency class functions as intended:\t', d.dependencies_test_all()
		print 'Node class functions as intended:\t', n.path_test_all()
		print 'Scoring class functions as intended:\t', s.score_test_all()
		print 'Rules class functions as intended:\t', r.rules_test_all()
		print 'Alignments class functions as intended:\t', a.spans_test_all()
		print  'Label class functions as intenced:\t', l.test_all()
		print  'HATs class functions as intenced:\t', h.test_all(), '\n'
	

if __name__ == "__main__":
	x = Tests()
	x.test_all()
