#!/usr/bin/env python
# coding: utf-8
"""
    pwdtool functions for mycloud server

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

import crypt, random, sys

KEYSTR = "poet"

def interlaced(p0, p1, random_interlace):
    putc = ""
    p0len = len(p0)
    for i in range(1,p0len):
        if random_interlace:
            if random.randint(0,1) == 1:
                putc += p1[i] + p0[i]
            else:
                putc += p0[i] + p1[i]
        else:
            putc += p0[i] + p1[i]
    return putc

def reinterlaced(key):
    putc = ""
    keylen = len(key)
    for i in range(0, keylen, 2):
        putc += key[i]
    for i in range(1, keylen, 2):
        putc += key[i]
    return putc

def private_encrypt10(str, key):
    return crypt.crypt(str,key)

def private_encrypt11(str, key):
    fkey = key[0]
    pwd = crypt.crypt(str, fkey)
    pwd = crypt.crypt(key, pwd[1:])
    for i in range(random.randint(0,3)):
        pwd = crypt.crypt(str, pwd[1:])
    return pwd

def private_encrypt12(str, key):
    fkey = key[0]
    pwd = crypt.crypt(str, fkey)
    pwd = crypt.crypt(key, pwd[1:])
    return pwd

def private_encrypt20(str, key):
    pwd = crypt.crypt(str, key)
    pwd = crypt.crypt(key, pwd[2:])
    return pwd

def private_encrypt21(str, key):
    pwd = crypt.crypt(str, key)
    pwd = crypt.crypt(str, pwd[2:])
    return pwd

def private_encrypt30(str, key):
    pwd = crypt.crypt(str, key)
    pwd = crypt.crypt(key, pwd[3:])
    pwd = crypt.crypt(str, pwd[3:])
    return pwd

def private_encrypt31(str, key):
    pwd = crypt.crypt(key, str)
    pwd = crypt.crypt(str, pwd[3:])
    pwd = crypt.crypt(key, pwd[3:])
    return pwd

def private_encrypt40(str, key):
    str1 = crypt.crypt(str, "40")
    key1 = crypt.crypt(key, "40")
    pwd = crypt.crypt(str1, key1)
    pwd = crypt.crypt(key, pwd[3:])
    return pwd

def private_encrypt41(str, key):
    str1 = crypt.crypt(str, "41")
    key1 = crypt.crypt(key, "41")
    pwd = crypt.crypt(key1, str1)
    pwd = crypt.crypt(str, pwd[3:])
    return pwd

def private_encrypt42(str, key):
    str2 = crypt.crypt(str, "42")
    key2 = crypt.crypt(key, "42")
    pwd = crypt.crypt(str2, key2)
    pwd = crypt.crypt(key2, pwd[3:])
    return pwd

def private_encrypt43(str, key):
    str2 = crypt.crypt(str, "43")
    key2 = crypt.crypt(key, "43")
    pwd = crypt.crypt(key2, str2)
    pwd = crypt.crypt(str2, pwd[3:])
    return pwd

def public_encrypt(str, key):
    random.seed()
    output = []
    funcs = (private_encrypt11, private_encrypt12, private_encrypt10, 
            private_encrypt20, private_encrypt21, private_encrypt30,
            private_encrypt31, private_encrypt40, private_encrypt41,
            private_encrypt42, private_encrypt43)
    for pe in funcs:
        if pe == private_encrypt11:
            pwd = interlaced(pe(str, key), pe(key, str), True)
        else:
            pwd = interlaced(pe(str, key), pe(key, str), False)
        slice0 = pwd[0:8], pwd[8:16], pwd[16:24]
        pwd = reinterlaced(pwd)
        slice1 = pwd[0:8], pwd[8:16], pwd[16:24]
        output.append(slice0 + slice1)
    return output

def public_parse(keyb):
    lenkeyb = len(keyb)
    sp = keyb.partition("@")
    if len(sp[0]) == 0:
        op = public_encrypt(KEYSTR, "python")
    elif len(sp[1]) == 0 or len(sp[2]) == 0:
        op = public_encrypt(KEYSTR, sp[0])
    else:
        op = public_encrypt(sp[2], sp[0])
    return op

def parse(keyb, debug=False):
    op = public_parse(keyb)
    output = []
    for y in range(len(op[0])):
        for x in range(1,len(op)):
            output.append((op[x][y]+" ","_",lenkeyb))
    return output

def opitem(op, start):
    x = 0
    size = len(op) - start
    resl = []
    for item in op:
        if x < start:
            x += 1
            continue
        resl.append("%02d %s  %02d %s  %02d %s  %02d %s  %02d %s  %02d %s" % \
            (x, item[0], x+size, item[1], x+size*2, item[2], \
            x+size*3, item[3], x+size*4, item[4], x+size*5, item[5]))
        x += 1
    return "\n".join(resl)

