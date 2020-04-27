import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib
from matplotlib import gridspec
matplotlib.rcParams.update({'font.size': 15})
import networkx as nx

from main import *
do_animate = True
graph_type = 'erdos'
#eps = -0.25
pos = {}
if graph_type == 'erdos':
    pos = nx.circular_layout(G)
    True
elif graph_type == 'grid':
    #pos = nx.circular_layout(G)
    dist = 1 / L
    for i in G.nodes():
        x = i % L
        y = int( i / L )
        pos[i] = np.array([ x * dist, y * dist ])# + np.array( [eps , eps] )

pos_array = np.array( list( pos.values() ) )

#node_size = 80000

#fig, axes= plt.subplots(1,2, figsize=(5,5))s
#fig.subplots_adjust(wspace = 0)
#ax, ay = axes
figure_ratio = 1
fig = plt.figure(figsize=(5*(1+figure_ratio), 5 ) )
fig.subplots_adjust(wspace = 0)
gs = gridspec.GridSpec(1, 2, width_ratios=[1, figure_ratio]) 
ax = plt.subplot(gs[0])
#ax0.plot(x, y)
ay = plt.subplot(gs[1])
#ay.plot(y, x)
color_code = [ 'blue', 'red', 'green' ]
shape_code = [ 's', 'o', '^' ]
def display_city(create_legend = True):
    alpha = 0.8
    for social_class in range( social_class_num ):
        #print('so: ', social_class)
        this_class_agents = (agents['social_class'] == social_class)
        #print('so: ', social_class)
        for health_status in range(-1, 2 ):
            this_health_status = (np.sign( agents['health'] ) == health_status)

            this_subgroup = np.all( [ this_class_agents, this_health_status ], axis = 0 )

            this_subgroup_list = np.where(this_subgroup)[0]
            #print('so: ', social_class)
            if (len(this_subgroup_list)):
                nx.draw_networkx_nodes(G,pos = pos, ax = ax, nodelist=list(this_subgroup_list),  node_color = color_code[health_status], node_shape = shape_code[social_class], alpha = alpha, edgecolors = 'r')
                #nx.draw_networkx_nodes(G,pos = pos, ax = ax, nodelist=np.array([1,2]),  node_color = 'r', node_shape = 'o', alpha = alpha, edgecolors = 'r')
    
    leavers = list( np.where(agents['strategy'] == 1)[0] )
    visible_edges = [edge for edge in G.edges() if( edge[0] in leavers  and edge[1] in leavers) ]
    invisible_edges = [edge for edge in G.edges() if not ( edge[0] in leavers  and edge[1] in leavers) ]
    
    nx.draw_networkx_edges(G,pos = pos, ax = ax, alpha = alpha/2, width = 2.3, edge_color = 'black', edgelist = visible_edges)
    nx.draw_networkx_edges(G,pos = pos, ax = ax, alpha = alpha/4, width = 1 ,edge_color = 'black', edgelist = invisible_edges)
    
    stayers = list( np.where(agents['strategy'] == 0)[0] )
    stayers_pos = pos_array[stayers]
    x = stayers_pos[:, 0]
    y = stayers_pos[:, 1]

    ax.scatter(x, y, s = 2000, facecolors='none', edgecolors='r', linewidth = 2.8)

    
    
    ax.axis('off')
    
    ax.set_ylim( np.array( list( pos.values() ) ).min()*1.2  - 0.1, np.array( list( pos.values() ) ).max()*1.2 )
    ax.set_xlim( np.array( list( pos.values() ) ).min()*1.2  - 0.1, np.array( list( pos.values() ) ).max()*1.2 )
    #ax.scatter(x, y, s = 2000, facecolors='none', edgecolors='r', linewidth = 2.8)
    #nx.draw_networkx_labels(G,pos , ax = ax, font_size=16)
    if create_legend:
        ay.axis('off')
        legend_elements = [
                       Line2D([0], [0], marker='o', color='w', markeredgecolor='blue', label='Susceptible',
                              markerfacecolor='b', markersize=10, alpha = alpha),
                              
                       Line2D([0], [0], marker='o', color='w', markeredgecolor='red', label='Infectious',
                              markerfacecolor='red', markersize=10, alpha = alpha),
                              
                       Line2D([0], [0], marker='o', color='w', markeredgecolor='g', label='Removed',
                              markerfacecolor='g', markersize=10, alpha = alpha),

                              
                       Line2D([0], [0], marker='s', color='w', markeredgecolor='black', label='Lower Class',
                              markerfacecolor='white', markersize=12, alpha = alpha),
                       Line2D([0], [0], marker='o', color='w', markeredgecolor='black', label='Middle Class',
                              markerfacecolor='white', markersize=12, alpha = alpha),
                       Line2D([0], [0], marker='^', color='w', markeredgecolor='black', label='Upper Class',
                              markerfacecolor='white', markersize=12, alpha = alpha),
                       Line2D([0], [0], marker='o', color='w', linewidth = 2, markeredgecolor='red', label='Staying at Home',
                              markerfacecolor='white', markersize=20, alpha = alpha),
                       #Patch(facecolor='white', linewidth = 2, edgecolor='r',
                         #label='Color Patch')


    ]
        ay.legend( handles=legend_elements, loc = 'lower center' )
        #ay.legend(handles = legend_elements, bbox_to_anchor=(0.5, 0.5))#,
        #   bbox_transform=plt.gcf().transFigure)
    #plt.show()
    print( 'healthies = ', np.sum(agents['health'] == 0) )
    return fig

def display_candidates( movers ):
    movers_list = list( movers )
    movers_pos = pos_array[movers_list]
    x = movers_pos[:, 0]
    y = movers_pos[:, 1]

    ax.scatter(x, y, s = 2000, facecolors='none', edgecolors='r', linewidth = 2.8)
    display_city(create_legend = True)

#display_city()
#G = init_graph()
#init_population(0.5, 0.5, 0.5)
#movers = ()

#display_city()

print(agents['health'] == 0)
prediction = 1
pred = 1
animation_phases = 3
def animate(t):
    global pred
    print('animate says = ',pred)
    if t == 0:
        pred = 1
    ay.clear()
    num_string = str( int( t ) )
    #ay.set_title("$t$ ="+ num_string)
    ay.text(0.4 , 0.7 , "$t$ ="+ num_string )
    print(t)
    
    ax.clear()
    display_city()
    if t>0:
        infected_num = infect(G, agents, transmit_prob) #nodes infect their neighbors
        newly_recovered = recover(agents, recovery_prob) #nodes get recovered
        update_infection(agents) #actually change the health statuses (necessary for parallel updating) 
        pred = predict_infected_num(agents, pred, learning_rate) #predict the number of upcoming infected agents for the next step
        survivor_num = update_strategy(agents, exp_stay_home_reward, pred * infection_reward, beta) #update strategies (going out and staying in)
    
    
    return fig

#"""
location = "./"
if do_animate:
#    ani = animation.FuncAnimation(fig, animate, save_count = 40)
#
#    dpi = 100
#    file_name = location + str(time.gmtime()[0:5]) + '.GIF'
#    ani.save( file_name ,dpi=dpi, writer = 'imagemagick')
    #"""

    ani = animation.FuncAnimation(fig, animate, save_count = 10)
    dpi = 200
    writer = animation.writers['ffmpeg'](fps = 1)
    file_name = str(time.gmtime()[0:5]) + '.mp4'
    ani.save( file_name, dpi=dpi, writer = writer)