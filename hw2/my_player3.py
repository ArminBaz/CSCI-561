'''
    Name: Armin Bazarjani
    Course: CSCI-561 Foundations of Artificial Intelligence
    Date: October 4, 2020
    
    Homework 2: Reinforcement Learning for the Game of "Little-GO"
'''
import os
import copy
import time
import random

# define all the constant variables
BOARD_SIZE = 5
INPUT = 'test_input.txt'
OUTPUT = 'output.txt'
test_input = "test_input.txt"

# function built to read in input.txt and update the previous and current boards
def read_input(input_file):
    input_info = list()
    with open(input_file, 'r') as F:
        for line in F.readlines():
            input_info.append(line.strip())

    color = int(input_info[0])
    prev_board = [[int(val) for val in line] for line in input_info[1:BOARD_SIZE+1]]
    board = [[int(val) for val in line] for line in input_info[BOARD_SIZE+1: 2*BOARD_SIZE+1]]

    return color, board, prev_board

# function that writes output file
def write_output(output_file, move):
    with open(output_file, 'w') as F:
        if move == 'PASS':
            F.write(move)
        else:
           F.write(str(move[0])+','+str(move[1]))

def heuristic(board, np):
    player, opponent, heur_player, heur_opponent = 0, 0, 0, 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == color:
                player += 1
                heur_player += (player + cluster_liberty(board, i, j))
            elif board[i][j] == 3 - color:
                opponent += 1
                heur_opponent += (opponent + cluster_liberty(board, i, j))

    if np == color:
        return heur_player - heur_opponent
    return heur_opponent - heur_player

# finds dead stones given stone color
def find_dead_stones(board, color):
    dead_stones = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == color:
                if not cluster_liberty(board, i, j) and (i,j) not in dead_stones:
                    dead_stones.append((i, j))
    return dead_stones

# helper function for removing dead stones
def remove_stones(board, locs):
    for stone in locs:
        board[stone[0]][stone[1]] = 0
    return board

# given stone color, removes dead stones
def remove_dead_stones(board, color):
    dead_stones = find_dead_stones(board, color)
    if not dead_stones:
        return board
    new_board = remove_stones(board, dead_stones)
    return new_board

# function that removes dead stones and returns adjacent stones within gameboard range
def find_adjacent_stones(board, row, col):
    board = remove_dead_stones(board, (row, col))
    neighboring = [(row - 1, col),
                (row + 1, col),
                (row, col - 1),
                (row, col + 1)]
    return ([point for point in neighboring if 0 <= point[0] < BOARD_SIZE and 0 <= point[1] < BOARD_SIZE])

# Function that returns list of all adjacent ally stones given another stones position
def find_ally_neighbors(board, row, col):
    allies = list()
    for point in find_adjacent_stones(board, row, col):
        if board[point[0]][point[1]] == board[row][col]:
            allies.append(point)

    return allies

# function that returns ally cluster of a point Implemented using BFS and above function
# returns a list of ally cluster given a certain point on the board
def find_ally_cluster(board, row, col):
    # initialize queue and explored
    queue = [(row, col)]
    cluster = list()
    
    while queue:
        node = queue.pop(0)
        cluster.append(node)
        # if ally nieghbors not empty, add them to cluster_dict
        for neighbor in find_ally_neighbors(board, node[0], node[1]):
            if neighbor not in queue and neighbor not in cluster:
                queue.append(neighbor)
    return cluster

# function that determines if a given cluster has liberty
# returns true or false when given a list that signifies a cluster
def cluster_liberty(board, row, col):
    count = 0
    # loop through each point in the cluster
    for point in find_ally_cluster(board, row, col):
        # if the point has an adjacent node with a value of 0, then the cluster has liberty
        for neighbor in find_adjacent_stones(board,  point[0], point[1]):
            if board[neighbor[0]][neighbor[1]] == 0:
                count += 1

    return count

# function that checks if KO or not
def ko_(prev_board, board):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != prev_board[i][j]:
                return False
    return True

