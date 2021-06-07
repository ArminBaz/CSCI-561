'''
    Name: Armin Bazarjani
    Course: CSCI-561 Foundations of Artificial Intelligence
    Date: September 2, 2020
    
    Homework 1: PathFinding in a 3D Mazes
'''
import time
import os
import math
from queue import PriorityQueue
import filecmp
import heapq

###   Implementation of different search algorithms   ###
def bfs(start, end):
    # initialize queue and explored
    queue = list()
    visited = {}

    # push the first path into the queue (just the start node)
    queue.append((start, None))
    # while there are still values in the queue
    while queue:
        # get the first path from the queue
        node, parent = queue.pop(0)

        # if node is in explored, skip over it
        if node in visited:
            continue
        
        # check if we got to the end
        if node == end:
            visited[node] = (parent)
            return visited
        
        # update visited dict
        visited[node] = (parent)

        # loop through the actions indices
        for action_index in node_actions[node]:
            # use the action to get the neighbor and its hash key
            neighbor = perform_action(node, action_list[action_index])

            # if neighbor not in visted, add it to the queue
            if neighbor not in visited:
                queue.append((neighbor, node))

    # if the queue is empty we want to return a fail
    return 'FAIL'


def ucs(start, end):
    # initialize queue and explored
    explored = {}
    priorityQueue = []
    visited = {}

    # have dictionary at start where you do possible actions 
    # node, parent, cost, depth

    heapq.heappush(priorityQueue, (0, start, None, None)) # (cost, current node, parent node, action taken)

    # while there are still values in the queue
    while priorityQueue:
        # get the first path from the queue
        cost, curr_node, parent_node, action_taken = heapq.heappop(priorityQueue)

        # if it has been seen before AND it had a lower cost, dont keep going
        if (curr_node in visited) and (visited[curr_node][0] < cost):
            continue

        # check if we got to the end
        if curr_node == end:
            visited[curr_node] = (cost, parent_node, action_taken)
            return visited

        # update visited dict
        visited[curr_node] = (cost, parent_node, action_taken)

        # loop through the actions indices
        for action_index in node_actions[curr_node]:
            # use the action to get the neighbor and its hash key
            neighbor = perform_action(curr_node, action_list[action_index])
            neighbor_cost = cost + action_costs[action_index]

            # check if neighbor has been visited OR if it has been visited at a higher cost
            if (neighbor not in visited) or (visited[neighbor][0] > neighbor_cost):
                neighbor_node = (neighbor_cost, neighbor, curr_node, action_index)
                heapq.heappush(priorityQueue, neighbor_node)

    # if the queue is empty return fail
    return 'FAIL'

def astar(start, end):
    # initialize queue and explored
    priorityQueue = []
    visited = {}

    heapq.heappush(priorityQueue, (0, start, None, None, 0)) # (cost, current node, parent node, action taken, parent heuristic)
    # while there are still values in the queue
    while priorityQueue:
        # get the first path from the queue
        cost, curr_node, parent_node, action_taken, parent_h = heapq.heappop(priorityQueue)
        cost = cost - parent_h

        # if it has been seen before AND it had a lower cost, dont keep going
        if (curr_node in visited) and (visited[curr_node][0] < cost):
            continue

        # check if we got to the end
        if curr_node == end:
            visited[curr_node] = (cost, parent_node, action_taken)
            return visited
        
        # update visited dict
        visited[curr_node] = (cost, parent_node, action_taken)
        
        # loop through the actions indices
        for action_index in node_actions[curr_node]:
            # use the action to get the neighbor and its cost
            neighbor = perform_action(curr_node, action_list[action_index])
            neighbor_cost = cost + action_costs[action_index] + heuristic_(neighbor, end)

            if (neighbor not in visited) or (visited[neighbor][0] > neighbor_cost):
                neighbor_node = (neighbor_cost, neighbor, curr_node, action_index, heuristic_(neighbor, end))
                heapq.heappush(priorityQueue, neighbor_node)

    # if the queue is empty return fail
    return 'FAIL'


###   Helpful Functions   ###

# Function that performs the specified action (basically just performs addition on tuples)
def perform_action(current_node, action):

    return (current_node[0] + action[0], current_node[1] + action[1], current_node[2] + action[2])

# takes a space seperated string of integer values as input and returns a tuple of coordinates
def create_node(x, y, z):

    return tuple([int(x), int(y), int(z)])

# heuristic function for A* implementation, returns the rounded distance of two points in a 3d space
def heuristic_euclidean(node1, node2):
    x1 = node1[0]
    y1 = node1[1]
    z1 = node1[2]

    x2 = node2[0]
    y2 = node2[1]
    z2 = node2[2]

    return math.sqrt(((x1-x2)**2) + ((y1-y2)**2) + ((z1-z2)**2))

