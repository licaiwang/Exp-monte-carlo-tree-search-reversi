from random import choice
import numpy as np
from Board import Board


class Opponent:
    def __init__(self, level="random"):
        assert level in ["random", "minmax", "alphabeta"]
        self._move = MOVE_FUNC[level]
        self.name = "Opponent"

    def first_move(self, valid_moves, state):
        return choice(valid_moves)

    def move(self, _, _0, _1, valid_moves):
        return choice(valid_moves)


def random_move(valid_moves):
    return choice(valid_moves)


def minmax(board):
    pass


def alphabeta(board):
    pass


MOVE_FUNC = {"random": random_move, "minmax": minmax, "alphabeta": alphabeta}
