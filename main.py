import pandas as pd
from Main import characters_v2 as char


def run():
    chars = ['Kiana', 'Mei', 'Bronya', 'Himeko', 'Rita', 'YaeAndKallen', 'Corvus', 'Theresa', 'Gemini', 'Selee', 'Durandal', 'Hua']
    game_amount = 100000
    char_a = None
    char_b = None
    save_list = []
    for i in range(len(chars)-1):
        for j in range(i+1, len(chars)):
            winners = []
            for count in range(game_amount):
                char_a = get_char(chars[i])
                char_b = get_char(chars[j])
                judgment = char.Judgment(char_a, char_b)
                winners += [judgment.game_begin()]
            save_list += [[char_a.name, char_b.name, winners.count(char_a.name)*1./game_amount,
                           winners.count(char_b.name)*1./game_amount, winners.count(char_a.name), winners.count(char_b.name)]]
            # print(save_list)

    result = pd.DataFrame(save_list, columns=['char_a', 'char_b', 'a_win_rate', 'b_win_rate', 'a_win_count', 'b_win_count'])
    result.to_csv('../Data/result_100000_v1.csv', index=None)
    print(result)


def test():
    judgment = char.Judgment(get_char('Selee'), get_char('Durandal'))
    judgment.game_begin()


"各人物构造Key,换成特定字符串好点"
def get_char(name):
    if name=='Kiana':
        return char.Kiana('Kiana', 100, 24, 11, 23, 1)
    if name=='Mei':
        return char.Mei('Mei', 100, 22, 12, 30, 1)
    if name=='Bronya':
        return char.Bronya('Bronya', 100, 21, 10, 20, 1)
    if name=='Himeko':
        return char.Himeko('Himeko', 100, 23, 9, 12, 1)
    if name=='Rita':
        return char.Rita('Rita', 100, 26, 11, 17, 1)
    if name=='YaeAndKallen':
        return char.YaeAndKallen('YaeAndKallen', 100, 20, 9, 18, 0)
    if name=='Corvus':
        return char.Corvus('Corvus', 100, 23, 14, 14, 1)
    if name=='Theresa':
        return char.Theresa('Theresa', 100, 19, 12, 22, 1)
    if name=='Gemini':
        return char.Gemini('Gemini', 100, 18, 10, 10, 0)
    if name=='Selee':
        return char.Selee('Selee', 100, 23, 13, 26, 1)
    if name=='Durandal':
        return char.Durandal('Durandal', 100, 19, 10, 15, 0)
    if name=='Hua':
        return char.Hua('Hua', 100, 17, 15, 16, 1)


if __name__ == '__main__':
    # test()
    run()
