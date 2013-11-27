import argparse
from file_processing import *
import pickle

if __name__ == "__main__":
		#Parse arguments
	parser = argparse.ArgumentParser(description="Generate and store the HATforests of a file of sentences.")
	
	#non-optional arguments
	parser.add_argument("alignments", help="File with alignments")
	parser.add_argument("source", help="File with source sentences")
	parser.add_argument("trees", help="File with parses of the source sentences")
	
	#arguments allowing the user to change the standard settings
	parser.add_argument("-r", "--rules", default="HATs", choices=["HATs","all"],help="Set the rule type, default = HATs")
	parser.add_argument("-m", "--max_length",default=40,type=int,help="Set the maximum sentence length, default = 40")
	parser.add_argument("-la","--labelling", default=None,help="Specify how labels should be constructed", choices = ['basic', 'SAMT','all',None])
	
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-d", "--dependencies",action="store_true",help="Inputted treefile containts dependencies", default=True)
	parser.add_argument("-c", "--constituencies",action="store_true",help="Inputted treefile containts constituencies")
	
	#specify output writing options
	parser.add_argument("-H","--HATs_to",default="HATs.txt", help="Used in combination with --HATs, pickle HATs to filename")
	
	args = parser.parse_args()

	#Run the program
	files = ProcessDependencies(args.alignments,args.source,args.trees)
	files.all_HATs(args.HATs_to, args.labelling,args.max_length)

