import sys

l = sys.stdin.readline()
print l.replace("\t", " ").replace("\"", ""),
for i in range(50):
    l = sys.stdin.readline()
    print l.split("\t")[0]

l = sys.stdin.readline()
while l != "":
    toks = l.replace("\"","").rstrip().split("\t")
    print toks[0],
    if len(toks)>1:
        print " ".join(map(lambda x:"0"+x, toks[1:])),
    print
    l = sys.stdin.readline()
