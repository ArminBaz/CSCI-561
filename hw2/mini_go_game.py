import random
import copy
import timeit
from random import shuffle


def read_input_file():
    """
    Get current player, previous and current board state from game host
    :return: current player color (1=black, 2=white), previous and current board state
    """
    with open('test_input.txt') as file:
        file_lines = file.readlines()
        stone_type = int(file_lines[0])
        previous_board = [[int(pos) for pos in row.rstrip('\n')] for row in file_lines[1: 6]]
        current_board = [[int(pos) for pos in row.rstrip('\n')] for row in file_lines[6: 11]]
        return stone_type, previous_board, current_board


def write_output_file(next_move, output_file):
    """
    Write calculated next move to output file
    :param next_move: a tuple with row and column position
    :param output_file: file to write output to
    """
    with open(output_file, 'w') as file:
        if next_move != "PASS":
            file.write(str(next_move[0]) + ',' + str(next_move[1]))
        else:
            file.write(next_move)


def find_evaluation_value(current_board, previous_board, board_size, stone_type):
    """
    Calculate evaluation function for given board state and current player
    :param current_board: Current board state
    :param previous_board: Previous board state
    :param board_size: 5 in this case
    :param stone_type: Current player color (1=black, 2=white)
    :return: Evaluation value for current board state and player
    """
    player_stones, adversary_stones, player_liberties, adversary_liberties = 0, 0, 0, 0
    komi = board_size / 2
    input_list = read_input_file()
    player = int(input_list[0])
    for row in range(0, len(current_board)):
        for col in range(0, len(current_board)):
            if current_board[row][col] != 0:
                if current_board[row][col] == player:
                    player_stones = player_stones + 1
                else:
                    adversary_stones = adversary_stones + 1
    player_liberties = len(find_liberties(current_board, previous_board, board_size, player))
    adversary_liberties = len(find_liberties(current_board, previous_board, board_size, 3 - player))
    if player == stone_type:
        return (player_stones + 1 * player_liberties) - (adversary_stones + 2 * adversary_liberties)
    else:
        return - (player_stones + 1 * player_liberties) + (adversary_stones + 2 * adversary_liberties)


def find_all_possible_moves(current_board):
    """
    Find all empty spots on the board
    :param current_board: Current board state
    :return: A list of all unoccupied spots on the board
    """
    all_possible_moves = []
    for row in range(0, len(current_board)):
        for col in range(0, len(current_board)):
            # Find all empty points to play next move
            if current_board[row][col] == 0:
                all_possible_moves.append((row, col))
    return all_possible_moves


def find_connected_friendly_neighbors(row, col, stone_type, board_size, current_board):
    """
    Find all friendly neighbors (stones of same color as current player) connected to each other with no empty spots in between
    :param row: row index of stone position
    :param col: col index of stone position
    :param stone_type: Current player color (1=black, 2=white)
    :param board_size: Size of board. 5 in this case
    :param current_board: Current board state
    :return: List of connected, same stone neighbors
    """
    unvisited_neighbors = [(row, col)]
    connected_neighbors = []
    while unvisited_neighbors:
        current_stone = unvisited_neighbors.pop()
        connected_neighbors.append(current_stone)
        current_friendly_neighbors = find_current_friendly_neighbors(current_board, current_stone, stone_type,
                                                                     board_size)
        for friend in current_friendly_neighbors:
            if friend not in unvisited_neighbors and friend not in connected_neighbors:
                unvisited_neighbors.append(friend)
    return connected_neighbors


def check_liberty_presence(current_board, row, col, stone_type, board_size):
    """
    Check for liberty presence in current board state for current player and position
    :param current_board: Current board state
    :param row: row index of stone position
    :param col: col index of stone position
    :param stone_type: Current player color (1=black, 2=white)
    :param board_size: Size of board. 5 in this case
    :return: List of positions of liberties
    """
    connected_neighbors = find_connected_friendly_neighbors(row, col, stone_type, board_size, current_board)
    liberties = []
    for neighbor in connected_neighbors:
        row = neighbor[0]
        col = neighbor[1]
        all_neighbors = find_all_neighbors(row, col, board_size)
        for stone in all_neighbors:
            if current_board[stone[0]][stone[1]] == 0 and stone not in liberties:
                liberties.append((stone[0], stone[1]))
    return liberties


