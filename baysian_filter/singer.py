# -*- encoding: sjis -*-
# bayesian fillter

import os
import sys

import MeCab

def wakati(dat):
    arg = [sys.argv[0], "-Owakati"]
    m = MeCab.Tagger(" ".join(arg))
    dat = m.parse(dat)
    dat2 = dat.rstrip('\r\n')
    #print("dat2:", dat2)
    lst = dat2.split(" ")
    while lst.count("") > 0:
        lst.remove("")

    return lst

def getFilelist(path):
    filelist = []
    for root, directories, files in os.walk(path):
        for f in files:
            filelist.append(path + "/" + f)
    return filelist

def analysisWord(dic, word, lst, opt=0):
    counter = 0
    for l in lst:
        dat = open(l).read()
        lst = wakati(dat)
        counter += lst.count(word)

    probability = float(counter) / float(len(lst))
    if word in dic:
        dic[word][opt] += probability
    else:
        dic[word] = [0,0,0]
        dic[word][opt] = probability

    return dic

# Initialize
MRC, GLAY = 0, 1
glay = "./glay"
mrc = "./mrc"
target = "./target.txt"

glaylst = getFilelist(glay)
mrclst = getFilelist(mrc)
print("Gray:", glaylst)
print("Mr.Children :", mrclst)

dat = open(target).read()
wordlist = wakati(dat)
worddic = {} # {word: [nmrc, nglay]}
print("wordlist:", wordlist)

# Analysis
for word in wordlist:
    worddic = analysisWord(worddic, word, mrclst, MRC)
    worddic = analysisWord(worddic, word, glaylst, GLAY)

# Calculate pg(w)
pgwlist = []

#print("worddic:", worddic)
for w, v in worddic.items():
    if len(w) < 2:
        continue

    check = float(v[MRC])*len(mrclst)*2 + float(v[GLAY])*len(glaylst)
    if check >= 1: # 5:
        if v[MRC] != 0 and v[GLAY] == 0: # mrc
            pg_w = (0.01, 0.49, w)
        elif v[MRC] == 0 and v[GLAY] != 0: # rem
            pg_w = (0.99, 0.49, w)
        elif v[MRC] == 0 and v[GLAY] == 0: # token is not in database
            pg_w = (0.4, 0.1, w)
        else:
            tmp = v[GLAY] / (2 * v[MRC] + v[GLAY])
            pg_w = (tmp, abs(0.5 - tmp), w)

        pgwlist.append(pg_w)

pgwlist.sort(key=lambda x: float(x[0]))
pgwlist.reverse()

pgwlist = pgwlist[:5]
print("pgwlist:", pgwlist)
for pgw in pgwlist:
    print(pgw[2], "\t", pgw[0])

p1, p2 = 1.00, 1.00
for pgw in pgwlist:
    p1 = p1 * float(pgw[0])
    p2 = p2 * (1 - float(pgw[0]))
    print("p1=", p1, "p2=", p2, "pgw(p1)=", pgw[0], "pgw(p2)=", (1-float(pgw[0])))

print("Mr.children probability = ", p2 / (p1 + p2))

