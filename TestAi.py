import numpy as np
from random import choice
from Record import Record


class TestAi:
    def __init__(self, board, game_leves):
        self.state = board.state.copy()
        self.past_state = board.state.copy()
        self.valid_moves = board.valid_moves.copy()
        self.valid_moves_loc = board.valid_moves_loc.copy()
        self.isInside = board.isInside
        self.directions = board.directions
        self.current_player = board.current_player
        self.root_player = board.current_player

        self.result = []
        self.game_level = game_leves
        self.weight = np.array(
            [
                [9, -3, 5, 5, 5, 5, -3, 9],
                [-3, -8, 1, 1, 1, 1, -8, -3],
                [5, 6, 1, 1, 1, 1, 1, 5],
                [5, 6, 1, 1, 1, 1, 1, 5],
                [5, 6, 1, 1, 1, 1, 1, 5],
                [5, 6, 1, 1, 1, 1, 1, 5],
                [-3, -8, 6, 6, 6, 6, -8, -3],
                [9, -3, 5, 5, 5, 5, -3, 9],
            ]
        )

    def __action(self, action):
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

    def compute_available_move(self, chose_player):
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

    def get_valid_state(self):
        if self.valid_moves[self.current_player] != []:
            return np.unique(self.valid_moves[self.current_player][:, :2], axis=0)
        else:
            return []

    def is_Finish(self, chose_player):
        opponent = -chose_player
        chose_player_valid_moves = self.compute_available_move(chose_player)
        opponent_valid_moves = self.compute_available_move(opponent)
        state_count_chose = (self.state == chose_player).sum()
        state_count_opponent = (self.state == opponent).sum()
        if chose_player_valid_moves.shape[0] == 0 or opponent_valid_moves.shape[0] == 0:
            if state_count_chose > state_count_opponent:
                return (True, 1)
            elif state_count_chose == state_count_opponent:
                return (True, 0)
            else:
                return (True, -1)
        else:
            return (False, 0)

    def extend(self):
        """
        拿一個 state 
        找出所有 child
        """
        record_valid_moves, record_valid_moves_loc, cp = self.setSimulate()
        moves = self.get_valid_state()
        children = []
        for move in moves:
            self.__action(move)
            child = Record(self.current_player, self.state, move, self.deep, None)
            children.append(child)
            self.resetSimulate(record_valid_moves, record_valid_moves_loc, cp)
        self.tree[self.deep] = children

        return 0

    def setSimulate(self):
        record_valid_moves = self.valid_moves.copy()
        record_valid_moves_loc = self.valid_moves_loc.copy()
        cp = self.current_player
        return record_valid_moves, record_valid_moves_loc, cp

    def resetSimulate(self, record_valid_moves, record_valid_moves_loc, cp):
        self.state = self.past_state.copy()
        self.valid_moves = record_valid_moves.copy()
        self.valid_moves_loc = record_valid_moves_loc.copy()
        self.current_player = cp

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

    def easy(self):
        """
        每一步都找吃最多棋的

        勝率:50% ~ 60%
        """
        record_valid_moves, record_valid_moves_loc, cp = self.setSimulate()
        moves = self.get_valid_state()
        scores = []
        for move in moves:
            self.__action(move)
            opponent = -self.current_player
            chose_player_valid_moves = self.compute_available_move(self.current_player)
            opponent_valid_moves = self.compute_available_move(opponent)
            state_count_chose = (self.state == self.current_player).sum()
            state_count_opponent = (self.state == opponent).sum()
            score = state_count_chose - state_count_opponent
            scores.append(score)
            self.resetSimulate(record_valid_moves, record_valid_moves_loc, cp)
        return moves[scores.index(max(scores))]

    def changeWeight(self):
        first_12_weight = np.array(
            [
                [30, -10, 3, 3, 3, 3, -10, 30],
                [-10, -20, 1, 1, 1, 1, -20, -10],
                [3, 1, 10, 10, 10, 10, 1, 3],
                [3, 1, 10, 1, 1, 10, 1, 3],
                [3, 1, 10, 1, 1, 10, 1, 3],
                [3, 1, 10, 10, 10, 10, 1, 3],
                [-10, -20, 1, 1, 1, 1, -20, -3],
                [30, -10, 3, 3, 3, 3, -10, 30],
            ]
        )
        return first_12_weight

    def medium(self, player):

        step = len(np.where(self.state != 0)[0])
        record_valid_moves, record_valid_moves_loc, cp = self.setSimulate()
        moves = self.get_valid_state()
        for i in range(3):
            move = choice(moves)
            self.__action(move)
            opponent = -player
            motivate = len(self.compute_available_move(opponent))
            state_count_chose = (self.state == self.current_player).sum()
            state_count_opponent = (self.state == opponent).sum()
            # 玩家吃 AI
            if player == self.root_player:
                eat = state_count_chose - state_count_opponent
            else:
                eat = state_count_opponent - state_count_chose
            score = getScore(step, eat, move, motivate)
            self.result.append({step: score})
            # 換人
            self.current_player = -self.current_player
            self.explore(step)

        medium(-player)

        return 0

    def explore(self, step):
        step += 1
        record_valid_moves, record_valid_moves_loc, cp = self.setSimulate()
        moves = self.get_valid_state()
        move = choice(moves)
        self.__action(move)
        is_Finish, final_score = self.is_Finish
        if is_Finish:
            self.result.append({step: final_score})
            self.resetSimulate(record_valid_moves, record_valid_moves_loc, cp)
            step -= 1
            # 上步一樣是別人動
            self.current_player = -self.current_player
            self.explore(step)
        else:
            opponent = -self.current_player
            motivate = len(self.compute_available_move(opponent))
            state_count_chose = (self.state == self.current_player).sum()
            state_count_opponent = (self.state == opponent).sum()
            # 玩家吃 AI
            if self.current_player == self.root_player:
                eat = state_count_chose - state_count_opponent
            else:
                eat = state_count_opponent - state_count_chose
            score = getScore(step, eat, move, motivate)
            self.result.append({step: score})
            # 換人
            self.current_player = -self.current_player
            self.explore(step)

    def getScore(self, step, eat, action, mov):
        # 開盤:
        if step < 12:
            weight = self.changeWeight()
            score = weight[action[0]][action[1]] + eat - mov

        # 中盤:
        elif step < 50:
            score = (
                self.weight[action[0]][action[1]] * 3
                + (eat)
                - (mov * 3 / int(step ** 0.5))
            )
        # 尾盤:
        else:
            score = eat - self.weight[action[0]][action[1]] * 2
        return score

    def play_game(self):
        if self.game_level == 0:
            return self.easy()
        if self.game_level == 1:
            return self.medium(1, self.current_player)
