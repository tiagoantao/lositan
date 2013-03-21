def calcCPlot(ci, fname):
    f = open(fname)
    bins = 100
    perc = 0.95
    poses = {}
    xmin = None
    xmax = None
    for l in f:
        toks = l.rstrip().split(" ")
        x = float(toks[0])
        y = float(toks[1])
        poses.setdefault(x, []).append(y)
        if xmin is None or xmin > x:
            xmin = x
        if xmax is None or xmax < x:
            xmax = x
    xs = poses.keys()
    xs.sort()

    currBins = min([bins, len(set(xs))])
    lims = []
    for i in range(currBins - 1):
        lims.append(xs[i * len(xs) / (currBins)])
    lims.append(xmax + 0.01)
    lims = list(set(lims))
    lims.sort()

    nslices = int(round(1 / ((1 - perc) / 2)))
    medians = []
    bottoms = []
    tops = []
    for i in range(len(lims) - 1):
        vals = []
        for x in xs:
            if x < lims[i]:
                continue
            if  x >= lims[i + 1]:
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
    tops = [tops[0]] + tops
    bottoms = [bottoms[0]] + bottoms
    confLines = []
    for i in range(len(lims)):
        confLines.append((lims[i], bottoms[i], medians[i], tops[i]))
    return confLines
