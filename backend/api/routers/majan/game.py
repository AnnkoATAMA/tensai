from mahjong.constants import EAST, SOUTH, WEST, NORTH
import random
from . import rule, janshi, taku



class Game:
    WIND = {0: EAST, 1: SOUTH, 2: WEST, 3: NORTH}
    KAZE = {EAST: '東', SOUTH: '南', WEST: '西', NORTH: '北'}


    def __init__(self, hanchan=False, play=False, aka=False, player=4):
        a = 0
        self.taku = taku.Taku(aka)
        self.aka = aka
        self.hanchan = hanchan
        self.play = play
        self.kansen = not play

        self.janshi = []
        for i in range(player):
            jun = janshi.Janshi(play=True)
            self.janshi.append(jun)
        for i in range(4 - player):
            self.janshi.append(str(janshi.Janshi(play=False)))

        self.junme = 1
        self.chiicha = 0
        self.oya = self.chiicha

        self.ryukyoku = False
        self.agari = False


    def playername(self, player):
        for i in range(player):
            self.janshi[i].name = 'player' + str(i + 1)

        for i in range(player,4):
            self.janshi[i].name = 'com' + str(i + 1)

    def kazegime(self):
        for i in range(4):
            self.janshi[(self.oya + i) % 4].jikaze = self.WIND[i]
            self.janshi[(self.oya + i) % 4].jikaze_str = self.KAZE[self.janshi[(self.oya + i) % 4].jikaze] + '家'

    def oyagime(self):
        self.chiicha = random.randint(0, 3)
        self.oya = self.chiicha
        self.kazegime()
        print('起家 ' + self.janshi[self.chiicha].name + '\n')

    def bakaze_str(self):
        return self.KAZE[self.taku.bakaze]

    def start(self):
        global idx
        self.junme = 1
        self.ryuukyoku = False
        self.agari = False
        self.tobi = False

        for i in range(4):
            janshi.riichi = False

        self.oya = (self.oya + self.taku.kyoku) % 4
        self.kazegime()

        print(str(self.bakaze_str()) + ' ' + str(self.taku.kyoku) + '局\n')

        self.taku.yama = self.taku.hai.copy()
        #random.shuffle(self.taku.yama)

        for i in range(4):
            idx = (self.oya + i) % 4
            self.janshi[idx].haipai(self.taku.yama)
            self.janshi[idx].riipai()

            if self.janshi[idx].play:
                print(self.janshi[idx].jikaze_str + f'{i+1}の手牌')
                print([hai.str for hai in self.janshi[idx].tehai])

                print('\n')

        print('ドラ表示牌')
        print([dora.str for dora in self.taku.dora_hyouji])

        if self.play:
            input('Press any key')

    def agari_shori(self, agari_idx, tsumo):
        print(self.janshi[agari_idx].name + 'の和了')

    # result = rule.Rule.agari(self.janshi[agari_idx].tehai, self.taku.dora_hyouji, tsumo,
    #                          self.janshi[agari_idx].riichi, self.janshi[agari_idx].jikaze, self.taku.bakaze)
    # if result:
    #     print(result.yaku)
    #            if self.janshi[agari_idx].jikaze == EAST:
    #         print(str(result.cost['main']) + 'オール\n')
    #     else:
    #         print(str(result.cost['main']), str(result.cost['additional']) + '点\n')
    #     self.janshi[agari_idx].get_tenbou(result.cost['main'] + result.cost['additional'] * 2)

    #     for i in range(4):
    #         if i != agari_idx:
    #             if i == self.oya:
    #                 self.janshi[i].lost_tenbou(result.cost['main'])
    #            else:
    #            self.janshi[i].lost_tenbou(result.cost['additional'])
    #else:
    #    print('和了の計算に失敗しました')

    def ryuukyoku_shori(self):
        self.ryukyoku = True
        number_of_tenpai = 0
        for janshi in self.janshi:
            shantensu = rule.Rule.shantensuu(janshi.tehai)
            if shantensu == 0:
                print(janshi.name + '聴牌')
                janshi.tenpai = True
                number_of_tenpai += 1
            else:
                print(janshi.name + '不聴')
                janshi.tenpai = False
        if number_of_tenpai != 0:
            for janshi in self.janshi:
                if janshi.tenpai:
                    janshi.get_tenbou(3000 / number_of_tenpai)
                    janshi.tenpai = False
                else:
                    janshi.lost_tenbou(3000 / (4 - number_of_tenpai))

    def finish_kyoku(self):
        self.taku.kyoku += 1
        for i in range(4):
            print(self.janshi[i].name + ' ' + str(self.janshi[i].tenbou) + '点')
            if (self.janshi[i].tenbou < 0):
                print('トビ')
                self.tobi = True
        print('\n')
        if self.play:
            input('Press any key')

    def player_choice(self, player_idx, shantensu):
        janshi = self.janshi[player_idx]
        riichi = False

        # 立直できる状況のときの処理
        if shantensu == 0 and not janshi.riichi and len(self.taku.yama) > 17:
            temp = input('立直しますか?(Y/N) : ')
            if temp == 'Y' or temp == 'y':
                riichi = True

        # 立直するときの入力処理
        if riichi:
            riichi_idx = janshi.riichi_idx()
            while 1:
                try:
                    print(riichi_idx)
                    txt = '捨て牌の番号を入力してください' + str(riichi_idx) + ' : '
                    sutehai = int(input(txt))
                except ValueError:
                    print('半角の整数で入力してください')
                if not sutehai in riichi_idx:
                    print('その牌では立直できません')
                else:
                    break

        # すでに立直しているときはツモ切りを実行
        elif janshi.riichi:
            input('ツモ切りします(Press Enter) ')
            sutehai = 13

        # 通常時の処理
        else:
            while 1:
                try:
                    sutehai = int(input('捨て牌の番号を入力してください(0~13) : '))
                except ValueError:
                    print('0から13の整数を半角で入力してください')
                if sutehai < 0 or 13 < sutehai:
                    print('0から13の整数を入力してください')
                else:
                    break

        # このメソッド内でjanshi.riichiをTrueにしてしまうと立直時にツモ切りしてしまうため
        # riichiを戻し打牌処理を行ってからjanshi.riichiをTrueにする
        return sutehai, riichi

    def ichijun(self):
        print('\n' + str(self.junme) + '巡目')
        for i in range(4):
            # 東→南→西→北の巡で処理を行うための変数
            idx = (self.oya + i) % 4
            janshi = self.janshi[idx]

            print(janshi.jikaze_str + '(' + janshi.name + ')' + 'の手番')

            if self.kansen:
                print([hai.str for hai in janshi.tehai], end=' ')
            elif janshi.play:
                print([str(j) + ': ' + janshi.tehai[j].str for j in range(len(janshi.tehai))], end=' ')

            tsumohai = janshi.tsumo(self.taku.yama)

            if self.kansen:
                print(tsumohai.str)
            elif janshi.play:
                print('13: ' + tsumohai.str)

            shantensu = rule.Rule.shantensuu(janshi.tehai)

            if shantensu == -1:
                agari = False
                if janshi.play:
                    temp = input('和了しますか?(Y/N) : ')
                    if temp == 'Y' or temp == 'y':
                        agari = True
                else:
                    agari = True
                if agari:
                    self.agari_shori(idx, tsumo=True)
                    self.agari = True
                    self.finish_kyoku()
                    break

            if self.kansen or janshi.play:
                if shantensu == 0:
                    print('聴牌')
                else:
                    print(str(shantensu) + '向聴')

            riichi = False

            # プレイヤーの行動選択処理
            if janshi.play:
                sutehai, riichi = self.player_choice(idx, shantensu)

            # NPCの行動選択処理
            else:
                # 聴牌し、山が残り17牌以上なら強制的に立直する
                if shantensu == 0 and not janshi.riichi and len(self.taku.yama) > 17:
                    print(janshi.jikaze_str + 'のリーチ')
                    riichi = True
                sutehai = 13

            # 打牌処理と打牌の表示
            discarded_tile = janshi.dahai(sutehai)
            print('打 ' + discarded_tile.str)

            # リーチ時の処理
            if riichi:
                janshi.lost_tenbou(1000)
                self.taku.riibou += 1
                janshi.riichi = True

            # Check for Ron by other players
            for other_idx in range(4):
                if other_idx != idx and self.janshi[other_idx].can_ron(discarded_tile):
                    if self.janshi[other_idx].play:
                        temp = input(self.janshi[other_idx].name + 'のロンしますか?(Y/N) : ')
                        if temp == 'Y' or temp == 'y':
                            print(self.janshi[other_idx].name + 'のロン')
                            self.agari_shori(other_idx, tsumo=False)
                            self.agari = True
                            self.finish_kyoku()
                            return
                    else:
                        print(self.janshi[other_idx].name + 'のロン')
                        self.agari_shori(other_idx, tsumo=False)
                        self.agari = True
                        self.finish_kyoku()
                        return

            # 山が残り14牌になったら流局処理
            if len(self.taku.yama) == 14:
                print('流局\n')
                self.ryuukyoku_shori()
                self.ryukyoku = True
                self.finish_kyoku()
                break

            janshi.riipai()
            print('\n')
        self.junme += 1

    def game(self):
        self.playername(player=4)
        self.oyagime()

        if self.hanchan:
            kyokusuu = 8
        else:
            kyokusuu = 4

        for i in range(kyokusuu):
            self.start()

            while 1:
                self.ichijun()
                if self.agari == True or self.ryukyoku == True:
                    break

            if self.tobi == True:
                break

            # 南入の処理
            if i == 3:
                self.taku.bakaze = SOUTH
                self.taku.kyoku = 1

