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

import socket
import urllib
import data
import mypwd

try:
    socket.setdefaulttimeout(1)
except Exception:
    # ignore exception in GAE
    pass


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
            elif c in punctmap:
                if c == '"':
                    if g_double_quote_mode:
                        intmed += punctmap[c][0:3]
                    else:
                        intmed += punctmap[c][3:6]
                    g_double_quote_mode = not g_double_quote_mode
                else:
                    intmed += punctmap[c]
            elif uimode == mode_i and (c in imodemap):
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
    bchar = ""          # work around for new sogou py
    while index < lenitem:
        if not item[index].islower():
            index += 1
            continue
        # support user ziku, uimode only start at index 0
        if index == 0 and item[index] in qptable["__uimode__"]:
            index += 1
            if index < lenitem:
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
            if matchstr in qptable:
                # special case for fanguo, which should be fan'guo
                tempstr = item[end-1:end+1]
                if tempstr == "gu" or tempstr == "nu" or tempstr == "ni":
                    if matchstr[:-1] in qptable:
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
                    if matchstr[:-1] in qptable:
                        i -= 1
                        matchstr = matchstr[:-1]
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((matchstr, len(pinyinstr)))
                pinyinstr += qptable[matchstr] + bchar

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
            pinyinstr += item[index] + bchar
            index += 1
            word_count += 1
    itmmap[word_count] = filter_glyph(item[last_word_ptr:], qptable)
    ptrmap["word_count"] = word_count  # 经分析出的总字数
    pinyinstr = pinyinstr.rstrip(bchar)
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
    bchar = "'"         # work around for new sogou py
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
            if sp1 in sptable:
                # the last odd shuangpin code are output as only shengmu
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((sp1, len(pinyinstr)))
                pinyinstr += sptable[sp1]+bchar
            elif sp1 in alias1:
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((alias2[sp1], len(pinyinstr)))
                pinyinstr += alias1[sp1]+bchar
            else:
                # invalid shuangpin code
                ptrmap[len(pinyinstr)] = index
                pinyinlist.append((sp1, len(pinyinstr)))
                pinyinstr += sp1 + bchar
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
    pinyinstr = pinyinstr.rstrip(bchar)
    ptrmap[len(pinyinstr)] = index
    pinyinlist.append(("", len(pinyinstr)))
    ptrmap["pinyinstr"] = pinyinstr
    ptrmap["itmmap"] = itmmap
    ptrmap["pinyinlist"] = pinyinlist
    ptrmap["originput"] = item.translate(data.g_asctable, data.g_numchars)
    ptrmap["pytype"] = "shuangpin"

    return ptrmap

def clear_glyph_cache():
    global g_glyph_cache
    global g_glyph_first
    g_glyph_cache = []
    g_glyph_first = True

def get_choice(hint):
    lh = len(hint)
    for tl in range(lh):
        for sl in range(lh-tl):
            yield hint[sl:sl+tl+1]

def check_glyph(newoutput, hint, matchword):
    global g_glyph_cache
    global g_glyph_first
    if g_glyph_first:
        g_glyph_first = False
        g_glyph_cache.append("_")
        if matchword == "":
            return newoutput, "_"
        else:
            return "", ""
    if hint.find(matchword) < 0:
        newoutput = ""
    if g_glyph_cache != []:
        for key in get_choice(hint):
            for item in g_glyph_cache:
                if item.find(key) >= 0:
                    # jump to outter for loop
                    break
            else:
                g_glyph_cache.append(key)
                if matchword != "":
                    if key.startswith(matchword):
                        return newoutput, key[len(matchword):]
                    else:
                        return "", ""
                else:
                    return newoutput, key
    g_glyph_cache.append(hint)
    return newoutput, "_"

