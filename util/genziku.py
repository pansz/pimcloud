# coding=utf-8
# Author: Pan, Shi Zhu

import sys
import urllib
import re
import data
import time
from cPickle import *

pinyin_list = (
    "'a", "'ai", "'an", "'ang", "'ao", 'ba', 'bai', 'ban', 'bang', 'bao',
    'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo',
    'bu', 'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cen', 'ceng', 'cha',
    'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng', 'chi', 'chong',
    'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo',
    'ci', 'cong', 'cou', 'cu', 'cuan', 'cui', 'cun', 'cuo', 'da', 'dai',
    'dan', 'dang', 'dao', 'de', 'dei', 'deng', 'di', 'dia', 'dian', 'diao',
    'die', 'ding', 'diu', 'dong', 'dou', 'du', 'duan', 'dui', 'dun', 'duo',
    "'e", "'ei", "'en", "'er", 'fa', 'fan', 'fang', 'fei', 'fen',
    'feng', 'fiao', 'fo', 'fou', 'fu', 'ga', 'gai', 'gan', 'gang', 'gao',
    'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai', 'guan',
    'guang', 'gui', 'gun', 'guo', 'ha', 'hai', 'han', 'hang', 'hao', 'he',
    'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan', 'huang',
    'hui', 'hun', 'huo', 'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie',
    'jin', 'jing', 'jiong', 'jiu', 'ju', 'juan', 'jue', 'jun', 'ka', 'kai',
    'kan', 'kang', 'kao', 'ke', 'ken', 'keng', 'kong', 'kou', 'ku', 'kua',
    'kuai', 'kuan', 'kuang', 'kui', 'kun', 'kuo', 'la', 'lai', 'lan', 'lang',
    'lao', 'le', 'lei', 'leng', 'li', 'lia', 'lian', 'liang', 'liao', 'lie',
    'lin', 'ling', 'liu', 'long', 'lou', 'lu', 'luan', 'lue', 'lun', 'luo',
    'lv', 'ma', 'mai', 'man', 'mang', 'mao', 'me', 'mei', 'men', 'meng', 'mi',
    'mian', 'miao', 'mie', 'min', 'ming', 'miu', 'mo', 'mou', 'mu', 'na',
    'nai', 'nan', 'nang', 'nao', 'ne', 'nei', 'nen', 'neng', "'ng", 'ni',
    'nian', 'niang', 'niao', 'nie', 'nin', 'ning', 'niu', 'nong', 'nou', 'nu',
    'nuan', 'nue', 'nuo', 'nv', "'o", "'ou", 'pa', 'pai', 'pan', 'pang',
    'pao', 'pei', 'pen', 'peng', 'pi', 'pian', 'piao', 'pie', 'pin', 'ping',
    'po', 'pou', 'pu', 'qi', 'qia', 'qian', 'qiang', 'qiao', 'qie', 'qin',
    'qing', 'qiong', 'qiu', 'qu', 'quan', 'que', 'qun', 'ran', 'rang', 'rao',
    're', 'ren', 'reng', 'ri', 'rong', 'rou', 'ru', 'ruan', 'rui', 'run',
    'ruo', 'sa', 'sai', 'san', 'sang', 'sao', 'se', 'sen', 'seng', 'sha',
    'shai', 'shan', 'shang', 'shao', 'she', 'shei', 'shen', 'sheng', 'shi',
    'shou', 'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shui', 'shun', 'shuo',
    'si', 'song', 'sou', 'su', 'suan', 'sui', 'sun', 'suo', 'ta', 'tai',
    'tan', 'tang', 'tao', 'te', 'teng', 'ti', 'tian', 'tiao', 'tie', 'ting',
    'tong', 'tou', 'tu', 'tuan', 'tui', 'tun', 'tuo', 'wa', 'wai',
    'wan', 'wang', 'wei', 'wen', 'weng', 'wo', 'wu', 'xi', 'xia', 'xian',
    'xiang', 'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xu', 'xuan',
    'xue', 'xun', 'ya', 'yan', 'yang', 'yao', 'ye', 'yi', 'yin', 'ying', 'yo',
    'yong', 'you', 'yu', 'yuan', 'yue', 'yun', 'za', 'zai', 'zan', 'zang',
    'zao', 'ze', 'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao',
    'zhe', 'zhen', 'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai',
    'zhuan', 'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong', 'zou', 'zu',
    'zuan', 'zui', 'zun', 'zuo',
    "b", "p", "m", "f", "d", "t", "l", "n", "g", "k", "h",
            "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w")