def good_move(board, prev_board, player, row, col):
    if board[row][col] != 0:
        return False
    board_copy = copy.deepcopy(board)
    board_copy[row][col] = player
    dead_pieces = find_dead_stones(board_copy, 3 - player)
    board_copy = remove_dead_stones(board_copy, 3 - player)
    # find ally cluster of position
    # if cluster has liberty, add position to valid_moves list
    if cluster_liberty(board_copy, row, col) >= 1 and not (dead_pieces and ko_(prev_board, board_copy)):
        # add point to valid moves list
        return True


# return a list of valid moves given current gameboard position
def find_valid_moves(board, prev_board, player):
    valid_moves = list()
    # loop through the entire gameboard
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            # position that has a 0 is empty
            if good_move(board, prev_board, player, i, j) == True:
                valid_moves.append((i,j))
    return valid_moves

# the main minimax function
def minmax(curr_state, prev_state, max_depth, alpha, beta, color):
    # intialize helper variables
    moves = list()
    best = 0
    #game_state_copy = copy.deepcopy(game_state)
    #next_state = copy.deepcopy(curr_state)
    curr_state_copy = copy.deepcopy(curr_state)

    # iterate through all valid moves
    for move in find_valid_moves(curr_state, prev_state, color):
        # update the next state board
        next_state = copy.deepcopy(curr_state)
        next_state[move[0]][move[1]] = color
        next_state = remove_dead_stones(next_state, 3-color)

        # get heuristic of next state
        heur = heuristic(next_state, 3-color)
        evaluation = minmax_help(next_state, curr_state_copy, max_depth, 
                                    alpha, beta, heur, 3-color)

        curr_score = -1 * evaluation

        # check if moves is empty or if we have new best move(s)
        if curr_score > best or not moves:
            best = curr_score
            alpha = best
            moves = [move]
        # if we have another best move then we add to the moves list
        elif curr_score == best:
            moves.append(move)

    return moves

# the second minimax 'helper' function that iterates through the branches
def minmax_help(curr_state, prev_state, max_depth, alpha, beta, heur, next_player):
    if max_depth == 0:
        return heur
    best = heur

    curr_state_copy = copy.deepcopy(curr_state)
    # iterate through all valid moves
    for move in find_valid_moves(curr_state, prev_state, next_player):
        # update the next board state
        next_state = copy.deepcopy(curr_state)
        next_state[move[0]][move[1]] = next_player
        next_state = remove_dead_stones(next_state, 3-next_player)

        # get heuristic of next state
        heur = heuristic(next_state, 3-next_player)
        evaluation = minmax_help(next_state, curr_state_copy, max_depth - 1, 
                                    alpha, beta, heur, 3-next_player)

        curr_score = -1 * evaluation
        # check if new result is better than current best
        if curr_score > best:
            best = curr_score
        # update the score
        new_score = -1 * best

        # Alpha beta pruning
        # if we are looking at the minimizing player (opponent)
        if next_player == 3-color:
            player = new_score
            # check if prune
            if player < alpha:
                return best
            # if we dont prune, update beta
            if best > beta:
                beta = best
        # if we are looking at the maximizing player (ourselves)
        elif next_player == color:
            opponent = new_score
            # check prune
            if opponent < beta:
                return best
            # if we dont prune, update alpha
            if best > alpha:
                alpha = best

    return best

start = time.time()
color, cur_board, pre_board = read_input(INPUT)

checker=0
checker_bool = False
for i in range(5):
    for j in range(5):
        if cur_board[i][j] != 0:
            if i == 2 and j == 2:
                checker_bool = True
            checker += 1

if (checker==0 and color==1) or (checker==1 and color==2 and checker_bool is False):
    action = [(2,2)]
else:
    action = minmax(cur_board, pre_board, 2, -1000, -1000, color)
    print(action)
# if empty list, then no action, choose to pass
if action == []:
    rand_action = ['PASS']
# else choose a random action from the list
else:
    rand_action = random.choice(action)

write_output(OUTPUT, rand_action)
end = time.time()
print(f'total time of evaluation: {end-start}')