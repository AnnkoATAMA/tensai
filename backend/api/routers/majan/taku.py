from . import hai
from mahjong.constants import EAST, SOUTH, WEST, NORTH

class Taku:
    def __init__(self,aka=False):
        self.bakaze = EAST
        self.hai = []
        self.aka = aka
        self.kyoku = 1

        self.hai = []
        for i in range(136):
            self.hai.append(hai.Hai(i, self.aka))

        self.yama = self.hai.copy()

        self.kanctn = 0
        self.dora_hyouji = []
        self.dora_hyouji.append(self.yama[-(6 + self.kanctn * 2)])

        self.riibou = 0

    def kan(self):
        self.kanctn += 1
        self.dora_hyouji.append(self.yama[-(6 + self.kanctn * 2)])