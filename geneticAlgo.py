# -*- coding: utf-8 -*-
"""
Genetic Algorithm                                              01-November-2019
                                                               Nicholas Carlson                                                             
Description:
    Genetic algorithm with crossover and mutation. Intended for use on 
    expensive objective functions. Multiprocessing is employed to parallelize
    function evaluations. Generation results are saved and recorded in 
    Excel file to allow for multiple deployments of the algorithm on the same
    objective function.

Inputs:
    fitnessFun: Obective function to be minimized that takes numpy array as 
                input and outputs a scalar value.
    output_file: Excel file storing information regarding previous generations.
                 If no file exists in the working directory it is created and
                 saved.
    num_generations: Number of generations to be executed.
    num_params: Number of parameters used in fitnessFun. The length of the 
                numpy array fed to the fitnessFun.
    num_solutions: Number of solutions analyzed in each generation. Since
                   multiprocessing is used it is advised to set this as a 
                   multiple of the number of cpu's available.
    num_parents: Number of parents used to generate offspring after a new
                 generation is created.
    param_ranges: Ranges of fitnessFun parameters. Used to generate initial
                  population if not output_file exists in working directory.
                  
Output: Excel file containing latest solutions ranked from lowest fitness to
        highest, corresponding fitness values, and a record of the solution 
        with the minimum fitness value after each generation.
        
Notes: 
    1) If running in IPython Console / Spyder, ensure function is executed 
       in files directory in a dedicated console to ensure multiprocessing 
       will function correctly. If these conditions are not met, the code will
       hang on the first generation.
    2) The output file will be dumped into working directory.
"""

import numpy as np
import xlwings as xl
import multiprocessing as mp


def crossover(parents, num_solutions, num_parents, num_params):
    
     num_offspring = num_solutions - num_parents
     offspring = np.empty((num_offspring, num_params))
     
     # Center is point at which crossover takes place between two parents.
     crossover_point = np.uint8(num_params/2)
     
     for k in range(num_offspring):
         parent1_ind = k % num_parents
         parent2_ind = (k+1) % num_parents
         offspring[k, 0:crossover_point] = parents[parent1_ind, 0:crossover_point]
         offspring[k, crossover_point:] = parents[parent2_ind, crossover_point:]
         
     return offspring


def mutation(offspring_crossover, num_params, param_ranges):
    
    # Mutation changes a single value in a ranomly selected gene.
    for row in range(offspring_crossover.shape[0]):
        col = np.random.randint(0, num_params)
        low_bound = param_ranges[col][0]
        high_bound = param_ranges[col][1]
        new_gene = np.random.uniform(low_bound, high_bound, 1)
        offspring_crossover[row, col] = new_gene 
    
    return offspring_crossover



def solver(fitnessFun, fitness, population, no_data, num_solutions, num_parents, num_cpu):
             
    if no_data:
        req_solutions = num_solutions
    else:
        req_solutions = num_solutions - num_parents
     
    comp_solutions = 0
    
    # Loop until all required solutions are computed.
    while comp_solutions < req_solutions:
        num_processes = min(req_solutions - comp_solutions, num_cpu)
        mpPool = mp.Pool(num_processes)
        i1 = num_solutions - comp_solutions - num_processes
        i2 = i1 + num_processes
        fitness[i1:i2] = mpPool.map(fitnessFun, population[i1:i2, :])
        mpPool.close()
        mpPool.join()
        comp_solutions += num_processes
    
    return fitness



