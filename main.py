import argparse
from file_processing import *
import pickle

class Main():
	"""
	Class with all different processes that you would want to run
	over a set of files.
	"""
	def score(self,files, rule_generator, prob_function, prob_function_args,label_args,max_length,tree_file,score_file):
		"""
		Score the sentences with the given input arguments.		
		"""
		files.score_all_sentences(rule_generator, prob_function, prob_function_args, label_args, max_length, tree_file, score_file)
		files.close_all()

	def em(self,files, max_length, grammar_file, iterations, n):
		"""
		Generate a grammar using the Expectation Maximazation algorithm.
		Return a grammar
		"""
		print 'create initial all-rule grammar.'
		rules = files.all_rules(max_length)
		print 'print rule dict to file'
		pickle.dump(rules,open('rules','wb'))
		#print dictionary to file
		print 'normalise rules'
		normalised_rules = files.normalise2(rules)
		print 'transform to nltk grammar object'
		grammar_init = files.to_WeightedGrammar(normalised_rules)
		pickle.dump(grammar_init,open('initial_grammar',"wb"))
		new_grammar = files.em(grammar_init, iterations,n)
		#store grammar in file
		pickle.dump(new_grammar,open(grammar_file,"wb"))
		print 'Grammar written to: %s' %grammar_file
			
	def evaluate_grammar(self, files, grammar_file, score_file, max_length):
		"""
		Evaluate how well an inputted grammar generates the
		sentences and alignments.
		"""
		grammar = pickle.load(open(grammar_file,"rb"))
		files.evaluate_grammar(grammar, max_length, score_file)

	def create_grammar(self, tree_file, grammar_to):
		"""
		Create a normalised grammar from a file with trees and
		store the grammar in a file.
		"""
		files = ProcessFiles(False,False,False)
		grammar = files.create_grammar(tree_file)
		pickle.dump(grammar,open(grammar_to,"wb"))
	
	def compute_branching_factor(self,files,max_length):
		b= files.branching_factor(max_length)
		print b
		total = 0
		total_nodes = 0
		for key in b:
			total += key*b[key]
			total_nodes += b[key]
		average = float(total)/total_nodes
		print 'average branching factor: %f' % average
			 
	def print_grammar_to_file(self,grammar_dict, grammar_to):
		f = open(grammar_to,'w')
		for lhs in grammar_dict:
			for rhs in grammar_dict[lhs]:
				if lhs != 'COUNTS':
					if rhs != 'COUNTS':
						rhs_string = ' '.join([str(n) for n in rhs])
						string = '%s --> %s \t %i\n' % (lhs, rhs_string, grammar_dict[lhs][rhs])
						f.write(string)
				 
				 

if __name__ == "__main__":
		#Parse arguments
	parser = argparse.ArgumentParser(description="write description of the program")
	
	#non-optional arguments
	parser.add_argument("alignments", help="File with alignments")
	parser.add_argument("source", help="File with source sentences")
	parser.add_argument("trees", help="File with parses of the source sentences")
	
	parser.add_argument("--score", action= "store_true",help="Assign the corpus a consistency score")
	parser.add_argument("--evaluate",action="store_true",help="Evaluate a grammar, grammar input required")
	parser.add_argument("--branching", action="store_true", help="compute the branching factor of the nodes in the provided treefile")
	parser.add_argument("--HATs", action="store_true", help="compute all HATs of the corpus and write to a file")
	
	parser.add_argument("--target", help="File with target sentences")
	
	#arguments allowing the user to change the standard settings
	parser.add_argument("-r", "--rules", default="HATs", choices=["HATs","all"],help="Set the rule type, default = HATs")
	parser.add_argument("-m", "--max_length",default=40,type=int,help="Set the maximum sentence length, default = 40")
	parser.add_argument("-p", "--prob_function",default=Rule.probability_spanrels,help="Change the standard method of assigning weights")
	parser.add_argument("-pa","--prob_args", nargs=2, default=[True,True],help="Set the arguments for the probability function")
	parser.add_argument("-la","--label_args", nargs = 3, default=[1,1,3],help="Specify how labels should be constructed")
	parser.add_argument("--grammar", help="Input a grammar pickled in a file")
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-d", "--dependencies",action="store_true",help="Inputted treefile containts dependencies")
	parser.add_argument("-c", "--constituencies",action="store_true",help="Inputted treefile containts constituencies")
	parser.add_argument("-i","--EM_iterations",type=int,default=1,help="Number of iterations for EM")
	
	#specify output writing options
	parser.add_argument("-t","--trees_to", default=False,help="Write any trees outputted by the program to specified file name")
	parser.add_argument("-s","--scores_to", default=False,help="Write any scores outputted by the program to specified file name")
	parser.add_argument("-g","--grammar_to",default="grammar",help="Write grammar returned by the program to file")
	parser.add_argument("-H","--HATs_to",default="HATs", help="Used in combination with --HATs, pickle HATs to filename")
	
	args = parser.parse_args()

	if not (args.score or args.evaluate or args.branching or args.HATs):
		parser.error("No running mode is specified, add --em, --evaluate or --score")

	if not (args.dependencies or args.constituencies):
		parser.error("No parse type is specified, add --dependencies or --constituencies")

	#Run the program
	if args.score:
		ruletype = args.rules
		if ruletype == 'HATs':
			rule_generator = Alignments.hat_rules
		elif ruletype == 'all':
			rule_generator = Alignment.rules	
		main = Main()
		if args.dependencies:
			files = ProcessDependencies(args.alignments,args.source,args.trees)
			print args.alignments
			main.score(files, rule_generator, args.prob_function, args.prob_args, args.label_args, args.max_length, args.scores_to, args.trees_to)
		else:
			raise NotImplementedError

	elif args.HATs:
		#there are more options here, maybe labelling should be taken into account too
		main = Main()
		files = ProcessDependencies(args.alignments,args.source,args.trees)
		files.all_HATs(args.HATs_to,args.max_length)

	elif args.evaluate:
		main = Main()
		files = ProcessFiles(args.alignments,args.source,args.trees)
		main.evaluate_grammar(files, args.grammar, args.scores_to, args.max_length)


	elif args.branching:
		main = Main()
		if args.constituencies:
			files = ProcessConstituencies(args.alignments,args.source,args.trees)
		elif args.dependencies:
			files = ProcessDependencies(args.alignments,args.source,args.trees)
		main.compute_branching_factor(files,args.max_length)
		

