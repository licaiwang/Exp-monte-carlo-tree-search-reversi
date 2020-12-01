import numpy as np
from TestNode import Node
from copy import deepcopy
from MCTS import MonteCarlo


# 紀錄原本的玩家先手還後手
base_player = 0


def test(board):

    """
    測試蒙地卡羅樹搜尋，調整 montecarlo.simulate() 次數，可以增加或減少預判後面幾步

    對於黑白棋而言，解尾盤非常重要
    
    Args:
                 board: 當前盤面，物件 Board 的所有資訊 
    Return:
             best_move: 找到的最佳移動

    """

    global base_player
    total_step = board.total_step
    base_player = board.current_player
    node = Node(board, base_player)
    montecarlo = MonteCarlo(node, base_player)
    montecarlo.child_finder = child_finder
    montecarlo.node_evaluator = node_evaluator

    if total_step <= 12:
        montecarlo.simulate(3)
    elif total_step <= 24 and total_step > 12:
        # 8 , 5
        montecarlo.simulate(8)
    elif total_step <= 48 and total_step > 24:
        # 16 , 10, 8
        montecarlo.simulate(16)
    else:
        # 25 , 15 , 10
        montecarlo.simulate(25)

    best_move = montecarlo.make_choice(base_player)

    return best_move


def child_finder(node):
    """
    定義子節點怎麼找的

    Args:
        node: 現在的節點

    """
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
    """
    評估子節點的好壞

    Args:
            node: 現在的節點

    Return:
            是否結束: True or False
            getScore: 該節點分數

    """
    global base_player
    opponent = -self.current_player
    chose_player_valid_moves = self.compute_available_move(self.current_player)
    opponent_valid_moves = self.compute_available_move(opponent)
    state_count_chose = (self.state == self.current_player).sum()
    state_count_opponent = (self.state == opponent).sum()
    eat = state_count_chose - state_count_opponent
    step = step = len(np.where(self.state != 0)[0])

    # 如果這手是真正的玩家 (Player) 的，就看要步要調整權重
    if self.current_player == base_player:
        weightChange(self, self.move[0], self.move[1])

    # 吃子數
    eat = state_count_chose - state_count_opponent

    if chose_player_valid_moves.shape[0] == 0 or opponent_valid_moves.shape[0] == 0:
        if self.current_player == base_player and eat > 0:
            # 玩家贏
            return True, 2000
        elif eat == 0:
            # 平手
            return True, 750
        else:
            # 輸
            return True, -2000

    # 繼續
    else:
        return (
            False,
            getScore(self, step, eat, self.move, self.mov, self.current_player),
        )


def changeWeight():
    """
    前 12 手盡量下在 "箱" 裡

    權重不一樣，從這裡拿

    Return:
            前 12 手權重
    """
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
    """
    算子節點分數

    Args:
                    step:  總步數
                     eat:  吃子數
                  action:  移動
                     mov:  對手行動力剩餘
          current_player:  現在玩家
        
    Return:
                   score: 分數
    """
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
    """
    玩家如果搶到角了，就可以考慮佔邊戰術

    權重不一樣，從這裡更改

    Args:
            x: 棋盤位置 row
            y: 棋盤位置 colume
    """
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
