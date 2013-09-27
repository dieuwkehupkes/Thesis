from scoring import *

class ScoreTests():
	"""
	Test Scoring Class
	"""
	def score_test_all(self):
		return self.score_test1() and self.score_test2() and self.score_test3() and self.score_test4() and self.score_test7() and self.score_test8()

	def score_test1(self):
		"""
		Sentence: 'my dog likes eating sausage'
		Alignment: '0-0 1-1 2-2 2-3 3-5 4-4'
		Dependencies: 'nsubj(likes-3, dog-2)', 'root(ROOT-0, likes-3)',
		'xcomp(likes-3, eating-4)' and 'dobj(eating-4, sausages-5)'.
	
		Manual score normal rules spanrels: 1.0
		Manual score hatrules spanrels: 0.75
		Manual score hatrules spanrels deep: 1.0
		"""
		sentence = 'my dog likes eating sausage'
		alignment = '0-0 1-1 2-2 2-3 3-5 4-4'
		dependencies = ['poss(dog-2, My-1)','nsubj(likes-3, dog-2)','root(ROOT-0, likes-3)','xcomp(likes-3, eating-4)','dobj(eating-4, sausages-5)']
		deps = Dependencies(dependencies)
		nr_of_deps = deps.nr_of_deps
		relations = deps.spanrelations()
		scoring = Scoring(alignment, sentence, {})
		tree1, score1 = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
		tree2, score2 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		relations = deps.spanrelations(True, True)
		tree3, score3 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score1 == 1.0 and score2 == 0.75 and score3 == 1.0


	def score_test2(self):
		"""
		Sentence: 'european growth is inconceivable without solidarity .'
		Alignment: '0-0 1-1 2-2 3-3 4-4 5-5 6-6'
		Dependencies: 'nn(growth-2, european-1)', 'nsubj(inconceivable-4, growth-2)',
		'cop(inconceivable-4, is-3)', 'root(ROOT-0, inconceivable-4)', 
		'prep(inconceivable-4, without-5)' and 'pobj(without-5, solidarity-6)'
	
		Manual score all rules spanrels: 1.0
		Manual score hat rules spanrels: 0.6
		Manual score hat rules spanrels deep: 1.0
		"""
		sentence = "european growth is inconceivable without solidarity ."
		alignment = "0-0 1-1 2-2 3-3 4-4 5-5 6-6"
		dependencies = ['nn(growth-2, european-1)','nsubj(inconceivable-4, growth-2)','cop(inconceivable-4, is-3)','root(ROOT-0, inconceivable-4)','prep(inconceivable-4, without-5)','pobj(without-5, solidarity-6)']
		deps = Dependencies(dependencies)
		nr_of_deps = deps.nr_of_deps
		relations = deps.spanrelations()
		scoring = Scoring(alignment, sentence, {})
		tree1, score1 = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
		tree2, score2 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		relations = deps.spanrelations(True, True)
		tree3, score3 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score1 == 1.0 and score2 == 0.6 and score3 == 1.0

	def score_test3(self):
		"""
		Sentence: 'approval of the minutes of the previous sitting'
		Alignment: '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		Dependencies: 'root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)'

		Manual score all rules spanrels: 0.59
		Manual score hat rules spanrels: 0.57
		Manual score hat rules spanrels deep: 1.0
		"""
		sentence = 'approval of the minutes of the previous sitting'
		alignment = '5-6 4-5 3-4 3-2 2-1 6-8 3-3 1-1 0-0 7-7'
		dependencies = ['root(ROOT-0, approval-1)','prep(approval-1, of-2)', 'det(minutes-4, the-3)','pobj(of-2, minutes-4)','prep(approval-1, of-5)','det(sitting-8, the-6)','amod(sitting-8, previous-7)','pobj(of-5, sitting-8)']
		deps = Dependencies(dependencies)
		nr_of_deps = deps.nr_of_deps
		relations = deps.spanrelations()
		scoring = Scoring(alignment, sentence, {})
		tree1, score1 = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
		tree2, score2 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		relations = deps.spanrelations(True, True)
		tree3, score3 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score1 == float(6)/7 and score2 == float(3)/7 and score3 == float(5)/7


	def score_test4(self):
		"""
		Sentence: 'resumption of the session'
		Alignment: '3-3 2-2 1-1 0-0'
		Dependencies: 'root(ROOT-0, resumption-1)','prep(resumption-1, of-2)','det(session-4, the-3)','pobj(of-2, session-4)'
	
		Manual score all rules spanrels: 1.0
		Manual score hat rules spanrels: 1.0
		Manual score hat rules spanrels deep: 1.0	
		"""
		sentence = 'resumption of the session'
		alignment = '3-3 2-2 1-1 0-0'
		dependencies = ['root(ROOT-0, resumption-1)','prep(resumption-1, of-2)','det(session-4, the-3)','pobj(of-2, session-4)']
		deps = Dependencies(dependencies)
		nr_of_deps = deps.nr_of_deps
		relations = deps.spanrelations()
		scoring = Scoring(alignment, sentence, {})
		tree1, score1 = scoring.score(Alignments.rules, Rule.probability_spanrels, [relations, nr_of_deps])
		tree2, score2 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		relations = deps.spanrelations(True, True)
		tree3, score3 = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score1 == 1.0 and score2 == 1.0 and score3 == 1.0

	def score_test5(self):
		"""
		no dependencies
		"""
		sentence = '( 2 ) -do-'
		alignment = '0-0'
		dependencies = []
		deps = Dependencies(dependencies)
		print deps.checkroot()
		labels = deps.labels(1,1,3)
		print labels
		scoring = Scoring(alignment, sentence, labels)
		tree, score = scoring.score(Alignments.hat_rules, Rule.probability_labels, [labels])
		print(tree)
		print score
	
	def score_test6(self):
		"""
		dependencies form no tree
		"""
		sentence = '. ( pt ) we basically agree with the assessment and the thoughts put forward by the rapporteur concerning the sixth periodic report on the social and economic situation and development of the regions of the european union .'
		alignment = '0-0'
		dependencies = ['discourse(.-1, pt-3)','nsubj(agree-7, we-5)','advmod(agree-7, basically-6)','rcmod(.-1, agree-7)','prep(agree-7, with-8)','det(assessment-10, the-9)','pobj(with-8, assessment-10)','cc(assessment-10, and-11)','det(thoughts-13, the-12)','conj(assessment-10, thoughts-13)','root(ROOT-0, put-14)','advmod(put-14, forward-15)','prep(put-14, by-16)','det(rapporteur-18, the-17)','pobj(by-16, rapporteur-18)','det(report-23, the-20)','amod(report-23, sixth-21)','amod(report-23, periodic-22)','pobj(concerning-19, report-23)','prep(report-23, on-24)','det(situation-29, the-25)','amod(situation-29, social-26)','cc(social-26, and-27)','conj(social-26, economic-28)','pobj(on-24, situation-29)','cc(situation-29, and-30)','conj(situation-29, development-31)','prep(development-31, of-32)','det(regions-34, the-33)','pobj(of-32, regions-34)','prep(regions-34, of-35)', 'det(union-38, the-36)','nn(union-38, european-37)','pobj(of-35, union-38)']
		deps = Dependencies(dependencies)
		labels = deps.labels(1,1,3)
		scoring = Scoring(alignment, sentence, labels)
		tree, score = scoring.score(Alignments.hat_rules, Rule.probability_labels, [labels])
		print(tree)
		print score
	
	def score_test7(self):
		"""
		Test to check workings for interpunction.
		"""
		sentence = "the minutes of the sitting on thursday , 21 september have been distributed ."
		dependencies = ['det(minutes-2, the-1)','nsubjpass(distributed-13, minutes-2)','prep(minutes-2, of-3)','pobj(of-3, the-4)','amod(the-4, sitting-5)','prep(the-4, on-6)','pobj(on-6, Thursday-7)','num(September-10, 21-9)','nsubjpass(distributed-13, September-10)','aux(distributed-13, have-11)','auxpass(distributed-13, been-12)','root(ROOT-0, distributed-13)']
		alignment = '3-5 6-8 11-13 1-3 2-4 12-14 10-12 9-10 1-2 5-7 13-15 0-0 1-1 8-9 4-6 10-11'
		deps = Dependencies(dependencies)
		scoring = Scoring(alignment,sentence)
		relations = deps.spanrelations(True,True)
		nr_of_deps = deps.nr_of_deps
		tree, score = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score == 1.0
	
	def score_test8(self):
		"""
		Second interpunction check.
		"""
		sentence = "yes indeed , mrs thors , we shall amend the minutes accordingly ."
		alignment = "8-7 7-6 6-5 5-4 12-12 4-3 3-2 10-10 10-11 10-9 2-1 1-0 0-0 9-8"
		dependencies = ["discourse(mrs-4, yes-1)","dep(yes-1, indeed-2)","ccomp(amend-9, mrs-4)","dobj(mrs-4, thors-5)","nsubj(amend-9, we-7)","aux(amend-9, shall-8)",'root(ROOT-0, amend-9)','det(minutes-11, the-10)','dobj(amend-9, minutes-11)','advmod(amend-9, accordingly-12)']
		deps = Dependencies(dependencies)
		scoring = Scoring(alignment,sentence)
		relations = deps.spanrelations(True,True)
		nr_of_deps = deps.nr_of_deps
		tree, score = scoring.score(Alignments.hat_rules, Rule.probability_spanrels, [relations, nr_of_deps])
		return score == 1.0

if __name__ == "__main__":
	x = ScoreTests()
	print x.score_test_all()