def find_all_neighbors(row, col, board_size):
    """
    Find neighboring squares for current position
    :param row: row index of stone position
    :param col: col index of stone position
    :param board_size: Size of board. 5 in this case
    :return: List of positions of all neighboring squares for current position
    """
    all_neighbors = []
    if row > 0:
        all_neighbors.append((row - 1, col))
    if row < board_size - 1:
        all_neighbors.append((row + 1, col))
    if col > 0:
        all_neighbors.append((row, col - 1))
    if col < board_size - 1:
        all_neighbors.append((row, col + 1))
    return all_neighbors


def find_current_friendly_neighbors(current_board, current_stone, stone_type, board_size):
    """
    Find positions of friendly neighbors, i.e. same color stones neighboring the current player position
    :param current_board: Current board state
    :param current_stone: Position of current player
    :param stone_type: Current player color (1=black, 2=white)
    :param board_size: Size of board. 5 in this case
    :return: A list of positions of friendly neighbors
    """
    current_friendly_neighbors = []
    row = current_stone[0]
    col = current_stone[1]
    all_neighbors = find_all_neighbors(row, col, board_size)
    for neighbor in all_neighbors:
        row = neighbor[0]
        col = neighbor[1]
        if current_board[row][col] == stone_type and (row, col) not in current_friendly_neighbors:
            current_friendly_neighbors.append((row, col))
    return current_friendly_neighbors


def find_dead_stones(stone_type, current_board, board_size):
    """
    Identify dead stones, i.e. stones with no liberty on the current board given current player color
    :param stone_type: Current player color (1=black, 2=white)
    :param current_board: Current board state
    :param board_size: Size of board. 5 in this case
    :return: A list of positions of dead stones
    """
    dead_stones = []
    for row in range(board_size):
        for col in range(board_size):
            if current_board[row][col] == stone_type:
                liberties = check_liberty_presence(current_board, row, col, stone_type, board_size)
                if not liberties and (row, col) not in dead_stones:
                    dead_stones.append((row, col))
    return dead_stones


def remove_dead_stones(current_board, dead_stones):
    """
    Remove dead stones from the board by marking those positions as empty
    :param current_board: Current board state
    :param dead_stones: A list of positions of dead stones
    :return: Updated board state
    """
    for stone in dead_stones:
        current_board[stone[0]][stone[1]] = 0
    return current_board


def same_board_state_check(current_board, previous_board, board_size):
    """
    Check if board state is the same as the previous board configuration to avoid ko violation
    :param current_board: Current board state
    :param previous_board: Previous board state
    :param board_size: Size of board. 5 in this case
    :return: Boolean indicating if board state is same as before or not
    """
    for row in range(board_size):
        for col in range(board_size):
            if current_board[row][col] != previous_board[row][col]:
                return False
    return True


def find_liberties(current_board, previous_board, board_size, stone_type):
    """
    Find all liberties for the current board state and player
    :param current_board: Current board state
    :param previous_board: Previous board state
    :param board_size: Size of board. 5 in this case
    :param stone_type: Current player color (1=black, 2=white)
    :return: A list of posiitons of all liberties
    """
    all_possible_moves = find_all_possible_moves(current_board)
    liberties = []
    for move in all_possible_moves:
        row = move[0]
        col = move[1]
        current_board_copy = copy.deepcopy(current_board)
        current_board_copy[row][col] = stone_type
        # current_board_copy2 = copy.deepcopy(current_board_copy)
        liberties.append(check_liberty_presence(current_board_copy, row, col, stone_type, board_size))
    all_liberties = [lib for sublist in liberties for lib in sublist]
    return all_liberties


def find_legal_possible_moves(current_board, previous_board, board_size, stone_type):
    """
    Find all positions on the board where the next move can be played without violating Go rules
    :param current_board: Current board state
    :param previous_board: Previous board state
    :param board_size:  Size of board. 5 in this case
    :param stone_type: Current player color (1=black, 2=white)
    :return: A list of all board positions where the next legal move can be made
    """
    all_possible_moves = find_all_possible_moves(current_board)
    legal_possible_moves = []
    for move in all_possible_moves:
        row = move[0]
        col = move[1]
        current_board_copy = copy.deepcopy(current_board)
        current_board_copy[row][col] = stone_type
        current_board_copy2 = copy.deepcopy(current_board_copy)
        liberties = check_liberty_presence(current_board_copy, row, col, stone_type, board_size)
        if not liberties:
            dead_stones = find_dead_stones(3 - stone_type, current_board_copy, board_size)
            if dead_stones:
                current_board_copy = remove_dead_stones(current_board_copy, dead_stones)
            liberties = check_liberty_presence(current_board_copy, row, col, stone_type, board_size)
        if liberties:
            dead_stones = find_dead_stones(3 - stone_type, current_board_copy2, board_size)
            if dead_stones:
                current_board_copy2 = remove_dead_stones(current_board_copy2, dead_stones)
            if dead_stones and same_board_state_check(current_board_copy2, previous_board, board_size):
                print("ko violation!")
            else:
                legal_possible_moves.append(move)
    return legal_possible_moves


