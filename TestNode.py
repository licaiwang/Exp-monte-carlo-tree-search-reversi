import random
from math import log, sqrt
import numpy as np


class Node:
    def __init__(self, board, baseplayer):
        self.state = board.state
        self.valid_moves = board.valid_moves
        self.valid_moves_loc = board.valid_moves_loc
        self.isInside = board.isInside
        self.directions = board.directions
        self.current_player = board.current_player
        self.baseplayer = baseplayer
        self.weight = board.weight
        self.win_value = 0
        self.score = 0
        self.visits = 0
        self.mov = 0
        self.total_step = 0
        self.parent = None
        self.children = []
        self.move = []
        self.tree = []
        self.expanded = False

    def update_win_value(self, value):
        self.win_value = value
        self.visits += 1

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def get_preferred_child(self, root_node):
        """
        挑最高分
        """
        best_score = float("-inf")
        for child in self.children:
            if child.win_value > best_score:
                best_score = child.win_value
                best_child = child

        return best_child

    def get_score(self, root_node):
        return self.win_value

    def is_scorable(self):
        return self.visits != None

    def get_valid_state(self, chose_player, valid_moves):
        """取得玩家可以下棋位置的 list
        
        Args:
            chose_player: An integer to stand for player.
        return:
            a list of (row, col)
        """
        if valid_moves[chose_player] != []:
            return np.unique(valid_moves[chose_player][:, :2], axis=0)
        else:
            return []

    def compute_available_move(self, chose_player):
        """計算玩家能夠下棋的位置
        
        Args:
            chose_player: An integer to stand for player.
        Return:
            a list of (row, col)
        """
        valid_moves = []

        for row, col in self.valid_moves_loc:
            for idx, d in enumerate(self.directions):
                this_row, this_col = row + d[0], col + d[1]
                if (
                    self.isInside(this_row, this_col)
                    and self.state[this_row, this_col] == -chose_player
                ):
                    while True:
                        this_row += d[0]
                        this_col += d[1]
                        if self.isInside(this_row, this_col):
                            if self.state[this_row, this_col] == chose_player:
                                valid_moves.append((row, col, idx))
                                break
                            elif self.state[this_row, this_col] == -chose_player:
                                continue
                            else:
                                break
                        else:
                            break
        valid_moves = np.array(valid_moves)
        return valid_moves

    def print_state(self):
        """輸出局面 O:第一位玩家, X:第二位玩家, #:未下棋位置
        
        e.g.
            ['X' 'X' 'O' 'X' 'X' 'X' 'O' 'O']
            ['X' 'X' 'X' 'X' 'X' 'X' 'O' 'O']
            ['X' 'X' 'X' 'X' 'X' 'X' 'X' 'O']
            ['O' 'O' 'X' 'X' 'X' 'X' 'X' 'O']
            ['O' 'X' 'O' 'X' 'O' 'X' 'X' 'O']
            ['X' 'O' 'O' 'O' 'O' 'O' 'O' 'O']
            ['O' 'X' 'X' 'O' 'X' 'O' 'O' 'O']
            ['O' 'O' 'O' 'X' 'O' 'O' 'O' 'O']
        """
        for i in self.state:
            print(np.where(i == 1, "O", np.where(i == -1, "X", "#")))
        print("\n")

    def action(self, action):
        """決定下棋的位置
        
        Args:
            action: A tuple of location on board (row, col)
        """
        row, col = action
        assert self.state[row, col] == 0, "There has been already set"
        assert action in self.valid_moves[self.current_player][:, :2], "wrong choose"

        self.state[row, col] = self.current_player

        self.valid_moves_loc.remove((row, col))

        for d in self.directions:
            this_row, this_col = row + d[0], col + d[1]
            if (
                self.isInside(this_row, this_col)
                and self.state[this_row, this_col] == 0
                and (this_row, this_col) not in self.valid_moves_loc
            ):
                self.valid_moves_loc.append((this_row, this_col))

        flip_direction = np.where(
            (self.valid_moves[self.current_player][:, :2] == [row, col]).all(axis=1)
        )
        for i in self.valid_moves[self.current_player][flip_direction]:
            d = self.directions[i[-1]]
            this_row, this_col = row, col
            while True:
                this_row += d[0]
                this_col += d[1]

                if self.isInside(this_row, this_col):
                    if self.state[this_row, this_col] == -self.current_player:
                        self.state[this_row, this_col] = self.current_player
                    else:
                        break
                else:
                    break
        self.valid_moves[1] = self.compute_available_move(1)
        self.valid_moves[-1] = self.compute_available_move(-1)
