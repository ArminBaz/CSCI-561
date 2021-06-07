import random
import copy
import time
#Get the current board state 
start = time.time()
f = open("test_input.txt")
f2 = open("output.txt", "w+")
f1 = f.readlines()
#Get the player your AI agent should play as (Black or white)
color = int(f1[0].strip())

prevb = []
curb = []
#convert the input state to matrix
#first 5 rows is the previous board state this is used to check the violation of the KO rule
for i in [1, 2, 3, 4, 5]:
    prev = f1[i].strip()
    pr = [int(d) for d in prev]
    prevb.append(pr)
#last 5 rows is the current board state which the agent will play on    
for i in [6, 7, 8, 9, 10]:
    cur = f1[i].strip()
    cr = [int(d) for d in cur]
    curb.append(cr)
#Describe a heuristic that will give rewards based on the number of tiles of the player vs opponent on the board along with the liberties of the tiles.
def evaluate(board, np):
    pl = 0
    op = 0
    ev_pl=0
    ev_op=0
    for r in range(5):
        for j in range(5):
            if board[r][j] == color:
                pl = pl + 1
                libp = find_liberty(board, r, j)
                ev_pl = ev_pl+pl + libp
            elif board[r][j] == 3 - color:
                op = op + 1
                libo = find_liberty(board, r, j)
                ev_op = ev_op+op + libo

    ev = ev_pl - ev_op
    if np == color:
        return ev
    return -1 * ev

#Function to find how many opponent tiles will die if a tile is placed in a position
def find_dead_tiles(board, tile_type):
    dead_tiles = []
    for i in range(5):
        for j in range(5):
            if board[i][j] == tile_type:
                if not find_liberty(board, i, j):
                    dead_tiles.append((i, j))
    return dead_tiles

#Remove the dead tiles to form the next board state for the min-max algorithm.
def remove_dead_tiles(board, tile_type):
    dead_tiles = find_dead_tiles(board, tile_type)
    if not dead_tiles:
        return board
    new_board = remove_certain_tiles(board, dead_tiles)
    return new_board

#Sets the postion on the board to empty (zero)
def remove_certain_tiles(board, locations):
    for tile in locations:
        board[tile[0]][tile[1]] = 0
    return board

#Returns the ally members of a particular tile in a particular postion
def ally_dfs(board, i, j):
    pos = (i,j)
    arr = [(i, j)]
    ally_members = []
    while arr:
        piece = arr.pop()
        ally_members.append(piece)
        neighbor_allies = detect_neighbor_ally(board, piece[0], piece[1])
        for ally in neighbor_allies:
            if ally not in arr and ally not in ally_members:
                arr.append(ally)
    return ally_members

#Finds the 4 neighbours of a tile in position(i,j) on the board
def detect_neighbor(board, i, j):
    neighbors = []
    board = remove_dead_tiles(board, (i, j))
    if i > 0:
        neighbors.append((i - 1, j))
    if i < len(board) - 1:
        neighbors.append((i + 1, j))
    if j > 0:
        neighbors.append((i, j - 1))
    if j < len(board) - 1:
        neighbors.append((i, j + 1))
    return neighbors

#From the neighbours of a tile we check which of these are allys of our tile by seeing if their colour is the same (i.e 1 for black and 2 for white)
def detect_neighbor_ally(board, r, c):
    neighbors = detect_neighbor(board, r, c)
    group_allies = []

    for piece in neighbors:

        if board[piece[0]][piece[1]] == board[r][c]:
            group_allies.append(piece)
    return group_allies

#Checks if we can place and how many empty places we can place our tile by chceking the allies.
def find_liberty(board, row, col):
    count = 0

    ally_members = ally_dfs(board, row, col)
    for member in ally_members:
        neighbors = detect_neighbor(board, member[0], member[1])
        for tile in neighbors:

            if board[tile[0]][tile[1]] == 0:
                count = count + 1
    return count

#Returns if the position(row,col) is occupied or not on the board
def get(board, row, col):
    if board[row][col] == 0:
        return None
    else:
        return 1