def heuristic_(node1, node2):
    x1 = node1[0]
    y1 = node1[1]
    z1 = node1[2]

    x2 = node2[0]
    y2 = node2[1]
    z2 = node2[2]

    sums = abs(x1-x2) + abs(y1-y2) + abs(z1-z2)

    return 10 * (sums/2)


###   Main Program   ###
input_file = os.getcwd()+'/test_cases/input6.txt'
test_outfile = os.getcwd()+'/outputs/output6.txt'
#input_file = 'input.txt'
#output_file = 'output.txt'

# the 18 actions that are available
action_list = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1],
            [1,1,0],[1,-1,0],[-1,1,0],[-1,-1,0],[1,0,1],[1,0,-1],
            [-1,0,1],[-1,0,-1],[0,1,1],[0,1,-1],[0,-1,1],[0,-1,-1]]

# the costs the the different 18 actions, vertical = 10, diagonal = 14
action_costs = [10, 10, 10, 10, 10, 10, 14, 14, 14, 14, 14, 14, 14,
                14, 14, 14, 14, 14]

input_info = list()   # list to store information given from input.txt

#state_space = list()    # list that is our state space
node_actions = dict()  # store the available actions for each node

# Parse input file
## TIME ##
start = time.time()
with open(input_file) as F:
	for line in F.readlines():
		input_info.append(line.strip())

# the first 4 lines always define the same things
algorithm = input_info[0]
maze_shape = input_info[1]
start_node_string = input_info[2]
end_node_string = input_info[3]

start_node_split = start_node_string.split()
end_node_split = end_node_string.split()

# Fill in start and end nodes
start_node = create_node(start_node_split[0], start_node_split[1], start_node_split[2])
end_node = create_node(end_node_split[0], end_node_split[1], end_node_split[2])

# loop through the rest of input_info to update the available actions dict
for i in range(5, len(input_info)):
    # get the node and save it into a tuple
    line = input_info[i]
    line_split = line.split()

    node = create_node(line_split[0], line_split[1], line_split[2])

    actions = list()
    # get the available actions for each node
    for j in range(3, len(line_split)):
        action = int(line_split[j])-1
        actions.append(action)

    # fill in actions dictionary
    node_actions[node] = actions

# if statements to run appropriate algorithm
if algorithm == 'BFS':
    print("Running BFS!")
    visited = bfs(start_node, end_node)
elif algorithm == 'UCS':
    print("Running UCS!")
    visited = ucs(start_node, end_node)
elif algorithm == 'A*':
    print("Running A*!")
    visited = astar(start_node, end_node)
end2 = time.time()
print(f'time to run algorithm: {end2-start}')


###   Format Output   ###
def output(visited, goal_node, algorithm):
    cost = 0
    length = 0
    flag = True
    node = goal_node
    node_list = list()
    cost_list = list()

    if algorithm == 'BFS':
        while flag is True:
            if visited[node] is None:
                length += 1
                node_list.insert(0, node)
                cost_list.insert(0, 0)
                flag = False
            else:
                cost += 1
                length += 1
                node_list.insert(0, node)
                cost_list.insert(0, 1)
                node = visited[node]
        # Format output for BFS
        outf = open('output.txt', 'w')
        outf.write(str(cost) + '\n')
        outf.write(str(length) + '\n')
        for i in range(0, len(node_list)):
            if i == (len(node_list)-1):
                yeet = ([str(j) for j in node_list[i]])
                yeet.append(str(cost_list[i]))
                yeet2 = " ".join(yeet)
                outf.write(yeet2)
            else:
                yeet = ([str(j) for j in node_list[i]])
                yeet.append(str(cost_list[i]))
                yeet2 = " ".join(yeet)
                outf.write(yeet2 + '\n')
        outf.close()
    else:
        while flag is True:
            if visited[node][1] is None:
                length += 1
                node_list.insert(0, node)
                cost_list.insert(0, 0)
                flag = False
            else:
                cost += action_costs[visited[node][2]]
                length += 1
                node_list.insert(0, node)
                cost_list.insert(0, action_costs[visited[node][2]])
                node = visited[node][1]
        # Format output into txt file for both UCS and A*
        outf = open('output.txt', 'w')
        outf.write(str(cost) + '\n')
        outf.write(str(length) + '\n')
        for i in range(0, len(node_list)):
            # check if last
            if i == (len(node_list)-1):
                yeet = ([str(j) for j in node_list[i]])
                yeet.append(str(cost_list[i]))
                yeet2 = " ".join(yeet)
                outf.write(yeet2)
            else:
                yeet = ([str(j) for j in node_list[i]])
                yeet.append(str(cost_list[i]))
                yeet2 = " ".join(yeet)
                outf.write(yeet2 + '\n')
        outf.close()
# First check if it's a FAIL
if visited == 'FAIL':
    outf = open('output.txt', 'w')
    outf.write('FAIL')
    outf.close()
else:
    output(visited, end_node, algorithm)

# Compare files (DELETE THIS)
print(filecmp.cmp('output.txt', test_outfile))