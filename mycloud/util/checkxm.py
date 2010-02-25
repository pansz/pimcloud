#!/usr/bin/env python
# coding=utf-8
#
# 检查形码的完整性

import data

data.setmode("abc")

xmzk = data.get(data.load_reverse_xmzk)

zk2 = data.get(data.load_alpha_pyzk)

zk3 = data.get(data.load_alpha_pyzk3)

zk4 = data.get(data.load_alpha_pyzk4)

def checkitem(w):
    global found
    global foundcount
    global notfound
    global notfoundcount
    global xmzk

    if xmzk.has_key(w):
        if found.has_key(w):
            pass
        else:
            found[w] = xmzk[w]
            foundcount += 1
    else:
        if notfound.has_key(w):
            pass
        else:
            notfound[w] = w
            notfoundcount += 1
            print "not found", w, "in xmzk"

foundcount = 0
found = {}
notfoundcount = 0
notfound = {}

print "check level 2 zk"
for k, v in zk2.iteritems():
    for item in v.split(" "):
        if len(item) != 6:
            continue
        checkitem(item[0:3])
        checkitem(item[3:6])
print "matched",foundcount,"words", "not found", notfoundcount,"words"

print "check level 3 zk"
for k, v in zk3.iteritems():
    for item in v.split(" "):
        if len(item) != 9:
            continue
        checkitem(item[0:3])
        checkitem(item[3:6])
        checkitem(item[6:9])
print "matched",foundcount,"words", "not found", notfoundcount,"words"

print "check level 4 zk"
for k, v in zk4.iteritems():
    for item in v.split(" "):
        if len(item) != 12:
            continue
        checkitem(item[0:3])
        checkitem(item[3:6])
        checkitem(item[6:9])
        checkitem(item[9:12])
print "matched",foundcount,"words", "not found", notfoundcount,"words"

