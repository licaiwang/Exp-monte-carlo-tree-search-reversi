import numpy as np


class Board:
    def __init__(self, player, opponent):
        """
        
        player representation: (first_player: O, second_player: X)

        Args:
            player: an Object which has required functions
            opponent: an Object which has required functions

        """
        self.n_side = 8  # (rows,cols)
        self.player = player
        self.opponent = opponent
        self.total_step = 0
        self.weight = np.array(
            [
                [90, -80, 50, 15, 15, 50, -80, 90],
                [-80, -500, 6, 6, 6, 6, -500, -80],
                [50, 6, 8, 8, 8, 8, 6, 50],
                [15, 6, 8, 3, 3, 8, 6, 15],
                [15, 6, 8, 3, 3, 8, 6, 15],
                [50, 6, 8, 8, 8, 8, 6, 50],
                [-80, -500, 6, 6, 6, 6, -500, -80],
                [90, -80, 50, 15, 15, 50, -80, 90],
            ]
        )
        self.thunder_point = [
            [1, 1],
            [0, 1],
            [1, 0],
            [1, 6],
            [0, 6],
            [1, 7],
            [6, 1],
            [6, 0],
            [7, 1],
            [6, 6],
            [7, 6],
            [6, 7],
        ]

        # 012
        # 3#4
        # 567
        self.directions = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )

        # 黑色 = O (先行): 1, 白色 = X: -1
        self.isInside = (
            lambda r, c: True
            if (0 <= r < self.n_side and 0 <= c < self.n_side)
            else False
        )

    def __set_state(self):
        self.state = np.zeros((self.n_side, self.n_side))

        self.state[self.n_side // 2 - 1, self.n_side // 2 - 1] = -1
        self.state[self.n_side // 2, self.n_side // 2] = -1
        self.state[self.n_side // 2 - 1, self.n_side // 2] = 1
        self.state[self.n_side // 2, self.n_side // 2 - 1] = 1

    def reset(self):
        """
        重製局面
        
        """
        self.__set_state()
        self.current_player = 1
        self.valid_moves = {1: [], -1: []}
        self.valid_moves_loc = []
        self.thunder_point = [
            [1, 1],
            [0, 1],
            [1, 0],
            [1, 6],
            [0, 6],
            [1, 7],
            [6, 1],
            [6, 0],
            [7, 1],
            [6, 6],
            [7, 6],
            [6, 7],
        ]

        self.weight = np.array(
            [
                [90, -80, 50, 15, 15, 50, -80, 90],
                [-80, -500, 6, 6, 6, 6, -500, -80],
                [50, 6, 8, 8, 8, 8, 6, 50],
                [15, 6, 8, 3, 3, 8, 6, 15],
                [15, 6, 8, 3, 3, 8, 6, 15],
                [50, 6, 8, 8, 8, 8, 6, 50],
                [-80, -500, 6, 6, 6, 6, -500, -80],
                [90, -80, 50, 15, 15, 50, -80, 90],
            ]
        )
        self.total_step = 0
        for row, col in np.argwhere(self.state != 0):
            for d in self.directions:
                this_row = row + d[0]
                this_col = col + d[1]
                if (
                    self.isInside(this_row, this_col)
                    and self.state[this_row, this_col] == 0
                    and (this_row, this_col) not in self.valid_moves_loc
                ):
                    self.valid_moves_loc.append((this_row, this_col))

        self.valid_moves[1] = self.compute_available_move(1)
        self.valid_moves[-1] = self.compute_available_move(-1)

    def __action(self, action):
        """
        決定下棋的位置
        
        Args:
            action: A tuple of location on board (row, col)
        """
        self.total_step += 1
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
        """
        計算玩家能夠下棋的位置
        
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

    def is_game_finished(self, chose_player):
        """
        確認該局是否結束以及若結束確認該位是否獲勝。
        
        Args:
            chose_player: An integer to stand for player.
        Returns:
            (Boolean, Integer): (是否結束, 獲勝玩家 1: 黑棋, -1: 白棋, 0: 平手)
        """
        opponent = -chose_player
        chose_player_valid_moves = self.compute_available_move(chose_player)
        opponent_valid_moves = self.compute_available_move(opponent)

        if (
            chose_player_valid_moves.shape[0] == 0
            and opponent_valid_moves.shape[0] == 0
        ):
            state_count_chose = (self.state == chose_player).sum()
            state_count_opponent = (self.state == opponent).sum()

            if state_count_chose > state_count_opponent:
                return (True, chose_player, [state_count_chose, state_count_opponent])
            elif state_count_chose == state_count_opponent:
                return (True, 0, [state_count_chose, state_count_opponent])
            else:
                return (True, opponent, [state_count_chose, state_count_opponent])
        else:
            return (False, 0, [999, 999])

    def play(self, player_first=False):
        """
        一局遊戲的執行函式
        
        Args:
            player_first: Boolean
        """
        self.reset()
        players = [self.player, self.opponent]

        if player_first:
            # format: idx = (row,col)

            idx = self.player.first_move(
                self.get_valid_state(self.current_player), self.state
            )
            self.__action(idx)
            offset = 0
            player_no = 1

        else:

            idx = self.opponent.first_move(
                self.get_valid_state(self.current_player), self.state
            )
            self.__action(idx)
            offset = 1
            player_no = -1

        isFinished = (False, None)
        while isFinished[0] == False:

            offset = (offset + 1) % 2
            # 第一手已經在上面先走了，所以這邊先換人下
            self.current_player = -self.current_player
            current_player_ = players[offset]
            vaild = self.get_valid_state(self.current_player)
            if vaild != []:
                idx = current_player_.move(
                    self, self.get_valid_state(self.current_player),
                )
                self.__action(idx)
                self.print_state()
            isFinished = self.is_game_finished(self.current_player)

        if isFinished[1] == player_no:
            self.print_state()
            return (True, isFinished[1], isFinished[2])
        else:
            self.print_state()
            return (False, isFinished[1], isFinished[2])

    def print_state(self):
        """
        輸出局面 O:第一位玩家, X:第二位玩家, #:未下棋位置
        
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

    def get_valid_state(self, chose_player):
        """
        取得玩家可以下棋位置的 list
        
        Args:
            chose_player: An integer to stand for player.
        return:
            a list of (row, col)
        """
        if self.valid_moves[chose_player] != []:
            return np.unique(self.valid_moves[chose_player][:, :2], axis=0)
        else:
            return []
