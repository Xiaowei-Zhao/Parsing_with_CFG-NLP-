"""
COMS W4705 - Natural Language Processing - Spring 2019
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    #print(startsymbol, prob)
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        #print(lhs, rhs, prob)
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1

        for key,values in self.lhs_to_rules.items():
            lhs = values[0][0]
            #print(lhs)
            rhs=[]
            for i in range(len(values)):
                rhs.append(values[i][2])
            #print(round(sum(rhs)))
            test = round(fsum(rhs))
            if test==1:
                return True
            else:
                return False


if __name__ == "__main__":
    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)
    if grammar.verify_grammar():
        print("Yes, the grammar is a valid PCFG in CNF")
    else:
        print("No, the grammar is not a valid PCFG in CNF")
        
