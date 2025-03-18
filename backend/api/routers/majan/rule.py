from mahjong.shanten import Shanten
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld

class HaiList:
    def hai34(tehai):
        hai34 = [0 for i in range(34)]
        for hai in tehai:
            hai34[hai.kinds * 9 + hai.number] += 1
        return hai34

    def hai136(tehai):
        hai136 = [hai.number for hai in tehai]
        return hai136



class Rule:

    def shantensuu(tehai):
        shanten = Shanten()
        tiles = HaiList.hai34(tehai)
        result = shanten.calculate_shanten(tiles)
        return result



    def agari(tehai, dora, tsumo, riichi, jikaze, bakaze):
        aka = tehai[0].akaari
        calculator = HandCalculator()
        tiles = HaiList.hai136(tehai)  # Corrected method name
        win_tile = HaiList.hai136([tehai[13]])[0]  # Corrected method name
        dora_indicators = HaiList.hai136(dora)  # Corrected method name
        melds = None
        config = HandConfig(is_tsumo=tsumo, is_riichi=riichi, player_wind=jikaze, round_wind=bakaze,
                            options=OptionalRules(has_aka_dora=aka, has_open_tanyao=True))
        tehai_result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
        return tehai_result