import numpy as np
import time
import logging
from opponents import Opponent
from player import Player

from Board import Board


def main():
    NUM_RUNS = 100
    opponent = Opponent("random")
    player = Player()
    b = Board(player, opponent)
    result = []
    player_loss = 0
    player_no = 0

    draw = 0

    for i in range(NUM_RUNS):
        player_first = i % 2
        if player_first:
            player_no = 1
            print(f"Player Go First  -> O")
        else:
            player_no = -1
            print(f"Player Go Second -> X")

        res, state, step = b.play(player_first=player_first)

        if state == player_no:
            print(f" Player  Win : {max(step)}")
            print(f" AI Loss : {min(step)}")
            print("\n")

        if state == -player_no:
            print(f" AI  Win：{max(step)}")
            print(f" Player  Loss : {min(step)}")
            print("\n")
            player_loss += 1

        if state == 0:
            draw += 1
            print(f"Draw ：{step[0]}")
            print("\n")

        print(
            f"Player Win : {i - player_loss - draw +1}, Loss {player_loss} ,Draw : {draw}"
        )


main()
