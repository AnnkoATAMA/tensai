class Hai:
    KINDS = {0: '萬', 1: '筒', 2: '索', 3: '東', 4: '南', 5: '西', 6: '北', 7: '白', 8: '発', 9: '中'}
    AKADORA = {16: '赤5萬', 52: '赤5筒', 88: '赤5索'}

    def __init__(self,number,aka=True):
        self.number = number
        self.akaari = aka

        if number < 108:
            self.kinds = number // 36
            self.number = self.number // 4 - self.kinds * 9
            if aka and self.number in self.AKADORA:
                self.str = self.AKADORA[self.number]
            else:
                self.str = str(self.number + 1) + self.KINDS[self.kinds]

        else:
            self.kinds = 3
            self.number = (self.number - 108) // 4
            self.str = self.KINDS[self.kinds+self.number]