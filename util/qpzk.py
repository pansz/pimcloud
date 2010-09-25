# coding=utf-8
# Author: Pan, Shi Zhu

from genziku import *

def main():
    zk2 = getziku2()

    # write pinyin zk 2
    f = open("quanpin2.txt", "w")
    print "writing result..."
    try:
        for k,v in zk2.iteritems():
            f.write(k+v[1]+"\n")
    finally:
        f.close()

    print "get level 3"
    jpzk3 = getsogou3()
    # write jianpin part of pinyin zk 3
    f = open("quanpin3.txt", "w")
    print "writing jpzk3..."
    try:
        for k,v in jpzk3.iteritems():
            f.write(k+v[1]+"\n")
    finally:
        f.close()

    pyzk3 = getpyzk(jpzk3)
    # write quanpin pinyin zk 3
    f = open("quanpin3.txt", "a")
    print "writing pyzk3..."
    try:
        for k,v in pyzk3.iteritems():
            f.write(k+v[1]+"\n")
    finally:
        f.close()
    
    print "get level 4"
    jpzk4 = getsogou4()
    # write jianpin part of pinyin zk 4
    f = open("quanpin4.txt", "w")
    print "writing jpzk4..."
    try:
        for k,v in jpzk4.iteritems():
            f.write(k+v[1]+"\n")
    finally:
        f.close()

    pyzk4 = getpyzk(jpzk4)
    # write quanpin pinyin zk 4
    f = open("quanpin4.txt", "a")
    print "writing pyzk4..."
    try:
        for k,v in pyzk4.iteritems():
            f.write(k+v[1]+"\n")
    finally:
        f.close()
    
    # finish
    print "finished. "

if __name__ == "__main__":
    main()

