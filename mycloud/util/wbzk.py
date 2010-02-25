# coding=utf-8
# Author: Pan, Shi Zhu

from genziku import *
import data

def main(mode):

    data.setmode("abc")
    pinyin_table = data.get(data.get_py_table)

    print "writing ",mode, "1"
    fin = open("abc2.txt", "r")
    f = open("wubi1.txt", "w")
    try:
        for line in fin:
            items = line.partition(" ")
            key = items[0]
            if len(key) == 2:
                pinyin = pinyin_table[key]
                f.write(pinyin+items[1]+items[2])
    finally:
        f.close()
        fin.close()

    # finish
    print "finished. "

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main("wubi")

