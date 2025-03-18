from . import rule
from mahjong.constants import EAST, SOUTH, WEST, NORTH
from collections import OrderedDict

class Janshi:


    def __init__(self, play=False, first=False):
        self.name = ''
        self.wind = EAST
        self.wind_str = '東家'
        self.tehai = []
        self.kawa = []
        self.tenbou = 25000

        self.riichi = False
        self.tenpai = False
        self.first = first

        self.play = play

    def haipai(self, yama):
        if self.first:
            self.tehai = yama[0:14]
            del yama[0:14]
        else:
            self.tehai = yama[0:13]
            del yama[0:13]
        
    

    def tsumo(self, yama):
        hai = yama[0]
        del yama[0]
        self.tehai.append(hai)
        return hai

    def riipai(self):
        self.tehai = sorted(self.tehai, key=lambda t: t.kinds * 9 + t.number)

    def get_tenbou(self, tensuu):
        self.tenbou += tensuu

    def lost_tenbou(self, tensuu):
        self.tenbou -= int(tensuu)

    def dahai(self, sutehai=13):
        if self.riichi:
            hai = self.tehai[13]
            del self.tehai[13]
            return hai

        else:
            hai = self.tehai[sutehai]
            del self.tehai[sutehai]
            self.kawa.append(hai)
            return hai

    def riichi_idx(self):
        riichi_idx = []
        for i in range(len(self.tehai)):
            shantensuu = rule.Rule.shantensuu(self.tehai[:i] + self.tehai[i + 1:])
            if shantensuu == 0:
                riichi_idx.append(i)
        return riichi_idx

    def can_ron(self, discarded_tile):
        temp_tehai = self.tehai + [discarded_tile]
        shantensuu = rule.Rule.shantensuu(temp_tehai)
        return shantensuu == -1



