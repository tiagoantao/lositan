def calcCPlot(perc, fname):
    f = open(fname)
    bins = 50
    poses = {}
    allxs = []
    for l in f:
        toks = l.rstrip().split(" ")
        x = float(toks[0])
        y = float(toks[1])
        poses.setdefault(x, []).append(y)
        allxs.append(x)
    xs = poses.keys()
    xs.sort()
    allxs.sort()

    currBins = min([bins, len(xs)])
    lims = []
    perBin = len(allxs) / currBins
    print perBin
    prev = -1
    for i in range(currBins):
        curr = allxs[int(round(float(i) * len(allxs) / currBins))]
        if curr == prev:
            continue
        prev = curr
        lims.append(curr)
    lims.append(allxs[-1] + 0.001)

    nslices = int(round(1 / ((1 - perc) / 2)))
    medians = []
    bottoms = []
    tops = []
    for i in range(1, len(lims)):
        vals = []
        for x in xs:
            if x < lims[i - 1]:
                continue
            if x > lims[i]:
                break
            if x == lims[i]:
                if len(vals) < perBin:
                    lvals = len(vals)
                    vals.extend(poses[x][:perBin - lvals])
                    poses[x] = poses[x][perBin - lvals:]
                break
            vals.extend(poses[x])
        vals.sort()
        print i, len(vals)
        median = vals[len(vals) / 2]
        bottom = vals[len(vals) / nslices]
        top = vals[(nslices - 1) * len(vals) / nslices]
        medians.append(median)
        tops.append(top)
        bottoms.append(bottom)
    medians = [medians[0]] + medians
    tops = [tops[0]] + tops
    #tops = [(tops[0] + medians[0]) / 2] + tops
    bottoms = [bottoms[0]] + bottoms
    #bottoms = [(bottoms[0] + medians[0]) / 2] + bottoms
    confLines = []
    for i in range(len(lims)):
        confLines.append((lims[i], bottoms[i], medians[i], tops[i]))
    return confLines
