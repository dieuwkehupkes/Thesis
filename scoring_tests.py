from scoring import *

#Test scoring class
"""
Test Scoring Class
"""

def score_test_all():
	return score_test1() and score_test2() and score_test3()

def score_test1():
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


def score_test2():
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

def score_test3():
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


def score_test4():
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

def score_test5():
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
	
def score_test6():
	"""
	dependencies form no tree
	"""
	sentence = '. ( pt ) we basically agree with the assessment and the thoughts put forward by the rapporteur concerning the sixth periodic report on the social and economic situation and development of the regions of the european union .'
	alignment = '0-0'
	dependencies = ['discourse(.-1, pt-3)','nsubj(agree-7, we-5)','advmod(agree-7, basically-6)','rcmod(.-1, agree-7)','prep(agree-7, with-8)','det(assessment-10, the-9)','pobj(with-8, assessment-10)','cc(assessment-10, and-11)','det(thoughts-13, the-12)','conj(assessment-10, thoughts-13)','root(ROOT-0, put-14)','advmod(put-14, forward-15)','prep(put-14, by-16)','det(rapporteur-18, the-17)','pobj(by-16, rapporteur-18)','det(report-23, the-20)','amod(report-23, sixth-21)','amod(report-23, periodic-22)','pobj(concerning-19, report-23)','prep(report-23, on-24)','det(situation-29, the-25)','amod(situation-29, social-26)','cc(social-26, and-27)','conj(social-26, economic-28)','pobj(on-24, situation-29)','cc(situation-29, and-30)','conj(situation-29, development-31)','prep(development-31, of-32)','det(regions-34, the-33)','pobj(of-32, regions-34)','prep(regions-34, of-35)', 'det(union-38, the-36)','nn(union-38, european-37)','pobj(of-35, union-38)']
	deps = Dependencies(dependencies)
	print deps.checkroot()
	labels = deps.labels(1,1,3)
	scoring = Scoring(alignment, sentence, labels)
	tree, score = scoring.score(Alignments.hat_rules, Rule.probability_labels, [labels])
	print(tree)
	print score