#Checks if valid move by seeing if all the criteras like liberty, ko rule being satisfied.
def is_valid_move(board, row, col, pl, prboard):
    board2 = copy.deepcopy(board)
    board2[row][col] = pl
    died_pieces = find_dead_tiles(board2, 3 - pl)
    board2 = remove_dead_tiles(board2, 3 - pl)
    if get(board, row, col) is None and find_liberty(board2, row, col) >= 1 and not (
            died_pieces and ko_violation(prboard, board2)):
        return True

#Function that checks if KO rule is satisfied.
def ko_violation(prboard, board):
    for r in range(5):
        for c in range(5):
            if board[r][c] != prboard[r][c]:
                return False
    return True

#Returns all the valid positions tile can be placed in the current board state
def legal_moves(board, pl, prboard):
    moves = []
    for row in range(5):
        for col in range(5):
            if is_valid_move(board, row, col, pl, prboard):
                moves.append((row, col))
    return moves

# Main min-max function
def minmax(game_state, max_depth, tile, prvboard):
    best_moves = []
    best_score = None
    alpha = -1000
    beta = -1000
    game_state2 = copy.deepcopy(game_state)
    prvboard2 = copy.deepcopy(prvboard)
    next_state = copy.deepcopy(game_state)

    f = 1

    for possible_move in legal_moves(game_state, tile, prvboard2):

        f = f + 1
        prvboard2 = copy.deepcopy(next_state)

        next_state[possible_move[0]][possible_move[1]] = tile
        next_state = remove_dead_tiles(next_state, 3 - tile)
        ev = evaluate(next_state, next_player(tile))

        evaluation = minmax2(next_state, max_depth, alpha, beta, ev, next_player(tile), prvboard2)

        next_state = copy.deepcopy(game_state2)
        our_best_outcome = -1 * evaluation
        if (not best_moves) or our_best_outcome > best_score:

            best_moves = [possible_move]
            best_score = our_best_outcome

            alpha = best_score

        elif our_best_outcome == best_score:

            best_moves.append(possible_move)
    return best_moves


def minmax2(board, max_depth, alpha, beta, ev, np, prvboard):
    if max_depth == 0:
        return ev
    best_so_far = ev
    game_state2 = copy.deepcopy(board)
    prvboard2 = copy.deepcopy(prvboard)
    next_state = copy.deepcopy(board)

    for possible_move in legal_moves(board, np, prvboard2):

        prvboard2 = copy.deepcopy(next_state)

        next_state[possible_move[0]][possible_move[1]] = np
        next_state = remove_dead_tiles(next_state, 3 - np)

        ev = evaluate(next_state, next_player(np))

        evaluation = minmax2(next_state, max_depth - 1, alpha, beta, ev, next_player(np), prvboard2)

        next_state = copy.deepcopy(game_state2)

        our_result = -1 * evaluation
        if our_result > best_so_far:
            best_so_far = our_result
        if np == 3 - color:
            if best_so_far > beta:
                beta = best_so_far

            outcome_for_player = -1 * best_so_far
            if outcome_for_player < alpha:
                return best_so_far
        elif np == color:
            if best_so_far > alpha:
                alpha = best_so_far

            outcome_for_opp = -1 * best_so_far
            if outcome_for_opp < beta:
                return best_so_far

    return best_so_far


def next_player(tile):
    if tile == 2:
        return 1
    if tile == 1:
        return 2

#Main function that returns the best move for our player based on the current board state, previous board state and if player is black or white.
def findBestMove(board, prboard):
    movVal = minmax(board, 2, color, prboard)
    return movVal
   
numb=0
for r in range(5):
    for c in range(5):
        if curb[r][c] != 0:
                numb = numb + 1
#hard code the first move for the black player since it gets to start first
if numb==0 and color==1:
    a=[(2,2)]
#Return best moves and if more than one best move then selct one randomly. If no moves remaining then return PASS
else:
    a = findBestMove(curb, prevb)
    print(a)
    
if a == []:

    f2.write("PASS")
else:
    rand_best = random.choice(a)
    f2.write("%d%s%d" % (rand_best[0], ",", rand_best[1]))
end = time.time()
print(f'total time of evaluation: {end-start}')