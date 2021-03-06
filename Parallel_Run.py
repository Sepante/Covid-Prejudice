import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from simulate import simulate
import multiprocessing as mp
from connectivity_calc import connectivity_calc
import time
from pathlib import Path
from df_summarizer import df_summarizer

#### setup
timed_output = True
summarized_time_output = True
data_input = 'generate' #read-generate
data_title = 'Chicago'
data_dir = 'empirical_input/' + data_title + '/'
#data_input = 'generate'

run_number = 1
N = 10000
social_class_num = 2
k = 40
#seg_frac = 0 #between 1 and zero
#np.random.seed(0)
#recovery_prob = 0.025
transmit_prob_seq = [0.00025]
#transmit_prob_seq = [1]

recovery_prob = 0.003

#Game Theory Model
learning_rate = 1
beta = 10


infection_reward = -20
stay_home_reward = np.array([-0.9, -1.5, -3, -1.2]) #W - B - A - L




#health : 0 -> suceptible
#health > 0 -> number of days after infection
#health : -1 -> recovered (removed)
#future -> health in the next step (necessary for parallel updating)
#strategy -> going out or not
#social class -> 0, 1, 2 respectively low, medium and high economic class

jobs = []
#seg_frac_seq = np.arange( 0, 1, 0.2 )
#transmit_prob_seq = np.arange( 0.2, 1, 0.1 )
#seg_frac_seq = [0, 0.5, 0.8]
#transmit_prob_seq = [ 0.2, 0.4, 0.6, 0.8 ]
seg_frac_seq = [ 0.2, 0.6, 0.8, 0.9 ]

uniform_reside = 0

if data_input == 'generate':
    for seg_frac in seg_frac_seq:
        sizes, probs = connectivity_calc(N, social_class_num, seg_frac, k)
        for transmit_prob in transmit_prob_seq:
            args = (sizes, probs, seg_frac, social_class_num, beta, stay_home_reward, infection_reward\
                    , learning_rate, transmit_prob, recovery_prob, uniform_reside, timed_output)    
            
            for run in range(run_number):
                jobs.append( ( args + (np.random.randint(10000000),) ) )
elif data_input == 'read':
    
    seg_frac = data_title
    sizes = np.array( pd.read_csv(data_dir + 'Population_fraction.csv') )[0]
    
    social_class_num = len(sizes)
    
    sizes = sizes / sizes.sum() * N
    sizes = sizes.astype('int')
    
    probs = np.array( pd.read_csv(data_dir + 'P_norm_adj.csv', index_col = 0) )
    
    Rewards_pd = pd.read_csv(data_dir + 'Rewards.csv')
    infection_reward = float( Rewards_pd['Covid'] )
    stay_home_reward = np.array( Rewards_pd.iloc[0] )[ :-1 ]
    #print(probs)
    for transmit_prob in transmit_prob_seq:
        args = (sizes, probs, seg_frac, social_class_num, beta, stay_home_reward, infection_reward\
            , learning_rate, transmit_prob, recovery_prob, uniform_reside, timed_output)    
            
    for run in range(run_number):
        jobs.append( ( args + (np.random.randint(10000000),) ) )

    
#print('Jobs Done!')
##adding the random seeds.
#jobs = [ ( args + (np.random.randint(10000000),) )  for i in range(run_number)]


start_time = time.time()

processor_num = mp.cpu_count()

print( 'processor_num=', str(processor_num) )

with mp.Pool( processor_num ) as pool:
    p_r = pool.map_async(simulate, jobs)
    res = p_r.get()
elapsed_time = time.time() - start_time

print('elapsed time = ', elapsed_time)
#rand_string = str(np.random.randint(100000000))
rand_string = str(time.gmtime()[:7]).replace('(', '').replace(')', '').replace(', ', '')

target_dir = "Results/"
Path( target_dir ).mkdir(parents=True, exist_ok=True)

if timed_output:
    timed_results_params_with_index = ['realization', 't']
    classes = ([ 'class_' + str(i) for i in range(social_class_num) ])
    timed_results_params_with_index.extend(classes)
    
    timed_results_params_titles = ['transmit_prob', 'seg_frac', 'recovery_prob'\
           , 'infection_reward', 'beta']
        
    timed_results_params_with_index.extend( timed_results_params_titles )
        
    max_steps = len( res[-1][1] )
    
    timed_results = pd.DataFrame( np.zeros(( max_steps * len(jobs)\
        , len(timed_results_params_with_index) ), int) )
    timed_results.columns = timed_results_params_with_index
    
    for i in range(len(res)):
        params_for_timed_output, result, _ = res[i]
        
        print(params_for_timed_output)
        begin, end = max_steps * i, max_steps * (i+1) - 1 
        
        timed_results.loc[begin : end , 'realization'] = i
        timed_results.loc[begin : end , 't'] = list(range(max_steps))
        timed_results.loc[begin : end, classes]  = result
        
        for p_i, param in enumerate( timed_results_params_titles ):
            timed_results.loc[begin : end , param] = params_for_timed_output[p_i]
        
    id_string = 'timed=' + str(stay_home_reward) + '-infect_rew='  \
    + str(infection_reward) + '-recov =' + str(recovery_prob) + '-' + rand_string + '.csv'        
    timed_results.to_csv(target_dir + id_string, index = False)
    
    if summarized_time_output:
        
#        params_and_time = list( set().union( timed_results_params_titles, ['t'] ) )
#        summarized_timed_results = timed_results.groupby( params_and_time ).mean().reset_index().drop('realization', 1)
#        timed_std = timed_results.groupby( params_and_time ).std().reset_index().drop('realization', 1)
#        
#        for soc_class in classes:
#            summarized_timed_results[ soc_class + '_err'] = timed_std[ soc_class ] / np.sqrt( run_number )
#            
        
        summarized_timed_results = df_summarizer(df = timed_results\
         , outputs = classes, mean_over = 'realization')
        summarized_timed_results.to_csv(target_dir + 'summarized-' + id_string, index = False)



#    params_titles = ['transmit_prob', 'segregation', 'SES_dispar', 'size_dispar', 'uniform_reside' ]
params_titles = ['transmit_prob', 'seg_frac', 'recovery_prob'\
       , 'infection_reward', 'beta']
results = pd.DataFrame( np.zeros(( len(jobs) , social_class_num + len(params_titles)), int) )
results.columns = params_titles + ['class_'+str(i) for i in range(social_class_num) ]

#results[:] = res    

for i in range(len(res)):
    params_for_timed_output, _, result = res[i]
    for p_i, param in enumerate( params_titles ):
        results.loc[i , param] = params_for_timed_output[p_i]
        
    results.loc[i, classes]  = result


id_string = 'rewards=' + str(stay_home_reward) + '-infect_rew='  \
    + str(infection_reward) + '-recov =' + str(recovery_prob) + '-' + rand_string + '.csv'        
results.to_csv(target_dir + id_string, index = False)

summarized_results = df_summarizer(df = results\
     , outputs = classes, mean_over = False)

print(id_string)
