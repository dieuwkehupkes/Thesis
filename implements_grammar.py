import nltk
from nltk.grammar import *

class WeightedGrammar_nn(nltk.WeightedGrammar):
    """
	A non-normalised WeightedGrammar.
    """
    EPSILON = 0.01

    def __init__(self, start, productions, calculate_leftcorners=True):
        """
        Create a new context-free grammar, from the given start state
        and set of ``WeightedProductions``.

        :param start: The start symbol
        :type start: Nonterminal
        :param productions: The list of productions that defines the grammar
        :type productions: list(Production)
        :raise ValueError: if the set of productions with any left-hand-side
            do not have probabilities that sum to a value within
            EPSILON of 1.
        :param calculate_leftcorners: False if we don't want to calculate the
            leftcorner relation. In that case, some optimized chart parsers won't work.
        :type calculate_leftcorners: bool
        """
        nltk.ContextFreeGrammar.__init__(self, start, productions, calculate_leftcorners)

        # Make sure that the probabilities sum to one.
        probs = {}
        for production in productions:
            probs[production.lhs()] = (probs.get(production.lhs(), 0) +
                                       production.prob())

#nltk.WeightedGrammar = WeightedGrammar
