# coding=utf-8
# create shuangpin->quanpin convertion table for most styles
"""
    data for mycloud server

    Copyright (C) 2010  Pan, Shi Zhu

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import sys
import string
import os.path
import cPickle

# list of all valid pinyin, don't add other pinyin to this list,
# otherwise, shuangpin will break miserably
pinyin_list = (
    "'a", "'ai", "'an", "'ang", "'ao", 'ba', 'bai', 'ban', 'bang', 'bao',
    'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo',
    'bu', 'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cen', 'ceng', 'cha',
    'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng', 'chi', 'chong',
    'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo',
    'ci', 'cong', 'cou', 'cu', 'cuan', 'cui', 'cun', 'cuo', 'da', 'dai',
    'dan', 'dang', 'dao', 'de', 'dei', 'deng', 'di', 'dia', 'dian', 'diao',
    'die', 'ding', 'diu', 'dong', 'dou', 'du', 'duan', 'dui', 'dun', 'duo',
    "'e", "'ei", "'en", "'er", 'fa', 'fan', 'fang', 'fe', 'fei', 'fen',
    'feng', 'fiao', 'fo', 'fou', 'fu', 'ga', 'gai', 'gan', 'gang', 'gao',
    'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai', 'guan',
    'guang', 'gui', 'gun', 'guo', 'ha', 'hai', 'han', 'hang', 'hao', 'he',
    'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan', 'huang',
    'hui', 'hun', 'huo', "'i", 'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie',
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
    'tong', 'tou', 'tu', 'tuan', 'tui', 'tun', 'tuo', "'u", "'v", 'wa', 'wai',
    'wan', 'wang', 'wei', 'wen', 'weng', 'wo', 'wu', 'xi', 'xia', 'xian',
    'xiang', 'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xu', 'xuan',
    'xue', 'xun', 'ya', 'yan', 'yang', 'yao', 'ye', 'yi', 'yin', 'ying', 'yo',
    'yong', 'you', 'yu', 'yuan', 'yue', 'yun', 'za', 'zai', 'zan', 'zang',
    'zao', 'ze', 'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao',
    'zhe', 'zhen', 'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai',
    'zhuan', 'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong', 'zou', 'zu',
    'zuan', 'zui', 'zun', 'zuo')

# 标点符号转换表
punctmap = {
        "," : "，",
        "." : "。",
        "<" : "『",
        ">" : "』",
        "?" : "？",
        "\\" : "、",
        "!" : "！",
        "$" : "￥",
        ":" : "：",
        ";" : "；",
        '"' : "【】",
        '(' : "（",
        ')' : "）",
        "@" : "・"
        }
punctmap_qp = {
        "," : "，",
        "." : "。",
        "<" : "『",
        ">" : "』",
        "?" : "？",
        "\\" : "、",
        "!" : "！",
        "$" : "￥",
        ":" : "：",
        ";" : "；",
        "`" : "『",
        "'" : "",
        '"' : "【】",
        '(' : "（",
        ')' : "）",
        "@" : "・"
        }

# i 模式映射表
imodemap = {
        "1" : "一",
        "2" : "二",
        "3" : "三",
        "4" : "四",
        "5" : "五",
        "6" : "六",
        "7" : "七",
        "8" : "八",
        "9" : "九",
        "0" : "〇",
        "+" : "加",
        "-" : "减",
        "*" : "乘",
        "/" : "除",
        "=" : "等于",
        "$" : "元",
        "q" : "千",
        "w" : "万",
        "e" : "亿",
        "r" : "日",
        "t" : "吨",
        "y" : "月",
        "u" : "微",
        "i" : "豪",
        "o" : "度",
        "p" : "磅",
        "a" : "秒",
        "s" : "十",
        "d" : "第",
        "f" : "分",
        "g" : "个",
        "h" : "时",
        "j" : "斤",
        "k" : "克",
        "l" : "里",
        "z" : "兆",
        "x" : "升",
        "c" : "厘",
        "v" : "",
        "b" : "百",
        "n" : "年",
        "m" : "米"
        }

g_cache = {}
# 全局缓存
def get(func):
    global g_cache
    if not g_mode in g_cache:
        g_cache[g_mode] = {}
    if not func in g_cache[g_mode]:
        g_cache[g_mode][func] = func()
    return g_cache[g_mode][func]

def create_quanpin_table():
    table = {}
    for key in pinyin_list:
        if key[0] == "'":
            table[key[1:]] = key[1:]
        else:
            table[key] = key
    for shengmu in ["b", "p", "m", "f", "d", "t", "l", "n", "g", "k", "h",
            "j", "q", "x", "zh", "ch", "sh", "r", "z", "c", "s", "y", "w"]:
        table[shengmu] = shengmu
    table["__type__"] = "quanpin"
    table["__uimode__"] = "ui"
    return table

def save_to_file(ob, fname):
    file = open(fname, 'wb')
    cPickle.dump(ob, file, cPickle.HIGHEST_PROTOCOL)
    file.close

def load_from_file(fname):
    try:
        file = open(fname, "rb")
        p = cPickle.load(file)
        file.close()
    except Exception:
        p = {}
    return p

try:
    g_dict_path = os.path.expanduser("~/.mycloud_cache")
except Exception:
    g_dict_path = "mycloud_cache"
g_remote_dict = load_from_file(g_dict_path)
def save_remote_dict():
    save_to_file(g_remote_dict, g_dict_path)

def create_shuangpin_table(rules):
    sptable = {}
    # generate table for shengmu-yunmu pairs match
    for key in pinyin_list:
        if key[1] == "h":
            shengmu = key[:2]
            yunmu = key[2:]
        else:
            shengmu = key[0]
            yunmu = key[1:]
        if shengmu in rules[0]:
            shuangpin_shengmu = rules[0][shengmu]
        else:
            print "error", shengmu, "not found"
            continue
        if yunmu in rules[1]:
            shuangpin_yunmu = rules[1][yunmu]
        else:
            print "error", yunmu, "not found"
            continue
        sp1 = shuangpin_shengmu+shuangpin_yunmu
        if sp1 in sptable:
            print "error", shengmu, yunmu, "=", sp1, "duplicate with", sptable[sp1]
        else:
            if key[0] == "'":
                sptable[sp1] = key[1:]
            else:
                sptable[sp1] = key
    # the jxqy+v special case handling
    # alias 1 is shuangpin vs. quanpin, alias 2 is shuangpin vs. shuangpin
    if g_mode == "abc" or g_mode == "purple":
        sptable["__alias1__"] = {"jv":"ju", "qv":"qu", "xv":"xu", "yv":"yu"}
        sptable["__alias2__"] = {"jv":"ju", "qv":"qu", "xv":"xu", "yv":"yu"}
    elif g_mode == "ms":
        sptable["__alias1__"] = {"jv":"jue", "qv":"que", "xv":"xue", "yv":"yue"}
        sptable["__alias2__"] = {"jv":"jt", "qv":"qt", "xv":"xt", "yv":"yt"}
    elif g_mode == "nature":
        sptable["__alias1__"] = {"jv":"ju", "qv":"qu", "xv":"xu", "yv":"yu", 
                "aa":"a", "ee":"e"}
        sptable["__alias2__"] = {"jv":"ju", "qv":"qu", "xv":"xu", "yv":"yu",
                "aa":"oa", "ee":"oe"}
    else:
        sptable["__alias1__"] = {}
        sptable["__alias2__"] = {}
    # the u i mode setting
    if g_mode == "abc":
        sptable["__uimode__"] = "ui"
    elif g_mode == "ms" or g_mode == "plusplus" or g_mode == "nature":
        sptable["__uimode__"] = "ae"
    elif g_mode == "purple":
        sptable["__uimode__"] = "ve"
    # generate table for shengmu-only match
    for key, value in rules[0].iteritems():
        if key[0] == "'":
            sptable[value] = ""
        else:
            sptable[value] = key
    # finished init sptable, will use in shuangpin_transform
    sptable["__type__"] = "shuangpin"
    return sptable

def shuangpin_generic():
    # generate the default value of shuangpin table
    shengmu_dict = {}
    for shengmu in ["b", "p", "m", "f", "d", "t", "l", "n", "g", "k", "h",
            "j", "q", "x", "r", "z", "c", "s", "y", "w"]:
        shengmu_dict[shengmu] = shengmu
    shengmu_dict["'"] = "o"
    yunmu_list = {}
    for yunmu in ["a", "o", "e", "i", "u", "v"]:
        yunmu_list[yunmu] = yunmu
    return shengmu_dict, yunmu_list

# 智能 ABC 双拼编码方案
def shuangpin_abc(rule):
    rule[0].update({ "zh":"a", "ch":"e", "sh":"v" })
    rule[1].update({
        "an":"j",  "ao":"k",  "ai":"l",  "ang":"h", 
        "ong":"s", "ou":"b", 
        "en":"f",  "er":"r",  "ei":"q",  "eng":"g", "ng":"g",
        "ia":"d",  "iu":"r",  "ie":"x",  "in":"c",  "ing":"y", 
        "iao":"z", "ian":"w", "iang":"t",           "iong":"s", 
        "un":"n",  "ua":"d",  "uo":"o",  "ue":"m",  "ui":"m", 
        "uai":"c", "uan":"p", "uang":"t" })
    return rule[0], rule[1]

# 微软拼音双拼编码方案
def shuangpin_microsoft(rule):
    rule[0].update({ "zh":"v", "ch":"i", "sh":"u" })
    rule[1].update({
        "an":"j", "ao":"k", "ai":"l", "ang":"h",
        "ong":"s", "ou":"b",
        "en":"f", "er":"r", "ei":"z", "eng":"g", "ng":"g",
        "ia":"w", "iu":"q", "ie":"x", "in":"n", "ing":";",
        "iao":"c", "ian":"m", "iang":"d", "iong":"s",
        "un":"p", "ua":"w", "uo":"o", "ue":"t", "ui":"v",
        "uai":"y", "uan":"r", "uang":"d" ,
        "v":"y"} )
    return rule[0], rule[1]

# 自然码双拼编码方案
def shuangpin_nature(rule):
    rule[0].update({ "zh":"v", "ch":"i", "sh":"u" })
    rule[1].update({
        "an":"j", "ao":"k", "ai":"l", "ang":"h",
        "ong":"s", "ou":"b",
        "en":"f", "er":"r", "ei":"z", "eng":"g", "ng":"g",
        "ia":"w", "iu":"q", "ie":"x", "in":"n", "ing":"y",
        "iao":"c", "ian":"m", "iang":"d", "iong":"s",
        "un":"p", "ua":"w", "uo":"o", "ue":"t", "ui":"v",
        "uai":"y", "uan":"r", "uang":"d" } )
    return rule[0], rule[1]

# 紫光双拼编码方案
def shuangpin_purple(rule):
    rule[0].update({ "zh":"u", "ch":"a", "sh":"i" })
    rule[1].update({
        "an":"r", "ao":"q", "ai":"p", "ang":"s",
        "ong":"h", "ou":"z",
        "en":"w", "er":"j", "ei":"k", "eng":"t", "ng":"t",
        "ia":"x", "iu":"j", "ie":"d", "in":"y", "ing":";",
        "iao":"b", "ian":"f", "iang":"g", "iong":"h",
        "un":"m", "ua":"x", "uo":"o", "ue":"n", "ui":"n",
        "uai":"y", "uan":"l", "uang":"g"} )
    return rule[0], rule[1]

# 拼音加加双拼编码方案
def shuangpin_plusplus(rule):
    rule[0].update({ "zh":"v", "ch":"u", "sh":"i" })
    rule[1].update({
        "an":"f", "ao":"d", "ai":"s", "ang":"g",
        "ong":"y", "ou":"p",
        "en":"r", "er":"q", "ei":"w", "eng":"t", "ng":"t",
        "ia":"b", "iu":"n", "ie":"m", "in":"l", "ing":"q",
        "iao":"k", "ian":"j", "iang":"h", "iong":"y",
        "un":"z", "ua":"b", "uo":"o", "ue":"x", "ui":"v",
        "uai":"x", "uan":"c", "uang":"h" } )
    return rule[0], rule[1]

def get_shuangpin_table(rule_func):
    rules = shuangpin_generic()
    rules = rule_func(rules)
    return create_shuangpin_table(rules)

# 载入用于反查的逆向字库
def load_reverse_zk(fname):
    f = open(fname)
    try:
        rzk = {}
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            for item in items[1:]:
                #if item in rzk:
                    #print "duplicated", item, "with", rzk[item], 'and', key
                rzk[item] = key
    finally:
        f.close()
    return rzk

# 载入只支持单个匹配的字库
def load_unique_zk(fname):
    f = open(fname)
    try:
        rzk = {}
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            #if key in rzk:
                #print "duplicated", key, "with", rzk[key], 'and', item
            rzk[key] = items[1]
    finally:
        f.close()
    return rzk

# 以树结构载入字库，可支持部分匹配
def load_tree_zk(fname):
    f = open(fname)
    try:
        tzk = {}
        for line in f:
            items = line[:-1].split(" ")
            mzk = tzk
            for k in items[0]:
                if not k in mzk:
                    mzk[k] = {}
                lzk, mzk = mzk, mzk[k]
            key = items[0][-1]
            if type(lzk[key]).__name__ == "dict":
                lzk[key] = []
            for item in items[1:]:
                lzk[key].append(item)
    finally:
        f.close()
    return tzk

# 载入自然形式的字库，只支持完全匹配
def load_alpha_zk(fname):
    f = open(fname)
    try:
        zk = {}
        for line in f:
            k,p,v = line.partition(" ")
            zk[k] = v[:-1]
    finally:
        f.close()
    return zk

dirname = os.path.dirname(sys.argv[0])
if dirname != "":
    dirname += "/"

# define file names
def load_reverse_xmzk():
    return load_reverse_zk(dirname+"4corner.txt")

def load_reverse_pyzk():
    return load_unique_zk(dirname+g_mode+"1.txt")

def load_tree_xmzk():
    return load_tree_zk(dirname+"4corner.txt")

def load_alpha_pyzk1():
    return load_alpha_zk(dirname+g_mode+"1.txt")

def load_alpha_pyzk2():
    return load_alpha_zk(dirname+g_mode+"2.txt")

def load_alpha_pyzk3():
    return load_alpha_zk(dirname+g_mode+"3.txt")

def load_alpha_pyzk4():
    return load_alpha_zk(dirname+g_mode+"4.txt")

def load_alpha_userzk():
    return load_alpha_zk(dirname+"user.txt")

def load_alpha_xmzk2():
    return load_alpha_zk(dirname+g_mode+"2.txt")

def get_punctmap():
    if g_mode == "quanpin":
        return punctmap_qp
    else:
        return punctmap

def get_imodemap():
    return imodemap

get_py_table = create_quanpin_table
g_mode = "quanpin"
g_maxoutput = 30

def getmode():
    return g_mode

def getmaxoutput():
    return g_maxoutput

def setmaxoutput(v):
    global g_maxoutput
    temp = int(v)
    if temp > 0:
        g_maxoutput = temp

def setmode(mode):
    global get_py_table
    global g_mode
    if g_mode == mode:
        return
    else:
        g_mode = mode
    if mode == "quanpin":
        get_py_table = create_quanpin_table
    elif mode == "abc":
        get_py_table = lambda : get_shuangpin_table(shuangpin_abc)
    elif mode == "ms":
        get_py_table = lambda : get_shuangpin_table(shuangpin_microsoft)
    elif mode == "plusplus":
        get_py_table = lambda : get_shuangpin_table(shuangpin_plusplus)
    elif mode == "purple":
        get_py_table = lambda : get_shuangpin_table(shuangpin_purple)
    elif mode == "nature":
        get_py_table = lambda : get_shuangpin_table(shuangpin_nature)
    elif mode == "wubi":
        # wubi uses quanpin as pinyin table
        get_py_table = create_quanpin_table
    elif mode == "pwd":
        pass
    else:
        raise ValueError, "invalid mode"

def getname():
    if g_mode == "quanpin":
        return "全拼"
    elif g_mode == "abc":
        return "智能双打"
    elif g_mode == "ms":
        return "微软双拼"
    elif g_mode == "plusplus":
        return "加加双拼"
    elif g_mode == "purple":
        return "紫光双拼"
    elif g_mode == "nature":
        return "自然码"
    elif g_mode == "wubi":
        return "五笔"
    elif g_mode == "zhuyin":
        return "注音"
    elif g_mode == "cangjie":
        return "仓颉"
    elif mode == "pwd":
        return "密码生成"
    else:
        raise ValueError, "invalid mode"

def getkeychars():
    if g_mode == "quanpin":
        return "[a-z0-9']"
    elif g_mode == "abc":
        return '[a-z0-9"]'
    elif g_mode == "ms":
        return "[a-z;]"
    elif g_mode == "plusplus":
        return "[a-z]"
    elif g_mode == "purple":
        return "[a-z;]"
    elif g_mode == "nature":
        return "[a-z']"
    elif g_mode == "wubi":
        return "[a-z`]"
    elif g_mode == "zhuyin":
        return "[a-z]"
    elif g_mode == "cangjie":
        return "[a-z]"
    elif g_mode == "pwd":
        return "[A-Za-z0-9@._]"
    else:
        raise ValueError, "invalid mode"

g_asctable = string.maketrans("","")
g_numchars = "0123456789"

# set test stuffs
if __name__ == "__main__":
    sp_rule_table = [ "abc", "ms", "nature", "purple", "plusplus" ]
    if len(sys.argv) < 2:
        print "no argument. valid ones:\n\t", sp_rule_table
    else:
        if sys.argv[1] == "quanpin":
            save_to_file(get_py_table(), 'pinyin_table.p')
        elif sys.argv[1] in sp_rule_table:
            save_to_file(get_shuangpin_table(sys.argv[1]), 'pinyin_table.p')
        else:
            print "invalid rule name, valid ones:\n\t", sp_rule_table
