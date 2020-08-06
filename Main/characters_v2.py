import random

# 控制是否打印战斗过程
IF_PRINT = 1

"游戏裁判"
class Judgment(object):
    def __init__(self, char_a, char_b):
        # 速度快的是内部的char_a
        if char_a.speed > char_b.speed:
            self.char_a = char_a
            self.char_b = char_b
        else:
            self.char_b = char_a
            self.char_a = char_b
        # 预定胜利者
        self.winner = ''

    def over_judge(self):
        # 有复活技能就复活，没有就结束
        if self.char_a.health<=0:
            if self.char_a.revive_flag==1:
                self.char_a.revive(self.char_b)
                self.char_a.revive_flag = 0
            else:
                self.winner = self.char_b.name
                return 0
        if self.char_b.health<=0:
            if self.char_b.revive_flag==1:
                self.char_b.revive(self.char_a)
                self.char_b.revive_flag = 0
            else:
                self.winner = self.char_a.name
                return 0
        return 1

    def act_dealing(self, act_list, oneself, target, if_print=IF_PRINT):
        for index in act_list:
            if index[0] == 'TARGET':
                # 这里偷懒了导致鲁棒性很差，可以大幅度优化
                if index[1] == 'HEALTH': target.health += index[2] * index[3]
                if index[1] == 'STOP_PAR': target.stop_par_count += index[2] * index[3]
                if index[1] == 'STOP_VER': target.stop_ver_count += index[2] * index[3]
                if index[1] == 'STOP_SKILL': target.stop_skill_count += index[2]*index[3]
            elif index[0] == 'SELF':
                if index[1] == 'HEALTH': oneself.health += index[2] * index[3]
                if index[1] == 'STOP_PAR': oneself.stop_par_count += index[2] * index[3]
                if index[1] == 'STOP_VER': oneself.stop_ver_count += index[2] * index[3]
                if index[1] == 'STOP_SKILL': oneself.stop_skill_count += index[2] * index[3]
        if if_print==1:
            print('*** %s TIME ***' % oneself.name)
            print(act_list)
            self.char_a.print_attr(health_only=1)
            self.char_b.print_attr(health_only=1)

        if oneself.health >= 100:
            oneself.health = 100
        if target.health >= 100:
            target.health = 100

        return self.over_judge()


    def game_begin(self, if_print=IF_PRINT):
        # 回合计数
        round_count = 0
        # 赛前准备
        self.char_a.pre(self.char_b)
        self.char_b.pre(self.char_a)

        # 游戏开始
        # while round_count<=20:
        while self.over_judge():
            round_count += 1
            if if_print == 1:
                print("\nround %d\n" % round_count)

            # 处理char_a事件
            if (self.char_a.stop_ver_count==0) & (self.char_a.stop_par_count==0):
                if self.char_a.stop_skill_count==0:
                    act_list = self.char_a.round_fight(self.char_b, round_count)
                else:
                    act_list = [['TARGET', 'HEALTH', self.char_a.gen_attack(self.char_b)[0]*self.char_a.damage_rate, -1]]
                    self.char_a.stop_skill_count = (abs(self.char_a.stop_skill_count-1)+self.char_a.stop_skill_count-1)/2

                if self.act_dealing(act_list, self.char_a, self.char_b) == 0:
                    break
            else:
                self.char_a.stop_ver_count = positive_number(self.char_a.stop_ver_count - 1)
                self.char_a.stop_par_count = positive_number(self.char_a.stop_par_count - 1)

            # 处理char_b事件
            if (self.char_b.stop_ver_count==0) & (self.char_b.stop_par_count==0):
                if self.char_b.stop_skill_count == 0:
                    act_list = self.char_b.round_fight(self.char_a, round_count)
                else:
                    act_list = [['TARGET', 'HEALTH', self.char_b.gen_attack(self.char_a)[0]*self.char_b.damage_rate, -1]]
                    self.char_b.stop_skill_count = (abs(self.char_b.stop_skill_count-1)+self.char_b.stop_skill_count-1)/2
                if self.act_dealing(act_list, self.char_b, self.char_a) == 0:
                    break
            else:
                self.char_b.stop_ver_count = positive_number(self.char_b.stop_ver_count - 1)
                self.char_b.stop_par_count = positive_number(self.char_b.stop_par_count - 1)

            if round_count>=100:
                self.winner='None'
                break
        if if_print == 1:
            print("\nWINNER: %s" % self.winner)
        return self.winner


