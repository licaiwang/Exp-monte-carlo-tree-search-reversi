# 組員: 姓名一 (學號一), options[姓名二 (學號二),  姓名三 (學號三)]
from random import choice
import time
import logging
import numpy as np
from TestMCTS import test


TIMEOUT = 10


def profile(func):
    def wrap(*args, **kwargs):
        s = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - s
        if duration > TIMEOUT:
            logging.warning(f"Time Limit Exceeded: {duration}")
        logging.info(f"using {duration} sec")
        return result

    return wrap


class Player:
    # TODO: 把第一步隨機改掉
    def __init__(self):
        self.name = "Player"
        pass

    def first_move(self, valid_moves, state):
        # 第一步隨機
        return choice(valid_moves)

    @profile
    def move(self, board, _):
        """

        策略 1: 無論如何，有角點就下，然後更新旁邊邊的權重，方便爬邊

        """
        pior = []
        for state in _:
            if list(state) == [0, 0]:
                pior.append(state)
            if list(state) == [0, 7]:
                pior.append(state)
            if list(state) == [7, 0]:
                pior.append(state)
            if list(state) == [7, 7]:
                pior.append(state)
        if pior != []:
            move = list(choice(pior))
            if move == [0, 0]:
                board.weight[0][1] = 50
                board.weight[1][0] = 50
                board.weight[1][1] = 20
                board.thunder_point.remove([0, 1])
                board.thunder_point.remove([1, 0])
                board.thunder_point.remove([1, 1])
            if move == [0, 7]:
                board.weight[0][6] = 50
                board.weight[1][7] = 50
                board.weight[1][6] = 20
                board.thunder_point.remove([0, 6])
                board.thunder_point.remove([1, 7])
                board.thunder_point.remove([1, 6])
            if move == [7, 0]:
                board.weight[6][0] = 50
                board.weight[7][1] = 50
                board.weight[6][1] = 20
                board.thunder_point.remove([6, 0])
                board.thunder_point.remove([7, 1])
                board.thunder_point.remove([6, 1])
            if move == [7, 7]:
                board.weight[7][6] = 50
                board.weight[6][7] = 50
                board.weight[6][6] = 20
                board.thunder_point.remove([7, 6])
                board.thunder_point.remove([6, 7])
                board.thunder_point.remove([6, 6])
            return move

        """
        策略 2:  

        根據步數決定搜尋深度，50 步到達最大

        """

        move = test(board)

        """
        策略 3:  

        因為搜尋的時候不夠深，所以有時候雷點的分數比較高，但這卻是爛步

        """
        _ = list(_)
        if list(move) in board.thunder_point and len(_) != 0:
            best_score = -10000
            best_move = []
            for mov in _:
                score = board.weight[mov[0]][mov[1]]
                if score > best_score:
                    best_score = score
                    best_move = [mov]
                elif score == best_score:
                    best_move.append(mov)
            return choice(best_move)
        return move
