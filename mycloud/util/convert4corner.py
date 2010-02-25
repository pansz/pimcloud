# coding=utf-8
import math

def load_alpha_zk(fname):
    f = open(fname)
    try:
        zk = {}
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            if not zk.has_key(key):
                zk[key] = []
            for item in items[1:]:
                zk[key].append(item)
    finally:
        f.close()
    return zk

def printstat(hkma):
    total = 0
    count = len(hkma)
    index = 0
    newmb = []
    # sort and average
    for k, v in hkma.iteritems():
        newmb.append((k, v))
        total += v
    newmb.sort(cmp=lambda x,y: cmp(x[1], y[1]))
    # print
    for k in xrange(len(newmb)):
        if k % 10 == 0:
            print ""
        else:
            print "\t",
        print newmb[k][0], newmb[k][1],
    print ""
    # calculate sd
    avg = (total + 0.) / count
    devia = 0.
    for k, v in hkma.iteritems():
        devia += (v - avg) * (v - avg)
    devia /= count
    print "avg=",avg,"\tsd=", math.sqrt(devia)

def stat1(zk, index1):
    dmjz = {}
    for k, v in zk.iteritems():
        key = k[index1]
        if not dmjz.has_key(key):
            dmjz[key] = 0
        dmjz[key] += len(v)
    print index1+1, 
    printstat(dmjz)

def stat2(zk, index1, index2):
    dmjz = {}
    for k, v in zk.iteritems():
        key = k[index1] + k[index2]
        if not dmjz.has_key(key):
            dmjz[key] = 0
        dmjz[key] += len(v)
    print index1+1,"+",index2+1,
    printstat(dmjz)

def stat3(zk, index1, index2, index3):
    dmjz = {}
    for k, v in zk.iteritems():
        key = k[index1] + k[index2] + k[index3]
        if not dmjz.has_key(key):
            dmjz[key] = 0
        dmjz[key] += len(v)
    print index1+1,"+",index2+1,"+",index3+1,
    printstat(dmjz)

def statall(zk):
    dmjz = {}
    for k, v in zk.iteritems():
        if not dmjz.has_key(k):
            dmjz[k] = 0
        dmjz[k] += len(v)
    print "1234",
    printstat(dmjz)

def main():
    # load file
    zk = load_alpha_zk("4corner.txt")
    #stat1(zk, 0)
    #stat1(zk, 1)
    #stat1(zk, 2)
    #stat1(zk, 3)
    stat2(zk, 0, 1)
    #stat2(zk, 0, 2)
    stat2(zk, 0, 3)
    #stat2(zk, 1, 2)
    #stat2(zk, 1, 3)
    #stat2(zk, 2, 3)
    #stat3(zk, 0, 1, 2)
    #stat3(zk, 0, 1, 3)
    #stat3(zk, 0, 2, 3)
    #stat3(zk, 1, 2, 3)
    #statall(zk)
    # write file
    f = open("xcorner.txt", "w")
    for k, v in zk.iteritems():
        newkey = k[0]+k[3]+k[1:3]
        f.write(newkey)
        for item in v:
            f.write(" "+item)
        f.write("\n")
    f.close()

if __name__ == "__main__":
    main()

