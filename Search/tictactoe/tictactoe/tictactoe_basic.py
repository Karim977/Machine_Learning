"""
Tic Tac Toe Player
"""

import math
import copy
import random
import time

X = "X"
O = "O"
EMPTY = None
AI=None
x={}
original=None
def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count_O=0
    count_X=0
    count_None=0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j]==O:count_O+=1
            if board[i][j]==X:count_X+=1
            if board[i][j]==EMPTY:count_None+=1
    if count_None==9: return X
    if count_X>count_O: return O
    else: return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions=set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == None:
                actions.add((i,j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        print(action)
        raise NameError('Invalid move')
    modified_board=copy.deepcopy(board)
    modified_board[action[0]][action[1]] = player(board)
    return modified_board



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    lst=['X','O']
    for i in range(len(board)):
        if board[i][0]==board[i][1]==board[i][2] and board[i][2] in lst:
            return board[i][0]
        if board[0][i]==board[1][i]==board[2][i] and board[2][i] in lst:
            return board[0][i]
    if board[0][0]==board[1][1]==board[2][2] and board[0][0] in lst :
        return board[0][0]
    if board[0][2]==board[1][1]==board[2][0] and board[0][2] in lst :
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is None:
        for row in board:
            for j in row:
                if j == None : return False
        return True
    else: return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if (winner(board))==O:
        return -1
    elif (winner(board))==X:
        return 1
    else:return 0


def MAX_VALUE(board):
    global x
    if terminal(board):
        return utility(board)
    v=-math.inf
    for action in actions(board):
        j=MIN_VALUE(result(board,action))
        v = max(v,j)
        if board==original:
            x[action]= j
    return v

def MIN_VALUE(board):
    global x
    if terminal(board):
        return utility(board)
    v=math.inf
    for action in actions(board):
        j=MAX_VALUE(result(board,action))
        v = min(v,j)
        if board==original:
            x[action]= j
    return v


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    start=time.time()
    global original
    global AI
    #we must make global AI before it because we will alter AI and use it , therefore global AI is a must
    #if we just want to print AI, then we could neglect typing 'global AI'
    x.clear()
    AI=player(board)
    print(AI)
    if terminal(board):return None
    original=board
    V=MIN_VALUE(board) if AI=='O' else MAX_VALUE(board)
    end=time.time()
    print(end-start)
    print(x)
    for key,value in x.items():
        if value==V:
            print(key)
            return key
