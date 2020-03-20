# -*- coding: utf-8 -*-
"""
Genetic Algorithm Test Environment                             01-November-2019
                                                               Nicholas Carlson
"""

import numpy as np
import geneticAlgo as ga

def testFitnessFunc(x):
    return sum((x - np.array([5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000]))**2)

if __name__ == '__main__':
    # parameters: 
    output_file = 'geneticAlgoOutput.xlsx'
    num_generations = 10
    num_params = 8
    num_solutions = 8
    num_parents = 4
    param_ranges = [[2000, 10000],
                    [2000, 10000],
                    [2000, 10000],
                    [2000, 10000],
                    [2000, 10000],
                    [2000, 10000],
                    [2000, 10000],
                    [2000, 10000]]
    
      
    ga.geneticAlgoSolve(testFitnessFunc, 
                        output_file, 
                        num_generations, 
                        num_params, 
                        num_solutions, 
                        num_parents, 
                        param_ranges)