def cloudcheck(keyb, wordnum):
    empty_zk = data.load_from_file("empty.p")
    if empty_zk.has_key(keyb):
        return keyb, "", []
    url = "http://web.pinyin.sogou.com/web_ime/get_ajax/%s.key" % keyb
    fh = urllib.urlopen(url)
    str = urllib.unquote(fh.read())
    try:
        exec(str)
    except Exception, (errno, strerror):
        print "Exception at",keyb," str='"+ str + "' errno=", errno, strerror
        return keyb, "", []
    ret = []
    if keyb != ime_query_key:
        print "fatal error! "+ keyb + " != " + ime_query_key
    retstr = ""
    for item in ime_query_res.split("+"):
        myitem = item.rstrip()
        index = myitem.find('：')
        if index == -1:
            continue
        pos = int(myitem[index+3:])
        if len(keyb) != pos:
            continue
        myitem = myitem[:index]
        if len(myitem) != (wordnum*3):
            continue
        if retstr.find(myitem) >= 0:
            continue
        retstr += " " + myitem
        ret.append(myitem)
    if retstr == "":
        empty_zk[keyb] = keyb
        data.save_to_file(empty_zk, "empty.p")
    else:
        print ime_query_key + retstr
    return ime_query_key, retstr, ret

def savefile(zk):
    print "saving file... "
    file = open('ziku2.p', 'wb')
    dump(zk, file, HIGHEST_PROTOCOL)
    file.close
    print "file saved."

def readfile():
    file = open('ziku2.p', "rb")
    print "loading file... "
    zk = load(file)
    file.close()
    return zk

jp_tuple = (
    "a", "o", "e",
    "b", "p", "m", "f", "d", "t", "l", "n", "g", "k", "h",
            "j", "q", "x", "r", "z", "c", "s", "y", "w")
def getsogou3():
    modified = False
    zk3 = data.load_from_file("ziku3.p")

    for k1 in jp_tuple:
        for k2 in jp_tuple:
            for k3 in jp_tuple:
                key = k1+"'"+k2+"'"+k3
                if zk3.has_key(key):
                    continue
                zk3[key] = cloudcheck(key, 3)
                if zk3[key][1] == "":
                    del zk3[key]
                else:
                    modified = True
        if modified:
            data.save_to_file(zk3, "ziku3.p")
            modified = False

    return zk3

def getsogou4():
    modified = False
    zk4 = data.load_from_file("ziku4.p")

    for k1 in jp_tuple:
        for k2 in jp_tuple:
            for k3 in jp_tuple:
                for k4 in jp_tuple:
                    key = k1+"'"+k2+"'"+k3+"'"+k4
                    if zk4.has_key(key):
                        continue
                    time.sleep(0.1)
                    zk4[key] = cloudcheck(key, 4)
                    if zk4[key][1] == "":
                        del zk4[key]
                    else:
                        modified = True
                        continue
                    if key == "j'd'b'c":
                        zk4[key] = key," 觉得不错 较短比长 结对编程 极地冰川 教得不错 极地冰虫 极端编程 建德苞茶 军队编成", \
["觉得不错","较短比长","结对编程","极地冰川","教得不错","极地冰虫","极端编程","建德苞茶","军队编成"]
                        modified = True
                    if key == "j'x'l'b":
                        zk4[key] = key," 就行了吧 江西老表 急性淋病 酱香萝卜", \
["就行了吧","江西老表","急性淋病","酱香萝卜"]
                        modified = True

            if modified:
                data.save_to_file(zk4, "ziku4.p")
                modified = False
    return zk4

