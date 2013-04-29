def calcCPlot(ci, fname):
    f = open(fname)
    bins = 50
    perc = 0.95
    poses = {}
    xmin = None
    xmax = None
    allxs = []
    for l in f:
        toks = l.rstrip().split(" ")
        x = float(toks[0])
        y = float(toks[1])
        poses.setdefault(x, []).append(y)
        allxs.append(x)
        if xmin is None or xmin > x:
            xmin = x
        if xmax is None or xmax < x:
            xmax = x
    xs = poses.keys()
    xs.sort()
    allxs.sort()

    currBins = min([bins, len(set(xs))])
    lims = []
    prev = None
    for i in range(currBins - 1):
        curr = allxs[i * len(allxs) / currBins]
        if curr == prev:
            continue
        prev = curr
        lims.append(curr)
    #lims.append(xmax + 0.01)
    lims.append(allxs[-1])
    lims = list(set(lims))
    lims.sort()

    nslices = int(round(1 / ((1 - perc) / 2)))
    medians = []
    bottoms = []
    tops = []
    for i in range(len(lims) - 1):
        vals = []
        if i == 0:
            mi = 0
        else:
            mi = i - 1
        if i == len(lims) - 2:
            ma = len(lims) - 1
        else:
            ma = i + 2
        for x in xs:
            if x < lims[mi]:
                continue
            if  x >= lims[ma]:
                break
            vals.extend(poses[x])
        vals.sort()
        median = vals[len(vals) / 2]
        bottom = vals[len(vals) / nslices]
        top = vals[(nslices - 1) * len(vals) / nslices]
        medians.append(median)
        tops.append(top)
        bottoms.append(bottom)
    medians = [medians[0]] + medians
    tops = [(tops[0] + medians[0]) / 2] + tops
    bottoms = [(bottoms[0] + medians[0]) / 2] + bottoms
    confLines = []
    for i in range(len(lims)):
        confLines.append((lims[i], bottoms[i], medians[i], tops[i]))
    return confLines
