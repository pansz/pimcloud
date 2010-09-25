
def convert_zk(fname):
    f = open(fname)
    fo = open("r"+fname, "w")
    try:
        for line in f:
            items = line[:-1].split(" ")
            key = items[0]
            for item in items[1:]:
                fo.write(item+" "+key+"\n")
    finally:
        f.close()
        fo.close()
    print "write", "r"+fname

def main():
    convert_zk("p1.txt")
    convert_zk("quanpin1.txt")

if __name__ == "__main__":
    main()

