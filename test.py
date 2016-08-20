import sys

id = "1207467036"

def c(i):
    s = hex(int(i))[2:]
    return s if len(s) is 5 else "0000"[:5 - len(s)] + s

def dc(i):
    l = 0
    while i[l] == 0:
        l+=1
    return int(i[:5-l], 16)

if __name__ == "__main__":
    if len(id) == 10:
        sp = [id[:5],id[5:]]
        print(c(sp[0]))
        print(c(sp[1]))
        print(c("89"))
        print(dc(c("89")))