# 插入中间的非中文输入到返回文字中，并进行附加的形码本地解析
def process(item, tmap, rzk):
    unitem = unicode(item,"utf-8")
    wc = len(unitem)            # 本次匹配码长
    twc = tmap["word_count"]     # 总期望码长
    # 如果搜索返回了大于期望字长的字，则忽略
    if wc > twc:
        return "", ""
    outlist = [tmap["itmmap"][0][0], tmap["itmmap"][0][1]]
    for i in xrange(wc):
        outlist.append(unitem[i].encode("utf-8"))
        if (i+1) in tmap["itmmap"]:
            outlist.append(tmap["itmmap"][i+1][1])
    newoutput = "".join(outlist)
    # calculate hint
    hint = "_"
    matchword = tmap["itmmap"][twc][0]
    if wc == 1:
        if item in rzk:
            hint = rzk[item]
        else:
            if twc > 1:
                # 对于多字输入的情形，隐藏不含形码的单字。
                return "", ""
    elif wc == 2:
        key1 = unitem[0].encode("utf-8")
        key2 = unitem[1].encode("utf-8")
        if key1 in rzk and key2 in rzk:
            hint = rzk[key1][0:2] + rzk[key2][0:2]
    elif wc == 3:
        key1 = unitem[0].encode("utf-8")
        key2 = unitem[1].encode("utf-8")
        key3 = unitem[2].encode("utf-8")
        if key1 in rzk and key2 in rzk and key3 in rzk:
            hint = rzk[key1][0] + rzk[key2][0] + rzk[key3][0:2]
    elif wc >= 4:
        key1 = unitem[0].encode("utf-8")
        key2 = unitem[1].encode("utf-8")
        key3 = unitem[2].encode("utf-8")
        key4 = unitem[-1].encode("utf-8")
        if key1 in rzk and key2 in rzk and key3 in rzk and key4 in rzk:
            hint = rzk[key1][0] + rzk[key2][0] + rzk[key3][0] + rzk[key4][0]
    # filter words according to the hint
    if len(hint) > 1 and wc == twc:
        return check_glyph(newoutput, hint, matchword)
    elif matchword == "":
        return newoutput, hint
    else:
        return "", ""
    #return newoutput, hint

def ime_callback(istr, keyb, dummy):
    ret = []
    for item in istr.split("\t+"):
        k,h,v = item.partition("：")
        ret.append((k,int(v)))
    return ret

def sogou_cloud_check(kbmap):
    kbpy = kbmap["pinyinstr"]
    keyb = kbpy.replace("'", "")
    if keyb in data.g_remote_dict:
        ret = data.g_remote_dict.get(keyb,[])
    else:
        # check cloud
        #url = "http://web.pinyin.sogou.com/web_ime/get_ajax/%s.key" % kbmap["pinyinstr"]
        url = "http://web.pinyin.sogou.com/api/py?key=938cdfe9e1e39f8dd5da428b1a6a69cb&query="+keyb
        fh = urllib.urlopen(url)
        try:
            remotestr = fh.read()
            sstr = urllib.unquote(remotestr)
        except Exception:
            sstr = ""
        fh.close()
        if sstr.startswith("ime_callback"):
            try:
                exec("ret = "+sstr)
            except Exception, inst:
                print "Exception at "+keyb, "str='"+ sstr+ "'",type(inst).__name__, inst
                ret = []
        else:
            print "Error at "+keyb, "str='"+ sstr+ "'"
            ret = []
        if ret != []:
            data.g_remote_dict[keyb] = ret

    if len(kbpy) != len(keyb):
        # has quote
        qret = []
        wc = kbmap["word_count"]
        for a in ret:
            la = len(unicode(a[0],"utf-8"))
            if la > wc:
                la = wc
            qret.append((a[0], kbmap["pinyinlist"][la][1]))
        return qret
    else:
        return ret

def qq_cloud_check(kbmap):
    keyb = kbmap["pinyinstr"]
    if keyb in data.g_remote_dict:
        ret = data.g_remote_dict.get(keyb,[])
    else:
        # here we use 999 as uid, other IME should use something else and
        # get the key from http://ime.qq.com/fcgi-bin/getkey?callback=window.QQWebIME.keyback999
        # where the last 999 should be replaced with new UID between 900 and 998
        url = "http://ime.qq.com/fcgi-bin/getword?key=3e362ac8ddffd39a084ef6db48314f79&callback=window.QQWebIME.callback999&q="+keyb
        fh = urllib.urlopen(url)
        remotestr = ""
        try:
            remotestr = fh.read().strip()
            print repr(remotestr)
            if remotestr.startswith("window.QQWebIME.callback999"):
                exec("qret = "+remotestr.replace("window.QQWebIME.callback999(","").rstrip(")"))
                print type(qret).__name__, repr(qret)
            ret = []
            la = len(qret["rs"])
            for i in range(0,la):
                idx = int(qret["rsn"][i])
                if idx in kbmap:
                    ret.append((qret["rs"][i], idx))
            if ret != []:
                data.g_remote_dict[keyb] = ret
        except Exception, inst:
            print "Exception at "+keyb, "str='"+ remotestr+ "'",type(inst).__name__, inst
            ret = []
        fh.close()
    return ret

def baidu_cloud_check(kbmap):
    keyb = kbmap["pinyinstr"]
    if False:
        ret = data.g_remote_dict.get(keyb,[])
    else:
        url = "http://olime.baidu.com/py?py="+keyb+"&rn=0&pn=30&t=1294821263957"
        fh = urllib.urlopen(url)
        remotestr = ""
        try:
            remotestr = fh.read()
            exec("bret = "+remotestr)
            ret = []
            wc = kbmap["word_count"]
            for u in bret[0]:
                txt = u[0].decode("gbk")
                la = len(txt)
                if la > wc:
                    la = wc
                ret.append((txt.encode("utf-8"), kbmap["pinyinlist"][la][1]))
            if ret != []:
                data.g_remote_dict[keyb] = ret
        except Exception, inst:
            print "Exception at "+keyb, "str='"+ remotestr+ "'",type(inst).__name__, inst
            ret = []
        fh.close()
        pass
    return ret

