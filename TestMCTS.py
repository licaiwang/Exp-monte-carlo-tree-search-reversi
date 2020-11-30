import numpy as np
from TestNode import Node
from copy import deepcopy
from MCTS import MonteCarlo


# 紀錄原本的玩家先手還後手
base_player = 0


def test(board, depth):
    global base_player
    base_player = board.current_player
    node = Node(board, base_player)
    montecarlo = MonteCarlo(node, base_player)
    montecarlo.child_finder = child_finder
    montecarlo.node_evaluator = node_evaluator

    # 調整可以增加或減少預判後面幾步，對於黑白棋而言，解尾盤非常重要
    if depth <= 12:
        montecarlo.simulate(3)
    elif depth <= 24 and depth > 12:
        montecarlo.simulate(8)
    elif depth <= 48 and depth > 24:
        montecarlo.simulate(16)
    else:
        montecarlo.simulate(25)

    best_move = montecarlo.make_choice(base_player)

    return best_move


def child_finder(node):
    global base_player
    valid = node.get_valid_state(node.current_player, node.valid_moves)
    if valid != []:
        for move in valid:
            child = Node(deepcopy(node), base_player)
            child.action(move)
            child.move = move
            child.current_player = -child.current_player
            child.mov = len(child.compute_available_move(child.current_player))
            node.add_child(child)


def node_evaluator(self, node):
    global base_player
    opponent = -self.current_player
    chose_player_valid_moves = self.compute_available_move(self.current_player)
    opponent_valid_moves = self.compute_available_move(opponent)
    state_count_chose = (self.state == self.current_player).sum()
    state_count_opponent = (self.state == opponent).sum()
    eat = state_count_chose - state_count_opponent
    step = step = len(np.where(self.state != 0)[0])

    # base_player 真正的玩家
    if self.current_player == base_player:
        weightChange(self, self.move[0], self.move[1])

    eat = state_count_chose - state_count_opponent

    if chose_player_valid_moves.shape[0] == 0 or opponent_valid_moves.shape[0] == 0:
        if self.current_player == base_player and eat > 0:
            # 玩家贏
            return True, 1000
        elif eat == 0:
            # 平手
            return True, 500
        else:
            # 輸
            return True, -1000

    #
    else:
        return (
            False,
            getScore(self, step, eat, self.move, self.mov, self.current_player),
        )


def changeWeight():
    first_12_weight = np.array(
        [
            [90, -60, 30, 3, 3, 30, -60, 90],
            [-60, -100, 1, 1, 1, 1, -100, -60],
            [30, 1, 10, 10, 10, 10, 1, 30],
            [3, 1, 10, 1, 1, 10, 1, 3],
            [3, 1, 10, 1, 1, 10, 1, 3],
            [30, 1, 10, 10, 10, 10, 1, 30],
            [-60, -100, 1, 1, 1, 1, -100, -60],
            [90, -60, 30, 3, 3, 30, -60, 90],
        ]
    )
    return first_12_weight


def getScore(self, step, eat, action, mov, current_player):
    global base_player
    # 開盤: 前 12 手盡量下在 "箱"
    if step <= 12:
        self.weight = changeWeight()
        score = self.weight[action[0]][action[1]] - mov * 5

    # 中盤: 以封鎖對手行動力加上佔好位置為主
    elif step <= 45 and step > 12:
        score = self.weight[action[0]][action[1]] * 3 - (mov * 8 / int(step ** 0.5))
    # 尾盤: 考慮吃最多
    else:
        score = eat

    return score


# 更改權重
def weightChange(self, x, y):
    # 下到角落則調整相鄰兩排邊的權重
    if x == 0 and y == 0:
        self.weight[x + 1][y + 1] = 90
        for i in range(1, 7):
            self.weight[x + i][y] = (10 - i) * 2
            self.weight[x][y + i] = (10 - i) * 2
    elif x == 7 and y == 0:
        self.weight[x - 1][y + 1] = 90
        for i in range(1, 7):
            self.weight[x - i][y] = (10 - i) * 2
            self.weight[x][y + i] = (10 - i) * 2
    elif x == 7 and y == 7:
        self.weight[x - 1][y - 1] = 90
        for i in range(1, 7):
            self.weight[x - i][y] = (10 - i) * 2
            self.weight[x][y - i] = (10 - i) * 2
    elif x == 0 and y == 7:
        self.weight[x + 1][y - 1] = 90
        for i in range(1, 7):
            self.weight[x + i][y] = (10 - i) * 2
            self.weight[x][y - i] = (10 - i) * 2