def apply_move(current_board, stone_type, move):
    """
    Place the stone on given position
    :param current_board: Current board state
    :param stone_type: Current player color (1=black, 2=white)
    :param move: row, col position of current move
    :return:
    """
    current_board_copy = copy.deepcopy(current_board)
    row = move[0]
    col = move[1]
    current_board_copy[row][col] = stone_type
    return current_board_copy


def alpha_beta_search(board_state, previous_board_state, board_size, n, alpha, beta, stone_type,
                      maximizing_player):
    """
    Use alpha beta search to find next best move using evaluation score
    :param board_state: Current board state
    :param previous_board_state: Previous board state
    :param board_size: Size of board. 5 in this case
    :param n: Depth of alpha-beta search
    :param alpha: Maximum value that maximizer can get
    :param beta: Minimum value that minimizer can get
    :param stone_type: Current player color (1=black, 2=white)
    :param maximizing_player: Boolean to indicate if it is maximizing player's turn or not
    :return: Evaluation value and current best move
    """
    if n == 0:
        return find_evaluation_value(board_state, previous_board_state, board_size, stone_type), None

    legal_possible_moves = find_legal_possible_moves(board_state, previous_board_state, board_size, stone_type)
    shuffle(legal_possible_moves)  # for random ordering of moves

    if not legal_possible_moves:
        current_best_move = ['PASS']
        return 0, current_best_move

    current_best_move = None

    if maximizing_player:
        v = -1000
        for move in legal_possible_moves:
            next_state = apply_move(board_state, stone_type, move)
            dead_stones = find_dead_stones(3 - stone_type, next_state, board_size)
            next_state = remove_dead_stones(next_state, dead_stones)
            abs_score = alpha_beta_search(next_state, board_state, board_size, n - 1, alpha,
                                          beta, 3 - stone_type, False)
            if v < abs_score[0]:
                v = abs_score[0]
                alpha = max(alpha, v)
                current_best_move = [move]
            if alpha >= beta:
                break
        if current_best_move is None:
            return v, None
        return v, current_best_move
    else:
        v = 1000
        for move in legal_possible_moves:
            next_state = apply_move(board_state, stone_type, move)
            dead_stones = find_dead_stones(3 - stone_type, next_state, board_size)
            next_state = remove_dead_stones(next_state, dead_stones)
            abs_score = alpha_beta_search(next_state, board_state, board_size, n - 1, alpha,
                                          beta, 3 - stone_type, True)
            if v > abs_score[0]:
                v = abs_score[0]
                beta = min(beta, v)
                current_best_move = [move]
            if alpha >= beta:
                break
        if current_best_move is None:
            return v, None
        return v, current_best_move


def play_next_move(current_board, previous_board, board_size, stone_type):
    """
    Find what move must be played next
    :param current_board: Current board state
    :param previous_board: Previous board state
    :param board_size: Size of board. 5 in this case
    :param stone_type: Current player color (1=black, 2=white)
    :return: A tuple of row, col position of next mvoe to be played by current player
    """
    legal_moves = find_legal_possible_moves(current_board, previous_board, board_size, stone_type)
    # Set initial move to centre position of board if player is black - Opening game
    if (len(legal_moves) == (board_size*board_size)) and (stone_type == 1):
        next_move = [(2, 2)]
    # Set second move to centre position of board if unoccupied and player is white - Opening moves
    elif (len(legal_moves) == (board_size*board_size)-1) and (stone_type == 2):
        if current_board[2][2]==0:
            next_move = [(2, 2)]
        # Otherwise set it a move that surrounds the black player assuming it has played at 2,2
        else:
            next_move = [random.choice([(2, 3), (2, 1), (1, 2), (3, 2)])]
    else:
        value, next_move = alpha_beta_search(current_board, previous_board, board_size, 2, -1000, 1000, stone_type, True)
    return next_move


def main():
    """
    Main instantiation function to begin the alpha-beta search for finding the next best move
    """
    board_size = 5
    output_file = 'output.txt'
    input_list = read_input_file()
    stone_type = input_list[0]
    previous_board = input_list[1]
    current_board = input_list[2]
    next_move = play_next_move(current_board, previous_board, board_size, stone_type)
    print(next_move)
    write_output_file(next_move[0], output_file)


main()