import random
import numpy as np
import collections


class MonteCarlo:
    def __init__(self, root_node, root_player):
        self.root_node = root_node
        self.root_player = root_player
        self.child_finder = None
        self.node_evaluator = lambda child, montecarlo: None
        self.isInside = root_node.isInside
        self.directions = root_node.directions
        self.tree = []
        self.width = 12
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

    def make_choice(self, current_player):
        """
        best_children = []
        most_visits = float("-inf")
        for child in self.root_node.children:
            if child.visits > most_visits:
                most_visits = child.visits
                best_children = [child]
            elif child.visits == most_visits:
                best_children.append(child)
        """
        """
        挑 最高分
        """
        root_key = 100
        best_children = []
        best_score = -1000
        score = []
        tmp_parent = []
        tmp_child = []
        root_node = []
        step_id = []
        candidate = []
        best_leaf = None
        base_score = []

        for i, child in enumerate(self.root_node.children):
            self.traversal(child, i)

        if self.tree:
            for tree in self.tree:
                for key, value in tree.items():
                    # state 轉 1D 找哪邊非 0
                    score.append(value[0])
                    tmp_child.append(np.where(value[1] != 0))
                    tmp_parent.append(np.where(value[2] != 0))
                    step_id.append(value[3])

            idx = [i for i, j in enumerate(step_id) if j == max(step_id)]

            best_score = -10000
            #  找最深而且分數最好的
            for id_ in idx:
                if score[id_] > best_score:
                    best_score = score[id_]
                    best_leaf = self.tree[id_].copy()

            # 回去找誰走過來的
            leaf_p = []
            leaf_id = 0
            for _, v in best_leaf.items():
                leaf_p = np.where(v[2] != 0)
                leaf_id = v[3]

            best_root = best_leaf
            search = 0
            while True:
                if leaf_id == 0:
                    break
                for i, c in enumerate(tmp_child):
                    if len(c[0]) == len(leaf_p[0]):
                        res = np.equal(c, leaf_p)
                        if len(tuple(res)) != 1:
                            break
                        leaf_id -= 1
                        leaf_p = tmp_parent[i]
                        best_root = self.tree[i]
                        break
                search += 1
                if search > len(tmp_child):
                    break

            for _, v in best_root.items():
                value = v[0]
                move = v[5]
                candidate.append([value, move])

            b_score = -10000
            b_m = []

            for candi in candidate:
                score = candi[0]
                if score > b_score:
                    b_score = score
                    b_m = candi[1]
        else:
            # 即將結束
            b_score = -1000
            b_m = []
            for i, child in enumerate(self.root_node.children):
                score = child.win_value
                if score > b_score:
                    b_score = score
                    b_m = child.move

        return b_m

    def traversal(self, root_tree, id):
        weight_cp = self.weight.copy()
        for child in root_tree.children:
            if child != []:
                self.evaluate(child)
                self.tree.append(
                    {
                        child.total_step: [
                            child.win_value,
                            child.state.flatten(),
                            child.parent.state.flatten(),
                            id,
                            child.move,
                            child.parent.move,
                        ]
                    }
                )
                self.traversal(child, id + 1)
        self.weight = weight_cp

    def evaluate(self, child):
        op_score = 0
        player_score = 0
        p_num = 0
        c_num = 0

        for i in range(8):
            for j in range(8):
                if child.state[i][j] == self.root_player:
                    p_num += 1
                    child.total_step += 1
                    # 如果佔角了，就可以考慮爬邊
                    if i == 0 and j == 0:
                        self.weight[0][1] = 80
                        self.weight[1][0] = 80
                    if i == 0 and j == 7:
                        self.weight[0][6] = 80
                        self.weight[1][7] = 80
                    if i == 7 and j == 0:
                        self.weight[6][0] = 80
                        self.weight[7][1] = 80
                    if i == 7 and j == 0:
                        self.weight[7][6] = 80
                        self.weight[6][7] = 80
                    player_score += self.weight[i][j]

                if child.state[i][j] == -self.root_player:
                    c_num += 1
                    child.total_step += 1
                    op_score += self.weight[i][j]

        eat = p_num - c_num

        # 開盤:
        if child.total_step <= 12:
            weight = self.changeWeight()
            score = player_score - op_score + eat * 3
        # 中盤:
        elif child.total_step <= 50 and child.total_step > 12:
            score = player_score - op_score + eat * 5
        # 尾盤:
        elif child.total_step > 50:
            score = player_score - op_score + eat * 10

        child.win_value = score

    def changeWeight(self):
        first_12_weight = np.array(
            [
                [90, -60, 30, 3, 3, 30, -60, 90],
                [-60, -500, 1, 1, 1, 1, -500, -60],
                [30, 1, 10, 10, 10, 10, 1, 30],
                [3, 1, 10, 1, 1, 10, 1, 3],
                [3, 1, 10, 1, 1, 10, 1, 3],
                [30, 1, 10, 10, 10, 10, 1, 30],
                [-60, -500, 1, 1, 1, 1, -500, -60],
                [90, -60, 30, 3, 3, 30, -60, 90],
            ]
        )
        return first_12_weight

    def simulate(self, expansion_count=1):
        for i in range(expansion_count):
            current_node = self.root_node
            while current_node.expanded:
                current_node = current_node.get_preferred_child(self.root_node)
            self.width = 12
            self.expand(current_node)

    def expand(self, node):
        self.child_finder(node)
        score = 0
        for child in node.children:
            is_finish, score = self.node_evaluator(child, self)
            node.update_win_value(score)
            if not child.is_scorable():
                self.random_rollout(child)
                child.children = []

        if len(node.children):
            node.expanded = True

    def random_rollout(self, node):
        self.child_finder(node)

        child = random.choice(node.children)
        node.children = []
        node.add_child(child)
        is_finish, score = self.node_evaluator(child, self)
        node.update_win_value(score)
        if not is_finish:
            self.random_rollout(child)