class Character(object):
    def __init__(self, name, health, attack, defense, speed, if_single):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.if_single = if_single
        self.hit_rate = 1
        # 复活技能标记
        self.revive_flag = 1
        # 停止回合计数: 麻痹 眩晕
        self.stop_par_count = 0
        self.stop_ver_count = 0
        # 停止技能回合计数
        self.stop_skill_count = 0
        # 全局伤害变化率
        self.damage_rate = 1
        # 技能抵抗率
        self.skill_resist_rate = -1


    def print_attr(self, health_only):
        if health_only==1:
            print("%s: %d" % (self.name, self.health))
        else:
            print("name: %s\nhealth: %d\nattack: %d\ndefense: %d\nhit_rate: %d" % (self.name, self.health, self.attack, self.defense, self.hit_rate))

    def gen_attack(self, char_target, if_elemental=0):
        flag = random.uniform(0, 1)
        if flag <= self.hit_rate:
            # 是否元素普攻
            if if_elemental==1:
                hit_num = self.attack
            else:
                hit_num = self.attack-char_target.defense
            flag = 1
        else:
            hit_num = 0
            flag = 0
        # 普攻返回[伤害数字, 是否命中]
        return [positive_number(hit_num*flag), flag]

    def pre(self, char_target):
        pass

    def revive(self, char_target):
        pass

    def round_fight(self, char_target, round_count):
        # act_list = [[char, key, value, sign, note], []]
        pass


'''琪亚娜'''
class Kiana(Character):
    def round_fight(self, char_target, round_count):
        act_list = []

        # 每两回合触发一次技能,35%概率眩晕一回合;否则普攻
        stop_ver_round_count = 0
        if round_count % 2 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag<char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name=='Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                hit_num = self.attack + 2*char_target.defense - char_target.defense
                # 施放后是否眩晕
                flag = random.uniform(0, 1)
                if flag <= 0.35:
                    stop_ver_round_count += 1
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        # 记录本次行为数据并返回
        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        act_list += [['SELF', 'STOP_VER', stop_ver_round_count, 1]]
        return act_list

    def round_fight_without_skill(self, char_target, round_count):
        pass


'''芽衣'''
class Mei(Character):
    def round_fight(self, char_target, round_count):
        act_list = []

        # 每两回合触发一次技能,额外造成5次3点元素伤害;否则普攻
        hit_num = 0
        stop_par_round_count = 0
        if round_count % 2 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag<char_target.skill_resist_rate:
                # 如果是呆鹅，额外承受30伤害
                if char_target.name=='Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                mul_hit_num = 3
                for i in range(5):
                    act_list += [['TARGET', 'HEALTH', mul_hit_num*self.damage_rate, -1]]
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        # 有30%概率麻痹对方一回合
        flag = random.uniform(0, 1)
        if flag <= 0.3:
            stop_par_round_count += 1
            act_list += [['TARGET', 'STOP_PAR', stop_par_round_count, 1]]


        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''板鸭'''
class Bronya(Character):
    def round_fight(self, char_target, round_count):
        act_list = []
        hit_num = 0
        # 每三回合触发一次技能,造成1-100伤害;否则普攻
        if round_count % 3 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag<char_target.skill_resist_rate:
                # 如果是呆鹅，额外承受30伤害
                if char_target.name=='Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                hit_num_1 = random.randint(1, 100)
                act_list += [['TARGET', 'HEALTH', positive_number(hit_num_1)*self.damage_rate, -1]]
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        # 攻击后有25%概率造成4*12伤害
        flag = random.uniform(0, 1)
        if flag <= 0.25:
            mul_hit_num = positive_number(12 - char_target.defense)
            for i in range(4):
                act_list += [['TARGET', 'HEALTH', positive_number(mul_hit_num) * self.damage_rate, -1]]

        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''姬子'''
