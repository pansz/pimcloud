# coding=utf-8
# Author: Pan, Shi Zhu

from genziku import *
import data

def qpsp_init():
    pinyin_table = data.get(data.get_py_table)

    reverse_table = {}
    if pinyin_table["__type__"] == "shuangpin":
        for k,v in pinyin_table.iteritems():
            if k[0:7] == "__alias":
                continue
            if reverse_table.has_key(v):
                if (reverse_table[v] < k):
                    print v, reverse_table[v], "=>", v, k 
                    reverse_table[v] = k
            else:
                if k == "__type__":
                    reverse_table[k] = v
                else:
                    reverse_table[v] = k
        return reverse_table
    elif pinyin_table["__type__"] == "quanpin":
        return pinyin_table
    else:
        print "invalid pinyin table file"
        return reverse_table

def qpsp_conv(input, rt):
    ret = ""
    for item in input.split("'"):
        if item == "":
            continue
        if rt["__type__"] == "shuangpin":
            # 双字词只允许最后一个缺韵母，如果前一个字缺韵母则直接退出
            if len(ret) == 1:
                return ""
            if rt.has_key(item):
                ret += rt[item]
            else:
                print "error: no match for ", item
                ret += item
        elif rt["__type__"] == "quanpin":
            return input
    return ret

def word_init(fin):
    word_table = {}
    for line in fin:
        items = line[:-1].split(" ")
        key = items[0]
        value = items[1]
        if word_table.has_key(key):
            word_table[key].append(value)
        else:
            word_table[key] = [ value ]
    return word_table

def word_init_bak(zk):
    print "init word table"
    word_table = {}
    for k, v in zk.iteritems():
        for i in v[2]:
            if len(i) != 3:
                break
            if re.compile("^[zcs]$").match(k):
                break
            if word_table.has_key(i):
                word_table[i].append(k)
            else:
                word_table[i] = [ k ]
            pass
        pass
    return word_table

def needcheck(spkey, qpkey):
    # 单字
    if re.compile("^[zcs]h$").match(qpkey):
        return True
    if re.compile("^[zcs]$").match(spkey):
        return True
    if re.compile("^o[aeo]$").match(spkey):
        return True
    # 第二字
    if re.compile("^..[zcs]$").match(spkey):
        return True
    if re.compile("^..o[aeo]$").match(spkey):
        return True
    # 第一字
    if re.compile("^o[aeo].$").match(spkey):
        return True
    if re.compile("^o[aeo]..$").match(spkey):
        return True
    # 其他
    return False

def validsingleword(w,k,t):
    if t.has_key(w):
        for i in t[w]:
            if i == k:
                return True
            if i[0:2] == "zh" and k == "z":
                continue
            if i[0:2] == "ch" and k == "c":
                continue
            if i[0:2] == "sh" and k == "s":
                continue
            if i[0] == "a" and len(i)>1 and k == "a":
                continue
            if i[0] == "e" and len(i)>1 and k == "e":
                continue
            if i[0] == "o" and len(i)>1 and k == "o":
                continue
            if i.startswith(k):
                return True
        else:
            return False
    else:
        return True

def wordcheck(key, wl, wt):
    output = ""
    for word in wl:
        if len(word) < 4:
            if validsingleword(word, key, wt):
                output += " " + word
        else:
            keys = key.split("'")
            if not validsingleword(word[0:3], keys[0], wt):
                continue
            if not validsingleword(word[3:6], keys[1], wt):
                continue
            output += " " + word
    return output

def main(mode):

    # don't worry, it will raise Exception for invalid mode
    data.setmode(mode)
    rt = qpsp_init()

    print "writing ",mode, "1"
    fin = open("quanpin1.txt", "r")
    f = open(mode+"1.txt", "w")
    try:
        for line in fin:
            items = line[:-1].split(" ")
            key = items[0]
            value = items[1]
            newvalue = qpsp_conv(value, rt)
            if newvalue == "":
                print "error at",key,value
                continue
            f.write(key+" "+newvalue+"\n")
    finally:
        f.close()
        fin.close()

    zk2 = getziku2()

    # write pinyin zk 2
    f = open(mode+"2.txt", "w")
    print "writing ",mode, "2"
    fin = open("quanpin1.txt", "r")
    wt = word_init(fin)
    fin.close
    try:
        for k,v in zk2.iteritems():
            newkey = qpsp_conv(v[0], rt)
            if newkey == "":
                continue

            if needcheck(newkey, k):
                str = wordcheck(k, v[2], wt)
                if str != "":
                    f.write(newkey+str+"\n")
            else:
                f.write(newkey+v[1]+"\n")
    finally:
        f.close()

    print "get level 3"
    jpzk3 = getsogou3()

    pyzk3 = getpyzk(jpzk3)
    # write pinyin zk 3
    f = open(mode+"3.txt", "w")
    print "writing ",mode,"3"
    try:
        for k,v in pyzk3.iteritems():
            newkey = qpsp_conv(v[0], rt)
            if newkey == "":
                print "error at", k, v[1]
                continue
            f.write(newkey+v[1]+"\n")
    finally:
        f.close()
    
    print "get level 4"
    jpzk4 = getsogou4()

    pyzk4 = getpyzk(jpzk4)
    # write pinyin zk 4
    f = open(mode+"4.txt", "w")
    print "writing ",mode,"4"
    try:
        for k,v in pyzk4.iteritems():
            newkey = qpsp_conv(v[0], rt)
            if newkey == "":
                print "error at", k, v[1]
                continue
            f.write(newkey+v[1]+"\n")
    finally:
        f.close()
    
    # finish
    print "finished. "

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("abc")

