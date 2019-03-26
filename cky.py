"""
COMS W4705 - Natural Language Processing - Spring 2019
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        n = len(tokens)
        pi = defaultdict()  # Initialzie the backpointers table
        for i in range(n+1):
            for j in range(i+1, n+1):
                pi[(i, j)] = defaultdict()
        for i, word in enumerate(tokens):
            for key, values in self.grammar.rhs_to_rules.items():
                #print(key,values)
                if word == key[0]:
                    for items in values:
                        pi[(i, i+1)][items[0]] = word

        #print(pi)
        # pseudocode
        # for length=2…n:
        #     for i=0…(n-length):
        #         j = i + length
        #         for k=i+1…j-1:
        #             for A ∈ N:
        #               M={A|A->BC∈R and B ∈ pi[i,k] and C∈ pi[k,j]
        #               pi[i,j]=pi[i,j] union M

        for length in range(2, n+1):
            for i in range(n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for key, values in self.grammar.rhs_to_rules.items():
                        for B in pi[(i, k)]:
                            for C in pi[(k, j)]:
                                if key[0] == B and key[1] == C: #A->BC∈R
                                    for items in values:
                                        if items[0] in pi[(i, j)]:
                                            pi[(i, j)][items[0]].append(((key[0],i,k), (key[1],k,j))) # pi[i,j]=pi[i,j] union M
                                        else:
                                            pi[(i, j)][items[0]] = [((key[0],i,k), (key[1],k,j))] # pi[i,j]= M

        if self.grammar.startsymbol in pi[(0, n)]:
            return True
        else:
            return False

       
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        n = len(tokens)
        pi = defaultdict()  # Initialzie the backpointers table
        probs = defaultdict()  # Initialzie the probabilities table
        for i in range(n+1):
            for j in range(i+1, n+1):
                pi[(i, j)] = defaultdict()
                probs[(i, j)] = defaultdict()

        for i, word in enumerate(tokens):
            for key, values in self.grammar.rhs_to_rules.items():
                #print(key,values)
                if word == key[0]:
                    for items in values:
                        pi[(i, i+1)][items[0]] = word
                        probs[(i, i+1)][items[0]] = math.log(items[2])

        #print(pi)
        # pseudocode
        # for length=2…n:
        #     for i=0…(n-length):
        #         j = i + length
        #         for k=i+1…j-1:
        #             for A ∈ N:
        #               M={A|A->BC∈R and B ∈ pi[i,k] and C∈ pi[k,j]
        #               pi[i,j]=pi[i,j] union M
        #                   ---or (put probability into consideration)---
        #               pi[i,j,A] = max P(A->BC)*pi[i,k,B]*pi[k,j,C]

        for length in range(2, n+1):
            for i in range(n - length + 1):
                j = i + length
                for k in range(i + 1, j):
                    for key, values in self.grammar.rhs_to_rules.items():
                        for B in pi[(i, k)]:
                            for C in pi[(k, j)]:
                                if key[0] == B and key[1] == C: #A->BC∈R
                                    for items in values:
                                        probability = math.log(items[2]) + probs[(i, k)][B] + probs[(k, j)][C]
                                        if items[0] in pi[(i, j)]:
                                            if probs[(i, j)][items[0]] < probability:
                                                probs[(i, j)][items[0]] = probability
                                                pi[(i, j)][items[0]] = ((key[0],i,k), (key[1],k,j)) # We only store the pi[i,j] with maximum probability
                                        else:
                                            pi[(i, j)][items[0]] = ((key[0],i,k), (key[1],k,j)) # pi[i,j]= M
                                            probs[(i, j)][items[0]] = probability


        return pi, probs


def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    if type(chart[(i, j)][nt]) == str:
        return (nt, chart[(i, j)][nt])
    left_child = chart[(i, j)][nt][0]
    right_child = chart[(i, j)][nt][1]
    return (nt, (get_tree(chart, left_child[1], left_child[2], left_child[0])), (get_tree(chart, right_child[1], right_child[2], right_child[0])))

       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.']
        #toks = ['miami','from','memphis','.']
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        tree = get_tree(table, 0, len(toks), grammar.startsymbol)
        print(tree)
        
