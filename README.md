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
