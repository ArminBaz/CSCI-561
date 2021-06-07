'''
    Name: Armin Bazarjani
    Course: CSCI-561 Foundations of Artificial Intelligence
    Date: October 4, 2020
    
    Homework 2: Reinforcement Learning for the Game of "Little-GO"
'''
import os
#input_file = "input.txt"
test_input = "test_input.txt"

class Board:
    # to intialize the game board all we need is the size N
    def __init__(self, N):
        self.size = N
        self.komi = N/2
        self.board_history = 0
    
    # function built to read in input.txt and update the previous and current boards
    def read_input(self, file_name):
        input_info = list()
        with open(file_name, 'r') as F:
            for line in F.readlines():
                input_info.append(line.strip())

        self.board_history += 1

        # if we have a history of more than 3 boards
        if self.board_history >= 3:
            self.color = int(input_info[0])
            self.third_prev_board = self.prev_board
            self.prev_board = [[int(val) for val in line] for line in input_info[1:self.size+1]]
            self.board = [[int(val) for val in line] for line in input_info[self.size+1: 2*self.size+1]]

        else:
            self.color = int(input_info[0])
            self.prev_board = [[int(val) for val in line] for line in input_info[1:self.size+1]]
            self.board = [[int(val) for val in line] for line in input_info[self.size+1: 2*self.size+1]]
    
    def heuristic(self, board, color)
        player = 0
        opponent = 0
        eval_player=0
        eval_opponent=0

        for i in range(5):
            for j in range(5):
                if board[i][j] == self.side:
                    player = player + 1
                    libp = find_liberty(board, i, j)
                    eval_player += player + libp

                elif board[i][j] == 3 - self.side:
                    opponent = opponent + 1
                    libo = find_liberty(board, i, j)
                    eval_opponent += opponent + libo

        final_eval = eval_player - eval_opponent
        if color == self.side:
            return final_eval
        return -1 * final_eval
    
    #Function to find how many opponent tiles will die if a tile is placed in a position
    # MODIFY
    def find_dead_tiles(self, board, tile_type):
        dead_tiles = []
        for i in range(5):
            for j in range(5):
                if board[i][j] == tile_type:
                    if not find_liberty(board, i, j):
                        dead_tiles.append((i, j))
        return dead_tiles

    # Remove the dead tiles to form the next board state for the min-max algorithm.
    # MODIFY
    def remove_dead_tiles(self, board, tile_type):
        dead_tiles = find_dead_tiles(board, tile_type)
        if not dead_tiles:
            return board
        new_board = remove_certain_tiles(board, dead_tiles)
        return new_board
    
    # Remove the dead tiles to form the next board state for the min-max algorithm.
    # MODIFY
    def remove_dead_tiles(self, board, tile_type):
        dead_tiles = find_dead_tiles(board, tile_type)
        if not dead_tiles:
            return board
        new_board = remove_certain_tiles(board, dead_tiles)
        return new_board

    # Sets the postion on the board to empty (zero)
    # MODIFY
    def remove_certain_tiles(self, board, locations):
        for tile in locations:
            board[tile[0]][tile[1]] = 0
        return board
    
    # function that simply returns adjacent stones
    def find_adjacent_stones(self, pos):
        neighboring = [(pos[0] - 1, pos[1]),
                    (pos[0] + 1, pos[1]),
                    (pos[0], pos[1] - 1),
                    (pos[0], pos[1] + 1)]
        return ([point for point in neighboring if 0 <= point[0] < self.size and 0 <= point[1] < self.size])
    
    # Function that returns list of all adjacent ally stones given another stones position
    def find_ally_neighbors(self, pos):
        neighboring = [(pos[0] - 1, pos[1]),
                    (pos[0] + 1, pos[1]),
                    (pos[0], pos[1] - 1),
                    (pos[0], pos[1] + 1)]
        return ([point for point in neighboring if 0 <= point[0] < self.size and 0 <= point[1] < self.size 
                                            and self.board[point[0]][point[1]] == self.color])
    
    # function that returns ally cluster of a point Implemented using BFS and above function
    # returns a list of ally cluster given a certain point on the board
    def find_ally_cluster(self, pos):
        # initialize queue and explored
        queue = list()
        cluster = list()
        cluster.append(pos)

        # push the first neighbor into the queue (just the start node)
        queue.append(pos)
        
        while queue:
            node = queue.pop(0)

            neighbors = self.find_ally_neighbors(node)
            # if ally nieghbors not empty, add them to cluster_dict
            for neighbor in neighbors:
                if neighbor not in cluster:
                    cluster.append(neighbor)
                    queue.append(neighbor)
                else:
                    continue
        
        return cluster

    # function that determines if a given cluster has liberty
    # returns true or false when given a list that signifies a cluster
    def cluster_liberty(self, cluster):
        # loop through each point in the cluster
        for point in cluster:
            # if the point has an adjacent node with a value of 0, then the cluster has liberty
            for neighbor in self.find_adjacent_stones(point):
                if self.board[neighbor[0]][neighbor[1]] == 0:
                    return True
        
        # if we have looped through all the points and all the neighbors and have not found an
        # empty adjacent node, the cluster does not have liberty
        return False
    
    # return a list of valid moves given current gameboard position
    def find_valid_moves(self):
        valid_moves = list()
        # loop through the entire gameboard
        for i in range(self.size):
            for j in range(self.size):
                # position that has a 0 is empty
                if self.board[i][j] == 0:
                    # find ally cluster of position
                    ally_cluster = self.find_ally_cluster((i,j))
                    # if cluster has liberty, add position to valid_moves list
                    if self.cluster_liberty(ally_cluster):
                        # add point to valid moves list
                        valid_moves.append((i,j))
        
        return valid_moves

        
# TEST
'''
if __name__ == "__main__":
    board = Board(5)
    board.read_input(test_input)
    #neighbors = board.find_ally_neighbors((0,3))
    #print(neighbors)
    cluster = board.find_ally_cluster((3,3))
    print(cluster)
    print(board.cluster_liberty(cluster))
    moves = board.find_valid_moves()
    print(moves)
'''