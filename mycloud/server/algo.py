#!/usr/bin/env python
# coding=utf-8
"""
    main algo for mycloud server

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

import urllib
import data

# 显示 unicode
def getunicode(code):
    lencode = len(code)
    try:
        if lencode <= 1:
            ret = ""
        elif lencode == 5:
            ret = eval("u'\u"+code[1:]+"'").encode("utf-8")
        elif lencode >= 9:
            ret = eval("u'\U"+code[1:9]+"'").encode("utf-8")
        elif lencode > 1 and lencode < 5:
            ret = eval(("u'\u%4s'" % code[1:]).replace(" ", "0")).encode("utf-8")
        elif lencode > 5 and lencode < 9:
            ret = eval(("u'\U%8s'" % code[1:]).replace(" ", "0")).encode("utf-8")
    except Exception:
        return ""
    return ret

# 当前双引号是前引号还是后引号的标志
g_double_quote_mode = 1

# 解析中间输入，分离形码与其他字符，并转换符号，转换 i 与 u 的处理。
def filter_glyph(input, pt):
    global g_double_quote_mode
    punctmap = data.get(data.get_punctmap)
    imodemap = data.get(data.get_imodemap)
    glyph = ""
    intmed = ""
    mode_u = pt["__uimode__"][0]
    mode_i = pt["__uimode__"][1]
    mode_o = ""
    uimode = mode_o
    if len(input) == 1 and input[0] == mode_i:
        return "", "一"
    for c in input:
        if c.isdigit() and uimode == mode_o:
            glyph += c
        else:
            if c == mode_i and uimode == mode_o:
                uimode = c
            elif c == mode_u and uimode == mode_o:
                uimode = c
                intmed += c
            elif punctmap.has_key(c):
                if c == '"':
                    if g_double_quote_mode:
                        intmed += punctmap[c][0:3]
                    else:
                        intmed += punctmap[c][3:6]
                    g_double_quote_mode = not g_double_quote_mode
                else:
                    intmed += punctmap[c]
            elif uimode == mode_i and imodemap.has_key(c):
                intmed += imodemap[c]
            elif uimode[:1] == mode_u:
                uimode += c
            else:
                intmed += c
    if uimode[:1] == mode_u:
        intmed = intmed.replace(mode_u, getunicode(uimode))

    return glyph, intmed

# 全拼分解转换，返回断字后的全拼码，指针映射表，中间符号表
def quanpin_transform(item, qptable):
    pinyinstr = ""      # output string
    pinyinlist = []     # output list
    ptrmap = {}         # string index map
    itmmap = {}         # intermediate input map
    word_count = 0      # total word count

    last_word_ptr = 0
    index = 0
    lenitem = len(item)
    while index < lenitem:
        if not item[index].islower():
            index += 1
            continue
        # support user ziku, uimode only start at index 0
        if index == 0 and item[index] in qptable["__uimode__"]:
            index += 1
            if index < lenitem :
                while item[index] != "v":
                    index += 1
                    if index >= lenitem:
                        break
                else:
                    index += 1
            continue
        for i in range(6,0,-1):
            if len(item[index:]) < i:
                continue
            end = index+i
            matchstr = item[index:end]
            if qptable.has_key(matchstr):
                # special case for fanguo, which should be fan'guo 
                tempstr = item[end-1:end+1]
                if tempstr == "gu" or tempstr == "nu" or tempstr == "ni":
                    if qptable.has_key(matchstr[:-1]):
                        i -= 1
                        matchstr = matchstr[:-1]
                # this is for ibus' rule
                tempstr2 = item[end-2:end+2]
                tempstr3 = item[end-1:end+2]
                tempstr4 = item[end-1:end+3]
                if (tempstr == "ge" and tempstr3 != "ger") \
                or (tempstr == "ne" and tempstr3 != "ner") \
                or (tempstr4 == "gong" or tempstr3 == "gou") \
                or (tempstr4 == "nong" or tempstr3 == "nou") \
                or (tempstr == "ga" or tempstr == "na") \
                or tempstr2 == "ier":
                    if qptable.has_key(matchstr[:-1]):
                        i -= 1
                        matchstr = matchstr[:-1]
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((matchstr, len(pinyinstr)))
                pinyinstr += qptable[matchstr] + "'"

                itmmap[word_count] = filter_glyph(item[last_word_ptr:index], qptable)
                index += i
                word_count += 1
                last_word_ptr = index
                break
            else:
                continue
        else:
            print "error: no match for", item
            ptrmap[len(pinyinstr)] = index
            pinyinlist.append((item[index], len(pinyinstr)))
            pinyinstr += item[index] + "'"
            index += 1
            word_count += 1
    itmmap[word_count] = filter_glyph(item[last_word_ptr:], qptable)
    ptrmap["word_count"] = word_count  # 经分析出的总字数
    pinyinstr = pinyinstr.rstrip("'")
    ptrmap[len(pinyinstr)] = index
    pinyinlist.append(("", len(pinyinstr)))
    ptrmap["pinyinstr"] = pinyinstr    # 此处返回完全断字之后的字符串，符合搜狗云标准
    ptrmap["pinyinlist"] = pinyinlist  # 此处返回每个单个拼音的列表，适合本地处理
    ptrmap["itmmap"] = itmmap          # 字间的非字符，例如形码表，标点符号等
    ptrmap["originput"] = item.translate(data.g_asctable, data.g_numchars)         # 原始输入的字符
    ptrmap["pytype"] = "quanpin"
    return ptrmap

# 双拼分解转换，返回全拼码，指针映射表，中间符号表
def shuangpin_transform(item, sptable):
    lenitem = len(item)
    index = 0
    last_word_ptr = 0
    pinyinstr = ""      # the output quanpin string
    ptrmap = {}         # map the quanpin position to shuangpin position
    itmmap = {}         # map the word count to intemediate inputs
    pinyinlist = []     # word count list of shuangpin inputs
    word_count = 0
    alias1 = sptable["__alias1__"]
    alias2 = sptable["__alias2__"]
    while index < lenitem:
        if item[index].islower():
            if item[index] in sptable["__uimode__"]:
                index += 1
                if index < lenitem:
                    # uimode only ends with v, otherwise continue to the end
                    while item[index] != "v":
                        index += 1
                        if index >= lenitem:
                            break
                    else:
                        index += 1
                continue
            if lenitem == index+1:
                sp1 = item[index]
            elif item[index+1].islower():
                sp1 = item[index]+item[index+1]
            else:
                sp1 = item[index]
            itmmap[word_count] = filter_glyph(item[last_word_ptr:index], sptable)
            if sptable.has_key(sp1):
                # the last odd shuangpin code are output as only shengmu
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((sp1, len(pinyinstr)))
                pinyinstr += sptable[sp1]+"'"
            elif alias1.has_key(sp1):
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((alias2[sp1], len(pinyinstr)))
                pinyinstr += alias1[sp1]+"'"
            else:
                # invalid shuangpin code
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((sp1, len(pinyinstr)))
                pinyinstr += sp1 + "'"
            index += len(sp1)
            if index > lenitem:
                index = lenitem
            word_count += 1
            last_word_ptr = index
        else:
            # bypass all non-lowercase-characters
            index += 1
    itmmap[word_count] = filter_glyph(item[last_word_ptr:], sptable)
    ptrmap["word_count"] = word_count
    pinyinstr = pinyinstr.rstrip("'")
    ptrmap[len(pinyinstr)] = index
    pinyinlist.append(("", len(pinyinstr)))
    ptrmap["pinyinstr"] = pinyinstr
    ptrmap["itmmap"] = itmmap
    ptrmap["pinyinlist"] = pinyinlist
    ptrmap["originput"] = item.translate(data.g_asctable, data.g_numchars)
    ptrmap["pytype"] = "shuangpin"

    return ptrmap

# 插入中间的非中文输入到返回文字中，并进行附加的形码本地解析
def process(item, map, rzk):
    wc = len(item)/3
    twc = map["word_count"]
    newoutput = map["itmmap"][0][0] + map["itmmap"][0][1]
    for i in xrange(len(item)/3):
        start = i*3
        end = i*3+3
        if map["itmmap"].has_key(i+1):
            glyph = map["itmmap"][i+1][0]
            if glyph == "":
                newoutput += item[start:end]
            else:
                word = item[start:end]
                if rzk.has_key(word):
                    if rzk[word].startswith(glyph):
                        newoutput += word
                    else:
                        return "", ""
                else:
                    return "", ""
            newoutput += map["itmmap"][i+1][1]
        else:
            newoutput += item[start:end]
    # display hint
    if wc == 1:
        if rzk.has_key(item):
            start = len(map["itmmap"][wc][0])
            hint = rzk[item][start:]
        else:
            if twc > 1:
                # 对于多字输入的情形，隐藏不含形码的单字。
                return "", ""
            else:
                hint = "_"
    elif wc >= 2:
        if rzk.has_key(item[-3:]):
            start = len(map["itmmap"][wc][0])
            hint = rzk[item[-3:]][start:]
        else:
            hint = "_"
    else:
        hint = "_"
    return newoutput, hint

# 解析云端数据，同时兼顾本地用户数据
def remote_parse(kbmap, debug):
    ret = []

    try:
        userzk = data.get(data.load_alpha_userzk)
        pys = kbmap["pinyinstr"]
        pyl = kbmap["pinyinlist"]
        ori = kbmap["originput"]
        wc = kbmap["word_count"]
        if kbmap["pytype"] == "quanpin":
            # 按全部解析出的输入判定
            index = pyl[wc][1]
            key = ori
            if userzk.has_key(key):
                for item in userzk[key].split(" "):
                    if item[0] == "#":
                        break
                    ret.append((item, index))
            # 按带断字符的方式判定
            key = pys
            if userzk.has_key(key):
                for item in userzk[key].split(" "):
                    if item[0] == "#":
                        break
                    ret.append((item, index))
        else:
            # 按原始输入来检查用户词库，支持不带断字符的双拼原始码用户词库
            index = pyl[wc][1]
            key = ori
            if userzk.has_key(key):
                for item in userzk[key].split(" "):
                    if item[0] == "#":
                        break
                    ret.append((item, index))
    except Exception:
        pass
    if len(ret) > 0:
        return ret

    # check cloud
    url = "http://web.pinyin.sogou.com/web_ime/get_ajax/%s.key" % kbmap["pinyinstr"]
    fh = urllib.urlopen(url)
    remotestr = fh.read()
    str = urllib.unquote(remotestr)
    try:
        exec(str)
    except Exception, inst:
        print "Exception at "+kbmap["pinyinstr"], "str='"+ str+ "'",type(inst).__name__, inst
        return ret
    for item in ime_query_res.split("+"):
        myitem = item.rstrip()
        index = myitem.find('：')
        if index == -1:
            continue
        ret.append((myitem[:index], int(myitem[index+3:])))
    if debug:
        ret.append((ime_query_key, -1))
    kbmap["remote_flag"] = True
    return ret

# 根据 list 获取拼音
def getshuangpin(pyl, wc):
    ret = ""
    for i in range(wc):
        ret += pyl[i][0]
    return ret, pyl[wc][1]
def getquanpin(pyl, wc):
    ret = ""
    for i in range(wc):
        ret += pyl[i][0] + "'"
    return ret.rstrip("'"), pyl[wc][1]

# 利用本地词库进行解析，全拼将来要支持简拼功能
def local_parse_quanpin(kbmap, debug):
    ret = []
    pys = kbmap["pinyinstr"]
    pyl = kbmap["pinyinlist"]
    if pys == "":
        ret.append(("", pyl[0][1]))
        return ret
    wc = kbmap["word_count"]
    zk = data.get(data.load_alpha_pyzk2)
    if wc >= 3:
        zk3 = data.get(data.load_alpha_pyzk3)
    if wc >= 4:
        zk4 = data.get(data.load_alpha_pyzk4)
    try:
        userzk = data.get(data.load_alpha_userzk)
        ori = kbmap["originput"]

        # 按全部解析出的输入判定
        index = pyl[wc][1]
        key = ori
        if userzk.has_key(key):
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
        # 按带断字符的方式判定
        key = pys
        if userzk.has_key(key):
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    except Exception:
        pass

    # 分别解析多字词、双字词和单字。
    if wc >= 4:
        key, index = getquanpin(pyl, 4)
        if zk4.has_key(key):
            for item in zk4[key].split(" "):
                ret.append((item, index))
    elif wc == 3:
        key, index = getquanpin(pyl, 3)
        if zk3.has_key(key):
            for item in zk3[key].split(" "):
                ret.append((item, index))
    if wc > 1:
        key, index = getquanpin(pyl, 2)
        if zk.has_key(key):
            for item in zk[key].split(" "):
                ret.append((item, index))
    if wc > 0:
        key, index = getquanpin(pyl, 1)
        if zk.has_key(key):
            for item in zk[key].split(" "):
                ret.append((item, index))
    if len(ret) == 0:
        ret.append(("", pyl[0][1]))
    return ret

# 利用本地词库进行解析，双拼不必使用简拼
def local_parse_shuangpin(kbmap, debug):
    ret = []
    pys = kbmap["pinyinstr"]
    pyl = kbmap["pinyinlist"]
    if pys == "":
        ret.append(("", pyl[0][1]))
        return ret
    wc = kbmap["word_count"]
    zk = data.get(data.load_alpha_pyzk2)
    if wc == 3 or wc > 4:
        zk3 = data.get(data.load_alpha_pyzk3)
    if wc == 4 or wc > 5:
        zk4 = data.get(data.load_alpha_pyzk4)
    try:
        userzk = data.get(data.load_alpha_userzk)
        ori = kbmap["originput"]
        # 按原始输入来检查用户词库，支持不带断字符的双拼原始码用户词库
        index = pyl[wc][1]
        key = ori
        if userzk.has_key(key):
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
        # 按带断字符的方式判定
        key = pys
        if userzk.has_key(key):
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    except Exception:
        pass

    # 分别解析多字词、双字词和单字。
    if wc == 4 or wc > 5:
        key, index = getshuangpin(pyl, 4)
        if zk4.has_key(key):
            for item in zk4[key].split(" "):
                ret.append((item, index))
    if wc == 3 or wc > 4:
        key, index = getshuangpin(pyl, 3)
        if zk3.has_key(key):
            for item in zk3[key].split(" "):
                ret.append((item, index))
    if wc >= 2:
        key, index = getshuangpin(pyl, 2)
        if zk.has_key(key):
            for item in zk[key].split(" "):
                ret.append((item, index))
    if wc == 1 or wc == 2:
        key, index = getshuangpin(pyl, 1)
        if zk.has_key(key):
            for item in zk[key].split(" "):
                ret.append((item, index))
    if len(ret) == 0:
        ret.append(("", pyl[0][1]))
    return ret

def traverse_tree(mzk):
    if type(mzk).__name__ == "dict":
        ret = []
        for v in mzk.itervalues():
            ret += traverse_tree(v)
        return ret
    elif type(mzk).__name__ == "list":
        return mzk

    return []

# 解析纯四角号码输入，只允许输入单字。
def parse_glyph(map):
    ret = []
    tzk = data.get(data.load_tree_xmzk)
    rzk = data.get(data.load_reverse_pyzk)
    xmcode = map["itmmap"][0][0]
    intermed = map["itmmap"][0][1]
    wordptr = map[0]
    mzk = tzk
    for k in xmcode:
        if mzk.has_key(k):
            lzk, mzk = mzk, mzk[k]
            if type(mzk).__name__ == "list":
                for item in mzk:
                    if rzk.has_key(item):
                        ret.append((item+intermed, rzk[item], wordptr))
                    else:
                        ret.append((item+intermed, "", wordptr))
                break
        else:
            ret.append((intermed, "", wordptr))
            break
    else:
        # mzk is a dict and we have exhausted the loop, do traverse the tree
        xmzk = data.get(data.load_reverse_xmzk)
        retlist = traverse_tree(mzk)
        if len(retlist) >= data.g_maxoutput:
            retlist = retlist[0:data.g_maxoutput]
        retlist.sort()
        for item in retlist:
            start = len(xmcode)
            if rzk.has_key(item):
                ret.append((item+intermed, xmzk[item][start:]+rzk[item], wordptr))
            else:
                ret.append((item+intermed, xmzk[item][start:], wordptr))
    return ret

g_gae = False

# 处理内部控制输入
def internal_command(cmd, debug):
    global g_gae
    k,p,v = cmd.partition("=")
    if k == "setmode":
        if v == "":
            # 如果并不是有效的控制命令，作为普通输入返回回去
            return False
        data.setmode(v)
        if debug:
            print "setmode to", v
        return True
    elif k == "setmaxoutput":
        data.setmaxoutput(v)
        if debug:
            print "setmaxoutput to", v
        return True
    elif k == "isvalid":
        return True
    elif k == "getname":
        return data.getname()
    elif k == "getkeychars":
        return data.getkeychars()
    elif k == "setgae":
        g_gae = True
        return True
    else:
        return False

# 全拼和双拼的解析应当尽量分离
# 因为全拼要支持简拼，而简拼会把双拼搞乱，完全分离全拼和双拼是很必要的。
# 虽然有一部分重复代码，但我们为代码分离提供了方便。
def quanpin_parse(keyb, debug):
    pinyin_table = data.get(data.get_py_table)
    pytype = pinyin_table["__type__"]
    map = quanpin_transform(keyb, pinyin_table)
    if debug:
        print map

    if map["word_count"] == 0:
        result = [("",0)]
    elif map["word_count"] < 3 and g_gae:
        result = local_parse_quanpin(map, debug)
    elif map["word_count"] < 5 and not g_gae:
        result = local_parse_quanpin(map, debug)
    else:
        # 当远程解析超时或者无结果时，启用本地解析
        result = remote_parse(map, debug)
        if len(result) <= 1:
            result = local_parse_quanpin(map, debug)

    xmcode = map["itmmap"][0][0]
    if len(xmcode) > 0 and map["word_count"] == 0:
        # 解析纯笔形模式，仅当无任何拼音输入时才进入此模式
        ret = parse_glyph(map)
    else:
        ret = []
        rzk = data.get(data.load_reverse_xmzk)
        # 解析有拼音输入时的形码过滤
        for item,index in result:
            if index == -1:
                ret.append((item, "_", index))
                continue
            displayitem, hint = process(item, map, rzk)
            if displayitem == "":
                continue
            if map.has_key(index):
                ret.append((displayitem, hint, map[index]))
            else:
                ret.append((displayitem, hint, index))
            if len(ret) >= data.g_maxoutput:
                break
        if debug:
            ret.append((keyb, "_", -1))
    if debug:
        print " %d 个结果：缺省为 %s => %s，提示信息为 %s" % (len(ret)-1, keyb, ret[0][0], ret[0][1])
    return ret

def shuangpin_parse(keyb, debug):
    pinyin_table = data.get(data.get_py_table)
    pytype = pinyin_table["__type__"]
    map = shuangpin_transform(keyb, pinyin_table)
    if debug:
        print map

    if map["word_count"] == 0:
        result = [("",0)]
    elif map["word_count"] < 3 and g_gae:
        result = local_parse_shuangpin(map, debug)
    elif map["word_count"] < 5 and not g_gae:
        result = local_parse_shuangpin(map, debug)
    else:
        # 当远程解析超时或者无结果时，启用本地解析
        result = remote_parse(map, debug)
        if len(result) <= 1:
            result = local_parse_shuangpin(map, debug)

    xmcode = map["itmmap"][0][0]
    if len(xmcode) > 0 and map["word_count"] == 0:
        # 解析纯笔形模式，仅当无任何拼音输入时才进入此模式
        ret = parse_glyph(map)
    else:
        ret = []
        rzk = data.get(data.load_reverse_xmzk)
        # 解析有拼音输入时的形码过滤
        for item,index in result:
            if index == -1:
                ret.append((item, "_", index))
                continue
            displayitem, hint = process(item, map, rzk)
            if displayitem == "":
                continue
            if map.has_key(index):
                ret.append((displayitem, hint, map[index]))
            else:
                ret.append((displayitem, hint, index))
            if len(ret) >= data.g_maxoutput:
                break
        if debug:
            ret.append((keyb, "_", -1))
    if debug:
        print " %d 个结果：缺省为 %s => %s，提示信息为 %s" % (len(ret)-1, keyb, ret[0][0], ret[0][1])
    return ret

# TODO: 五笔解析
def wubi_parse(keyb, debug):
    lenkb = len(keyb)
    pinyin_mode = false
    ret = []
    if keyb[0] == "`":
        if lenkb > 1:
            pinyin_mode = true
        else:
            return ret
    if pinyin_mode:
        pykb = keyb.lstrip("`")
        pinyin_table = data.get(data.get_py_table)
        pyzk = data.get(data.load_alpha_pyzk1)
        if pyzk.has_key(pykb):
            items = pyzk[pykb][1]
            for item in items.split(" "):
                ret.append((item, "", len(keyb)))
    else:
        wbzk = data.get(data.load_alpha_xmzk2)
        if wbzk.has_key(keyb):
            items = wbzk[keyb][1]
            for item in items.split(" "):
                if len(item) > 0:
                    if item[0] == "~":
                        ret.append((item[1:], "", len(keyb)))
                    elif item[0] == "^":
                        ret.append((item[1:], "", len(keyb)))
                    else:
                        ret.append((item, "", len(keyb)))
        else:
            # try z-match
            pass
    return []

parsefunc = {
        "quanpin" : quanpin_parse,
        "abc" : shuangpin_parse,
        "ms" : shuangpin_parse,
        "nature" : shuangpin_parse,
        "plusplus" : shuangpin_parse,
        "purple" : shuangpin_parse,
        "wubi" : wubi_parse,
        }

# 主要的解析函数，决定解析方式。
def parse(keyb, debug=False):
    # 双下划线开头一律认为是控制指令
    if keyb[0:2] == "__":
        try:
            ret = internal_command(keyb[2:], debug)
        except Exception:
            ret = "False"
        if type(ret).__name__ != "str":
            ret = str(ret)
        return [(ret, "__", len(keyb))]
    mode = data.g_mode
    if parsefunc.has_key(mode):
        return parsefunc[mode](keyb, debug)
    else:
        return []

def selftest():
    print "start self-test"
    parse("fanguo", debug=True)
    parse("__setmode=quanpin", debug=True)
    parse("0010", debug=True)
    parse("ni", debug=True)
    parse("wo", debug=True)
    parse("ta", debug=True)
    parse("niwo", debug=True)
    parse("nita", debug=True)
    parse("wota", debug=True)
    parse("niwota", debug=True)
    parse("__setmode=abc", debug=True)
    parse("0010", debug=True)
    parse("ae", debug=True)
    parse("jw", debug=True)
    parse("fh", debug=True)
    parse("aejw", debug=True)
    parse("jwfh", debug=True)
    parse("fhae", debug=True)
    parse("aejwfh", debug=True)
    print "self-test finished"

if __name__ == "__main__":
    selftest()