class Himeko(Character):
    def round_fight(self, char_target, round_count):
        act_list = []

        # 每二回合触发一次技能,攻击力翻倍,命中率下降35%
        if round_count % 2 == 0:
            self.attack *= 2
            self.hit_rate -= 0.35

        # 普攻
        [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
        if hit_flag == 1:
            hit_num = hit_num_tmp
        else:
            hit_num = 0

        # 记录本次行为数据并返回
        # 对非单人队伍伤害提升100%
        if char_target.if_single == 1:
            act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        else:
            act_list += [['TARGET', 'HEALTH', positive_number(hit_num*2)*self.damage_rate, -1]]
        return act_list


'''丽塔'''
class Rita(Character):
    def __init__(self, name, health, attack, defense, speed, if_single):
        super().__init__(name, health, attack, defense, speed, if_single)
        self.skill_2_flag = 1

    def round_fight(self, char_target, round_count):
        act_list = []

        # 每四回合触发一次技能,对方回复4点血量，2回合无法使用技能，伤害一次性下降60%;否则普攻, 且35%概率，本次普攻伤害减伤3，对方攻击力永久减4
        recover_num = 0
        hit_num = 0
        stop_skill_count = 0
        if round_count % 4 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag<char_target.skill_resist_rate:
                # 如果是呆鹅，额外承受30伤害
                if char_target.name=='Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                recover_num = 4
                stop_skill_count = 2
                if self.skill_2_flag==1:
                    char_target.damage_rate *= 0.4
                    self.skill_2_flag = 0
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
                flag = random.uniform(0, 1)
                if flag <= 0.35:
                    hit_num -= 3
                    if char_target.attack <= 4:
                        char_target.attack = 0
                    else:
                        char_target.attack -= 4
            else:
                hit_num = 0


        # 记录本次行为数据并返回
        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        act_list += [['TARGET', 'HEALTH', positive_number(recover_num), 1]]
        act_list += [['TARGET', 'STOP_SKILL', stop_skill_count, 1]]
        return act_list


'''希儿'''
class Selee(Character):
    def __init__(self, name, health, attack, defense, speed, if_single):
        super().__init__(name, health, attack, defense, speed, if_single)
        # state=0白希, state=1黑希;初始白希
        self.state = 0

    def round_fight(self, char_target, round_count):
        act_list = []

        # 攻击前改变状态：黑希，攻击+10，防御-5；白希，攻击-10，防御-5，回复1-15血量
        recover_num = 0
        if self.state == 0:
            self.attack += 10
            self.defense -= 5
            self.state = 1
        elif self.state == 1:
            self.attack -= 10
            self.defense += 5
            recover_num = random.randint(1, 15)
            self.state = 0

        [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
        if hit_flag == 1:
            hit_num = hit_num_tmp
        else:
            hit_num = 0

        # 记录本次行为数据并返回
        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        act_list += [['SELF', 'HEALTH', positive_number(recover_num), 1]]
        return act_list


'''八重樱&卡莲'''
class YaeAndKallen(Character):
    def round_fight(self, char_target, round_count):
        act_list = []

        # 回合开始前有30%概率回复25血量
        flag = random.uniform(0, 1)
        recover_num = 0
        if flag <= 0.3:
            recover_num += 25

        # 每两回合触发一次技能，造成25元素伤害；否则普攻
        if round_count % 2 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag<char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name=='Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                hit_num = 25
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        # 记录本次行为数据并返回
        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        act_list += [['SELF', 'HEALTH', positive_number(recover_num), 1]]
        return act_list


'''渡鸦'''
class Corvus(Character):
    def pre(self, char_target):
        if char_target.name == 'Kiana':
            self.damage_rate = 1.25
        else:
            flag = random.uniform(0, 1)
            if flag<=0.25:
                self.damage_rate = 1.25

    def round_fight(self, char_target, round_count):
        act_list = []
        hit_num = 0
        # 每三回合触发一次技能,造成7*16伤害;否则普攻
        if round_count % 3 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag < char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name == 'Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                mul_hit_num = (abs(16-char_target.defense)+16-char_target.defense)/2
                for i in range(7):
                    act_list += [['TARGET', 'HEALTH', positive_number(mul_hit_num)*self.damage_rate, -1]]
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''德丽莎'''
class Theresa(Character):
    def round_fight(self, char_target, round_count):
        act_list = []
        hit_num = 0
        # 每三回合触发一次技能,造成5*16伤害;否则普攻，且有30%攻击后降低对方5点防御
        if round_count % 3 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag < char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name == 'Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                mul_hit_num = positive_number(16-char_target.defense)
                for i in range(5):
                    act_list += [['TARGET', 'HEALTH', positive_number(mul_hit_num)*self.damage_rate, -1]]

        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        # 攻击后有30%概率降低对方5点防御
        flag = random.uniform(0, 1)
        if flag <= 0.3:
            char_target.defense -= 5


        # 记录本次行为数据并返回
        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''双子'''
class Gemini(Character):
    def pre(self, char_target):
        self.revive_flag = 1

    def revive(self, char_target):
        self.health = 20

    def round_fight(self, char_target, round_count):
        act_list = []

        # 技能触发，50%概率造成233伤害，50%概率造成50伤害；否则普攻
        if self.revive_flag == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag < char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name == 'Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                flag = random.uniform(0, 1)
                if flag<=0.5:
                    hit_num = 233
                else:
                    hit_num = 50
            self.revive_flag -= 1
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''幽兰戴尔'''
class Durandal(Character):
    def pre(self, char_target):
        # 必杀技抗性16%
        self.skill_resist_rate = 0.16

    def round_fight(self, char_target, round_count):
        act_list = []
        # 每回合前攻击上升3
        self.attack += 3

        # 普攻
        [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
        if hit_flag == 1:
            hit_num = hit_num_tmp
        else:
            hit_num = 0

        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''符华'''
class Hua(Character):
    def gen_attack(self, char_target, if_elemental=0):
        flag = random.uniform(0, 1)
        if flag <= self.hit_rate:
            hit_num = self.attack
            flag = 1
        else:
            hit_num = 0
            flag = 0
        # 普攻返回[伤害数字, 是否命中]
        return [positive_number(hit_num*flag), flag]

    def round_fight(self, char_target, round_count):
        act_list = []

        # 每三回合触发一次技能，造成18点元素伤害，对方命中率下降25%;否则元素普攻
        if round_count % 3 == 0:
            # 是否被抵抗
            flag = random.uniform(0, 1)
            if flag < char_target.skill_resist_rate:
                hit_num = 0
                # 如果是呆鹅，额外承受30伤害
                if char_target.name == 'Durandal':
                    act_list += [['SELF', 'HEALTH', 30, -1]]
            else:
                hit_num = 18
                char_target.hit_rate -= 0.25
        else:
            [hit_num_tmp, hit_flag] = self.gen_attack(char_target)
            if hit_flag == 1:
                hit_num = hit_num_tmp
            else:
                hit_num = 0

        act_list += [['TARGET', 'HEALTH', positive_number(hit_num)*self.damage_rate, -1]]
        return act_list


'''工具函数：小于0取0'''
def positive_number(num):
    if num<0:
        return 0
    return num