def google_cloud_check(kbmap):
    keyb = kbmap["pinyinstr"]
    if keyb in data.g_remote_dict:
        ret = data.g_remote_dict.get(keyb,[])
    else:
        url = "http://www.google.com/transliterate?tl_app=3&tlqt=1&num=30&langpair=en|zh&text="+keyb
        fh = urllib.urlopen(url)
        remotestr = ""
        try:
            remotestr = fh.read().replace('"\\u','u"\\u').lstrip("\n")
            exec("gret = "+remotestr)
            ret = []
            wc = kbmap["word_count"]
            for u in gret[0]['hws']:
                la = len(u)
                if la > wc:
                    la = wc
                ret.append((u.encode("utf-8"),kbmap["pinyinlist"][la][1]))
            if ret != []:
                data.g_remote_dict[keyb] = ret
        except Exception, inst:
            print "Exception at "+keyb, "str='"+ remotestr+ "'",type(inst).__name__, inst
            ret = []
        fh.close()
    return ret

# 解析用户本地字典
def userzk_check(kbmap):
    ret = []
    userzk = data.get(data.load_alpha_userzk)
    pys = kbmap["pinyinstr"]
    pyl = kbmap["pinyinlist"]
    ori = kbmap["originput"]
    wc = kbmap["word_count"]
    if kbmap["pytype"] == "quanpin":
        # 按全部解析出的输入判定
        index = pyl[wc][1]
        key = ori
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
        # 按带断字符的方式判定
        key = pys
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    else:
        # 按原始输入来检查用户词库，支持不带断字符的双拼原始码用户词库
        index = pyl[wc][1]
        key = ori
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    return ret

# 解析云端数据，同时兼顾本地用户数据
def remote_parse(kbmap, debug):

    try:
        ret = userzk_check(kbmap)
        if len(ret) > 0:
            return ret
    except Exception:
        pass

    # ret = sogou_cloud_check(kbmap)
    ret = baidu_cloud_check(kbmap)
    #ret = google_cloud_check(kbmap)

    if debug:
        ret.append((kbmap["pinyinstr"], -1))
    kbmap["remote_flag"] = True
    return ret

# 根据 list 获取拼音
def getshuangpin(pyl, wc):
    ret = []
    for i in range(wc):
        ret.append(pyl[i][0])
    return "".join(ret), pyl[wc][1]
def getquanpin(pyl, wc):
    ret = []
    for i in range(wc):
        ret.append(pyl[i][0])
    return "'".join(ret), pyl[wc][1]

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
    if not g_gae:
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
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
        # 按带断字符的方式判定
        key = pys
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    except Exception:
        pass

    # 分别解析多字词、双字词和单字。
    if not g_gae:
        if wc >= 4:
            key, index = getquanpin(pyl, 4)
            if key in zk4:
                for item in zk4[key].split(" "):
                    ret.append((item, index))
        elif wc == 3:
            key, index = getquanpin(pyl, 3)
            if key in zk3:
                for item in zk3[key].split(" "):
                    ret.append((item, index))
    if wc > 1:
        key, index = getquanpin(pyl, 2)
        if key in zk:
            for item in zk[key].split(" "):
                ret.append((item, index))
    if wc > 0:
        key, index = getquanpin(pyl, 1)
        if key in zk:
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
    if not g_gae:
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
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
        # 按带断字符的方式判定
        key = pys
        if key in userzk:
            for item in userzk[key].split(" "):
                if item[0] == "#":
                    break
                ret.append((item, index))
    except Exception:
        pass

    # 分别解析多字词、双字词和单字。
    if not g_gae:
        if wc == 4 or wc > 5:
            key, index = getshuangpin(pyl, 4)
            if key in zk4:
                for item in zk4[key].split(" "):
                    ret.append((item, index))
        if wc == 3 or wc > 4:
            key, index = getshuangpin(pyl, 3)
            if key in zk3:
                for item in zk3[key].split(" "):
                    ret.append((item, index))
    if wc >= 2:
        key, index = getshuangpin(pyl, 2)
        if key in zk:
            for item in zk[key].split(" "):
                ret.append((item, index))
    if wc == 1 or wc == 2:
        key, index = getshuangpin(pyl, 1)
        if key in zk:
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
def parse_glyph(tmap):
    ret = []
    tzk = data.get(data.load_tree_xmzk)
    rzk = data.get(data.load_reverse_pyzk)
    xmcode = tmap["itmmap"][0][0]
    intermed = tmap["itmmap"][0][1]
    wordptr = tmap[0]
    mzk = tzk
    for k in xmcode:
        if k in mzk:
            lzk, mzk = mzk, mzk[k]
            if type(mzk).__name__ == "list":
                for item in mzk:
                    if item in rzk:
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
            if item in rzk:
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
    elif k == "savecache":
        data.save_remote_dict()
        return True
    else:
        return False

