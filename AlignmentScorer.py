import argparse
from file_processing import *
import pickle

class AlignmentScoring():
	"""
	The class score alignments allows the user to run all scoring alignment
	functions from the commandline, and to create a file with pickled HATs
	from the alignment with labels fom the provided parses.
	"""
	def score(self,files, rule_generator, prob_function, prob_function_args,label_args,max_length,tree_file,score_file):
		"""
		Score the sentences with the given input arguments.		
		"""
		files.score_all_sentences(rule_generator, prob_function, prob_function_args, label_args, max_length, tree_file, score_file)
		files.close_all()	


def my_bool(i):
	if i == 'True' or i == 'true':
		return True
	elif i == 'False' or i == 'false':
		return False
	else:
		raise ValueError("Input string should be 'True' or 'False'")

###################################################################################
#RUN PROGRAM
###################################################################################

if __name__ == "__main__":
		#Parse arguments
	parser = argparse.ArgumentParser(description="A program for scoring alignments based on their consistency with parse trees.")
	
	#Alignment, source sentences and parse trees must be provided
	parser.add_argument("alignments", help="File with alignments")		
	parser.add_argument("source", help="File with source sentences")
	parser.add_argument("trees", help="File with parses of the source sentences")
	
	#extra input arguments
	parser.add_argument("--target", default=False, help="File with parses of the source sentences")

	#arguments for scoring
	parser.add_argument("-r", "--rules", default="HATs", choices=["HATs","all"],help="Type of rules to be used")
	parser.add_argument("-p", "--prob_function",default='spanrels', choices=['spanrels', 'labels'], help="Scoring method")
	parser.add_argument("-pa","--prob_args", nargs='*', type=my_bool, default = [], help="Set the arguments for the probability function")
	parser.add_argument("-la","--label_args", default='basic', choices = ["basic", "SAMT","all"], help="Labelling type")
	
	
	#more global arguments
	parser.add_argument("-m", "--max_length",default=40,type=int,help="The maximum sentence length")
	group2 = parser.add_mutually_exclusive_group()
	group2.add_argument("-d", "--dependencies",action="store_true", default=True, help="Run in dependency mode")
	group2.add_argument("-c", "--constituencies",action="store_true", help="Run in constituency mode")
	
	
	#Output writing options
	parser.add_argument("-t","--trees_to", default=False,help="Write any trees outputted by the program to specified file name")
	parser.add_argument("-s","--scores_to", default=False,help="Write any scores outputted by the program to specified file name")
	
	
	#Parse the arguments
	args = parser.parse_args()
	
	p_function = args.prob_function
	p_args = args.prob_args
	if p_function == 'spanrels':
		p = Rule.probability_spanrels
		if not len(p_args) == 2:
			#set default
			p_args = [True,True]
	elif p_function == 'labels':
		p = Rule.probability_labels
		p_args = [args.label_args]
	else:
		parser.error("Please choose a valid scoring method")
	
	rule_type = args.rules
	if rule_type == 'HATs':
		rule_generator = Alignments.hat_rules
	elif rule_type == 'all':
		rule_Generator = Alignments.rules
	main = AlignmentScoring()

	if args.constituencies:
		raise NotImplementedError("Scoring parses based on constituency trees is not implemented")		
	elif args.dependencies:
		files = ProcessDependencies(args.alignments, args.source, args.trees, args.target)
		main.score(files, rule_generator, p, p_args, args.label_args, args.max_length, args.scores_to, args.trees_to)
	
		
		