def rlookup(item, jpkey, rtable):
    max = len(item)
    p = 0
    ret = ""
    jp = jpkey.split("'")
    while p*3 < max:
        start = p*3
        end = (p+1)*3
        key = item[start:end]
        if len(key) != 3:
            print "Fatal error, invalid key",repr(key),"in",item, jpkey
            return ""
        if item[start:start+6] == "什么":
            ret += "shen'me'"
            p += 2
            continue
        if rtable.has_key(key):
            rl = rtable[key]
            if len(rl) > 1:
                count = 0
                matchstr = 0
                for match in rl:
                    if match[0:1] == jp[p]:
                        count += 1
                        matchstr = match
                if count == 1:
                    ret += matchstr + "'"
                elif count == 0:
                    print "not found, ",key,rl,"in",item,"for",jp[p]
                    return ""
                else:
                    print "duplicate", key, rl, "in", item
                    return ""
            else:
                ret += rl[0] + "'"
        else:
            print "Fatal error, key",key,"not found in",item,jpkey
            return ""
        p += 1
    return ret.rstrip("'")

def getpyzk(jpzk):
    rt = {}
    f = open("quanpin1.txt")
    try:
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            item = items[1]
            if rt.has_key(key):
                rt[key].append(item)
            else:
                rt[key] = [item]
    finally:
        f.close()

    pyzk = {}
    for k, v in jpzk.iteritems():
        for item in v[2]:
            key = rlookup(item, k, rt)
            if key == "":
                continue
            if pyzk.has_key(key):
                v0, v1, v2 = pyzk[key]
                v1 += " " + item
                v2.append(item)
                pyzk[key] = v0, v1, v2
            else:
                pyzk[key] = key, " "+item, [item]
    return pyzk

def getziku2():
    modified = False
    try:
        zk = readfile()
        print "resume from old zk file"
    except Exception, (errno, strerror):
        zk = {}
        print "creating new zk file"
    # create level 1 zk
    print "get level 1"
    for keyb in pinyin_list:
        mykeyb = keyb.lstrip("'")
        if zk.has_key(mykeyb):
            continue
        zk[mykeyb] = cloudcheck(mykeyb, 1)
        if zk[mykeyb][1] == "":
            del zk[mykeyb]
        else:
            modified = True

    if modified:
        savefile(zk)
        modified = False

    # create level 2 zk
    print "get level 2"
    for keyb in pinyin_list:
        mykeyb = keyb.lstrip("'")
        for keyb2 in pinyin_list:
            if keyb2[0] == "'":
                mykeyb2 = mykeyb + keyb2
            else:
                mykeyb2 = mykeyb + "'" + keyb2
            if zk.has_key(mykeyb2):
                continue
            zk[mykeyb2] = cloudcheck(mykeyb2, 2)
            if zk[mykeyb2][1] == "":
                del zk[mykeyb2]
            else:
                modified = True
                continue
            if mykeyb2 == "wan'zhuai":
                zk[mykeyb2] = "wan'zhuai", " 玩拽", ["玩拽"]
                modified = True

        if modified:
            savefile(zk)
            modified = False

    # import pinyin zk
    f = open("ziku1.txt")
    try:
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            for item in items[1:]:
                if zk.has_key(key):
                    if zk[key][1].find(item) >= 0:
                        continue
                    zk[key][2].append(item)
                    zk[key] = key, zk[key][1]+" "+item, zk[key][2]
                else:
                    zk[key] = key, " "+item, [item]
    finally:
        f.close()

    if modified:
        savefile(zk)
        modified = False

    # import 3000.txt
    f = open("3000.txt")
    try:
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            for item in items[1:]:
                if zk.has_key(key):
                    if zk[key][1].find(item) >= 0:
                        continue
                    zk[key][2].append(item)
                    zk[key] = key, zk[key][1]+" "+item, zk[key][2]
                else:
                    zk[key] = key, " "+item, [item]
    finally:
        f.close()

    return zk