def geneticAlgoSolve(fitnessFun, output_file, num_generations, 
                     num_params, num_solutions, num_parents, param_ranges):
    
    # Load or generate output file containing stored data from previous 
    # generations and load or initialize population, fitness, and record.
    try:
        
        print('Loading Excel Workbook ' + output_file + '...')
        
        # Attempt to open existing output file in working directory
        wb = xl.Book(output_file)
        
        # Recover existing population already ranked from smallest
        # to largest fitness.
        population_sheet = wb.sheets['Population']
        population = np.array(population_sheet.range((1, 1),(num_solutions, num_params)).value)
        
        # Recover existing fitness values of populations.
        fitness_sheet = wb.sheets['Fitness']
        fitness = np.array(fitness_sheet.range((1, 1),(1, num_solutions)).value)
        
        # Recover record of best fitness values for each of the previous
        # generations of solutions.
        record_sheet = wb.sheets['Record']
        recorded_generations = int(record_sheet.range((3, 5)).value)
        record = np.array(record_sheet.range((6, 2), (5 + recorded_generations, 3 + num_params)).value)
        
        # If all data recoveries pass, pass no_data is False to algorithm.
        no_data = False
        
        print('   ' + output_file + ' loaded successfully.')
        
    except:
        
        print('   Workbook ' + output_file + ' not found in working directory')
        print('   Creating Workbook...')
        
        # If no existing output file with specified name exists create 
        # the Excel file with predefined format.
        wb = xl.Book()
        wb.sheets.add('Population')
        wb.sheets.add('Record')
        wb.sheets.add('Fitness')
        
        # load worksheets just created for use in function.
        population_sheet = wb.sheets['Population']
        fitness_sheet = wb.sheets['Fitness']
        record_sheet = wb.sheets['Record']
        
        # Format output file (mainly the record sheet).
        record_sheet.range((1,2)).value = 'Genetic Algorithm Record'
        record_sheet.range((3,2)).value = 'Number of Generations'
        record_sheet.range((5,2)).value = 'Generation'
        record_sheet.range((5,3)).value = 'Parameters'
        record_sheet.range((5, 3 + num_params)).value = 'Fitness'
        record_sheet.range((3, 5)).value = 0 # initialize number of recorded generations to 0
        
        if len(param_ranges) != num_params:
            
            print('parameter ranges list is not equal to specified number of parameters')
            return
            
        else:
            
            # Create randomized population with parameter values 
            # between the specified ranges in param_ranges input
            population = np.empty((num_solutions, num_params))
            for col in range(num_params):
                low_bound = param_ranges[col][0]
                high_bound = param_ranges[col][1]
                rand_params = np.random.uniform(low=low_bound, high=high_bound, size=num_solutions)
                population[:, col] = rand_params
        
            # Create fitness list initialized with zeros.
            fitness = np.array([0 for k in range(num_solutions)])
            
            # Create empty record that will be overwritten.
            record = np.empty((1, num_params + 2))
            
        no_data = True
        
        print('   Workbook was created successfully.')
    
    # Determine maximum number of cpu's available for multiprocessing.
    num_cpu = mp.cpu_count()
    
    for generation in range(num_generations):
         
         print('Running Generation: ' + str(generation + 1) + ' of ' + str(num_generations) + '...')
         print('   Selecting parents and generating offspring...')
         
         # Select the best in population in terms of fitness to
         # be parents for mating.
         parents = population[0:num_parents, :]
     
         # Generating next generation using crossover.
         offspring_crossover = crossover(parents, num_solutions, num_parents, num_params)
     
         # Adding some variations to the offsrping using mutation.
         offspring_mutation = mutation(offspring_crossover, num_params, param_ranges)
         
         # Creating the new population based on the parents and offspring.
         population[num_parents:, :] = offspring_mutation
        
         # Solve fitness function for new members of population.
         print('   Computing fitness values...')
         fitness = solver(fitnessFun, fitness, population, no_data, num_solutions, num_parents, num_cpu)
            
         # Sort population by fitness level (smallest to largest).
         sinds = fitness.argsort()
         population = population[sinds, :]
         fitness = fitness[sinds]
         
         # Dump best in population to output file each iteration to track evolutionary progress.
         print('   Recording generation data in ' + output_file + '...')
         population_sheet.range((1, 1)).value = population
         fitness_sheet.range((1, 1)).value = fitness
         new_record = np.empty((2 + num_params,))
         if no_data:    
             recorded_generations = 1
             new_record[0] = recorded_generations
             new_record[1:(num_params+1)] = population[0, :]
             new_record[num_params+1] = fitness[0]
             record = new_record
             no_data = False
             wb.save(output_file)    
         else:  
             recorded_generations += 1
             new_record[0] = recorded_generations
             new_record[1:(num_params+1)] = population[0, :]
             new_record[num_params+1] = fitness[0]
             record = np.vstack((record, new_record))    
         record_sheet.range((3, 5)).value = recorded_generations
         record_sheet.range((6, 2)).value = record
         wb.save()