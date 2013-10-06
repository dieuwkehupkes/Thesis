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
		files = ProcessDependencies(alignments, sentences, dependencies)
		files.score_all_sentences(rule_generator, prob_function, prob_function_args, label_args, max_length, tree_file, score_file)
		files.close_all()


	def em(self,files, max_length, grammar_file, iterations, n):
		"""
		Generate a grammar using the Expectation Maximazation algorithm.
		Return a grammar
		"""
		rules = files.all_rules(max_length)
		normalised_rules = files.normalise2(rules)
		grammar_init = files.to_WeightedGrammar(normalised_rules)
		new_grammar = files.em(grammar_init, iterations,n)
		#store grammar in file
		pickle.dump(new_grammar,open(grammar_file,"wb"))
			
	def evaluate_grammar(self, files, grammar_file, score_file, max_length):
		"""
		Evaluate how well an inputted grammar generates the
		sentences and alignments.
		"""
		grammar = pickle.load(open(grammar_file,"rb"))
		files.evaluate_grammar(grammar, max_length, score_file)




if __name__ == "__main__":
		#Parse arguments
	parser = argparse.ArgumentParser(description="write description of the program")
	
	#non-optional arguments
	parser.add_argument("alignments", help="File with alignments")
	parser.add_argument("source", help="File with source sentences")
	parser.add_argument("trees", help="File with parses of the source sentences")
	parser.add_argument("mode", type=str, choices = ["score","em","evaluate"],help="Specify the running mode of the program")	
	
	parser.add_argument("--target", help="File with target sentences")
	
	#arguments allowing the user to change the standard settings
	parser.add_argument("-r", "--rules", default="HATs", choices=["HATs","all"],help="Change the standard rule type")
	parser.add_argument("-m", "--max_length",default=40,type=int,help="Change the standard maximum sentence length")
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
	
	args = parser.parse_args()


	ruletype = args.rules
	if ruletype == 'HATs':
		rule_generator = Alignments.hat_rules
	elif ruletype == 'all':
		rule_generator = Alignment.rules	
	
	#Run the program
	if args.mode == "score":
		main = Main()
		if args.dependencies:
			files = ProcessDependencies(args.alignments,args.source,args.trees)
			main.score(files, rule_generator, args.prob_function, args.prob_args, args.label_args, args.max_length, args.scores_to, args.trees_to)
		else:
			raise NotImplementedError
	
	if args.mode == "em":
		main = Main()
		if args.dependencies:
			files = ProcessDependencies(args.alignments, args.source, args.trees)
		else:
			files = ProcessConstituencies(args.alignments, args.source, args.trees)
		new_grammar = main.em(files, args.max_length, args.grammar_to, args.EM_iterations, 1)

	if args.mode == "evaluate":
		main = Main()
		files = ProcessFiles(args.alignments,args.source,args.trees)
		main.evaluate_grammar(files, args.grammar, args.scores_to, args.max_length)


		