# 全拼和双拼的解析应当尽量分离
# 因为全拼要支持简拼，而简拼会把双拼搞乱，完全分离全拼和双拼是很必要的。
# 虽然有一部分重复代码，但我们为代码分离提供了方便。
def quanpin_parse(keyb, debug):
    pinyin_table = data.get(data.get_py_table)
    pytype = pinyin_table["__type__"]
    tmap = quanpin_transform(keyb, pinyin_table)
    if debug:
        print tmap

    if tmap["word_count"] == 0:
        result = [("",0)]
    elif tmap["word_count"] < 3 and g_gae:
        result = local_parse_quanpin(tmap, debug)
    elif tmap["word_count"] < 5 and not g_gae:
        result = local_parse_quanpin(tmap, debug)
    else:
        # 当远程解析超时或者无结果时，启用本地解析
        result = remote_parse(tmap, debug)
        if len(result) <= 1:
            result = local_parse_quanpin(tmap, debug)

    xmcode = tmap["itmmap"][0][0]
    if len(xmcode) > 0 and tmap["word_count"] == 0:
        # 解析纯笔形模式，仅当无任何拼音输入时才进入此模式
        ret = parse_glyph(tmap)
    else:
        ret = []
        rzk = data.get(data.load_reverse_xmzk)
        # 解析有拼音输入时的形码过滤
        clear_glyph_cache()
        for item,index in result:
            if index == -1:
                ret.append((item, "_", index))
                continue
            displayitem, hint = process(item, tmap, rzk)
            if displayitem == "":
                continue
            if index in tmap:
                ret.append((displayitem, hint, tmap[index]))
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
    tmap = shuangpin_transform(keyb, pinyin_table)
    if debug:
        print tmap

    if tmap["word_count"] == 0:
        result = [("",0)]
    elif tmap["word_count"] < 3 and g_gae:
        result = local_parse_shuangpin(tmap, debug)
    elif tmap["word_count"] < 5 and not g_gae:
        result = local_parse_shuangpin(tmap, debug)
        # 三字词本地词库不全
        if len(result) > 0 and tmap["word_count"] >= 3:
            finished = tmap.get(result[0][1],result[0][1])
            if finished < len(keyb):
                result2 = remote_parse(tmap, debug)
                if len(result2) > 1:
                    result = result2
    else:
        # 当远程解析超时或者无结果时，启用本地解析
        result = remote_parse(tmap, debug)
        if len(result) <= 1:
            result = local_parse_shuangpin(tmap, debug)

    xmcode = tmap["itmmap"][0][0]
    if len(xmcode) > 0 and tmap["word_count"] == 0:
        # 解析纯笔形模式，仅当无任何拼音输入时才进入此模式
        ret = parse_glyph(tmap)
    else:
        ret = []
        rzk = data.get(data.load_reverse_xmzk)
        # 解析有拼音输入时的形码过滤
        clear_glyph_cache()
        for item,index in result:
            if index == -1:
                ret.append((item, "_", index))
                continue
            displayitem, hint = process(item, tmap, rzk)
            if displayitem == "":
                continue
            if index in tmap:
                ret.append((displayitem, hint, tmap[index]))
            else:
                ret.append((displayitem, hint, index))
            if len(ret) >= data.g_maxoutput:
                break
        if debug:
            ret.append((keyb, "_", -1))
    if debug:
        print " %d 个结果：缺省为 %s => %s，提示信息为 %s" % (len(ret)-1, keyb, ret[0][0], ret[0][1])
    return ret

# TODO: 自然码解析
def nature_parse(keyb, debug):
    retu = []
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
        if pykb in pyzk:
            items = pyzk[pykb][1]
            for item in items.split(" "):
                ret.append((item, "", len(keyb)))
    else:
        wbzk = data.get(data.load_alpha_xmzk2)
        if keyb in wbzk:
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
        "quanpin": quanpin_parse,
        "abc": shuangpin_parse,
        "ms": shuangpin_parse,
        "nature": nature_parse,
        "plusplus": shuangpin_parse,
        "purple": shuangpin_parse,
        "wubi": wubi_parse,
        "pwd": mypwd.parse,
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
    if mode in parsefunc:
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
    parse("womfzlaeli", debug=True)
    parse("__savecache", debug=True)
    print "self-test finished"

if __name__ == "__main__":
    selftest()
