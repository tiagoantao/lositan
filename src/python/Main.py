from javax.swing import JFrame, JMenuBar, JMenu, JMenuItem, KeyStroke, JLabel
from javax.swing import JFileChooser, JPanel, JButton, UIManager, Box
from javax.swing.border import LineBorder
from java.awt import BorderLayout, GridLayout, Color, Dimension, Component
from java.awt.event import ActionEvent, ActionListener, KeyEvent
from java.awt.event import ComponentAdapter, ComponentEvent
from java.lang import System
from java.util import Locale

from copy import deepcopy
import os
import shutil
import sys
import thread
import time
import types

from Bio.PopGen import GenePop
from Bio.PopGen.GenePop import Utils
from Bio.PopGen.GenePop import FileParser
from Bio.PopGen.FDist import Async
from Bio.PopGen.FDist.Controller import FDistController
from Bio.PopGen.FDist.Utils import convert_genepop_to_fdist, approximate_fst

from SelPanel import SelPanel
from SystemPanel import SystemPanel
from StatusPanel import StatusPanel
from SummPanel import SummPanel
from EmpiricalPanel import EmpiricalPanel
from Chart import Chart
from ChartConf import ChartConf
from Meter import Meter
from RestrictElements import RestrictionDialog
from EditTextList import EditTextList
from Shared import error, yesNo, info
import FDistExtra
from LoadStatus import LoadDialog

import Ftemp
from temporal import Datacal
import CPlot

#There are quite a few global variables
#  This is acceptable because the application won't grow that much

#globals are:
#  lpath     - LOSITAN path
#  dataPath  - Last directory with opened data
#
#  rec2      - GenePop record
#  selRec2   - GenePop record - only selected info
#  popNames  - Population Names
#  remPops   - Removed pops
#  remLoci   - Removed loci
#  sampSize  - Sample size
#  locusFst  - Fst by (selected) Locus
#  splitSize - Split size (for load balancing)
#  tempSamples - temporal points
#
#  fdc       - FDist controller
#  fda       - FDist async
#  fdRequest - FDist request can be '', 'Force', 'Neutral', 'NeuFor'
#  runState  - FDist state: can be 'Final', 'ForceBeforeNeutral', 'Neutral', 'Force'
#
#  Panels/GUI
#  frame           - Top frame
#  summPanel       - Summary panel
#  systemPanel     - System panel (cores, ...)
#  statusPanel     - Status panel
#  empiricalPanel  - Empirical panel (Max pops, ...)
#  simsDonePanel   - Meter (Sims done)
#  chartPanel      - Chart (graph...)
#  menuHandles     - Menu handles (hash)
#  loadPanel       - loci count

def enableAllMenus(also5000 = False):
    #if also5000 then Runninng extra  5000 sims is also enabled
    global menuHandles
    for name, handle in menuHandles.items():
        if (not name == 'item5000' and not name == 'checkLoci') or also5000:
            handle.setEnabled(True)
        else:
            handle.setEnabled(False)

def disableAllMenus():
    global menuHandles
    for name, handle in menuHandles.items():
        handle.setEnabled(False)

def updateAll():
    global rec2, selRec2, popNames, remPops, remLoci, locusFst #,rec
    global summPanel, empiricalPanel, frame
    global myFst, maxRun, minRun # This is really a private var to be reused on report
    empiricalPanel.ignoreChanges = True
    myFst  = -1
    maxRun = -1
    minRun = -1
    selRec2 = FileParser.read(rec2.fname)
    #print rec2.fname, countPops(rec2)
    #for locus in remLoci:
    selRec2.remove_loci_by_name(remLoci, lpath + os.sep + "sr.tmp")
    shutil.copyfile(lpath + os.sep + "sr.tmp",
                    lpath + os.sep + "sr")
    selRec2 = FileParser.read(lpath + os.sep + "sr")

    #print len(popNames), remPops
    for i in range(len(popNames)-1, -1, -1):
        #print i, popNames[i]
        if popNames[i] in remPops:
            selRec2.remove_population(i, lpath + os.sep + "sr.tmp")
            shutil.copyfile(lpath + os.sep + "sr.tmp",
                            lpath + os.sep + "sr")
            selRec2 = FileParser.read(lpath + os.sep + "sr")
            #print i, os.path.getsize(lpath + os.sep + "sr"), countPops(selRec2)
    summPanel.update(rec2, popNames, remPops, remLoci)
    enableAllMenus()
    empiricalPanel.setTotalPops(len(popNames))
    def after():
        chartPanel.setMarkers(locusFst)
        chartPanel.updateChartDataset()
        empiricalPanel.knownPops = countPops(selRec2)
        empiricalPanel.ignoreChanges = False
    runDatacal(after)

def countPops(rec2):
    f2 = FileParser.read(rec2.fname)
    pop = 1
    while f2.skip_population():
        pop += 1
    return pop

def checkAlleles(file):
    df = FileParser.read(file)
    countAlleles = []
    for locus in df.loci_list:
        countAlleles.append(set())
    indiv = df.get_individual()
    while indiv:
        if type(indiv) == tuple:
            name, loci = indiv
            for l in range(len(loci)):
                for a in loci[l]:
                    if a: countAlleles[l].add(a)
        indiv = df.get_individual()
    probLoci = []
    for l in range(len(countAlleles)):
        if len(countAlleles[l])>2:
            probLoci.append(df.loci_list[l])
    if probLoci != []:
        if len(probLoci)>5:
            error(frame, "Many (%d) loci have more than 2 alleles" % (len(probLoci)))
        else:
            error(frame, "Some loci have more than 2 alleles: %s" % (str(probLoci)))

def loadGenePop(file):
    global rec2, popNames, remPops, remLoci #,rec
    #rec = GenePop.read(open(str(file)))
    try:
        rec2 = FileParser.read(file)
        if isDominant:
            checkAlleles(file)
        remPops = []
        remLoci = []
        #popNames = ['pop' + str(i+1) for i in range(len(rec.populations))]
        popNames = ['pop' + str(i+1) for i in range(countPops(rec2))]
    except:
        error(frame, "Not a genepop file!")

def chooseFile():
    global frame, dataPath
    global systemPanel, chartPanel
    global isTemporal
    fc = JFileChooser(dataPath)
    retVal = fc.showOpenDialog(frame)
    if retVal != JFileChooser.APPROVE_OPTION:
        return
    fname = fc.getSelectedFile().getAbsolutePath()
    dataPath = os.sep.join(fname.split(os.sep)[:-1])
    if isTemporal:
        info(frame, "We need a file with information about the temporal point of each sample")
        tfc = JFileChooser(dataPath)
        tRetVal = tfc.showOpenDialog(frame)
        if retVal != JFileChooser.APPROVE_OPTION:
            return
        tname = tfc.getSelectedFile().getAbsolutePath()
    systemPanel.enableChartFun = False
    chartPanel.resetData()
    loadGenePop(fname)
    if isTemporal:
        if not loadTemporal(tname):
            return
    updateAll()
    enablePanel(empiricalPanel)

def loadFilePopNames(file):
    global popNames, remPops
    f = open(str(file))
    l = f.readline()
    i = 0
    while l != '':
        if i >= len(popNames):
            break
        popNames[i] = l.rstrip()
        i += 1
        l = f.readline()
    f.close()
    remPops = []


def loadTemporal(fname):
    global tempSamples, popNames
    f = open(fname)
    l = f.readline()
    i = 0
    tempSamples = []
    while l != '':
        if i > len(popNames):
            break
        try:
            tempSamples.append(int(l.rstrip()))
        except:
            error(frame, "Temporal file syntax error, please check")
            return False

        i += 1
        l = f.readline()
    f.close()
    if i != len(popNames):
        error(frame, "Number of temporal samples (%d) is less than the number of time points specified (%d)" % (i, len(popNames)))
        return False
    else:
        info(frame, "Temporal points set at: %s" % str(tempSamples))
        return True

def loadPopNames():
    global frame, empiricalPanel
    fc = JFileChooser(dataPath)
    retVal = fc.showOpenDialog(frame)
    if retVal == JFileChooser.APPROVE_OPTION:
        file = fc.getSelectedFile()
        loadFilePopNames(file)
        updateAll()
        enablePanel(empiricalPanel)

def useExampleData():
    global empiricalPanel, systemPanel, chartPanel, isDominant, isTemporal
    systemPanel.enableChartFun = False
    chartPanel.resetData()
    if isTemporal:
        loadGenePop(lpath + os.sep + 'texample.gp')
        loadFilePopNames(lpath + os.sep + 'texample.txt')
        loadTemporal(lpath + os.sep + 'texample.temp')
    elif isDominant:
        loadGenePop(lpath + os.sep + 'dexample2.gp')
        loadFilePopNames(lpath + os.sep + 'dexample.txt')
    else:
        loadGenePop(lpath + os.sep + 'example.gp')
        loadFilePopNames(lpath + os.sep + 'example.txt')
    updateAll()
    enablePanel(empiricalPanel)

def updatePopNames(popList):
    global popNames
    popNames = popList

def editPopNames():
    global popNames
    etl = EditTextList(frame, 'Change Population Names',
         popNames, updatePopNames)
    etl.show()

def savePopNames():
    global frame
    global popNames, remPops
    fc = JFileChooser(dataPath)
    retVal = fc.showSaveDialog(frame)
    if retVal == JFileChooser.APPROVE_OPTION:
        file = fc.getSelectedFile().getAbsolutePath()
        try:
            f = open(file)
        except IOError:
            exists = False
        else:
            exists = True
            f.close()
        if exists:
            if not yesNo(frame, "File exists, overwrite?"):
                return
        f = open(file, 'w')
        for popName in popNames:
            f.write(popName + '\n')
        f.close()


def updateLoci(elementSel, elementRem):
    global remLoci
    remLoci = elementRem
    updateAll()

def updatePops(elementSel, elementRem):
    global remPops
    remPops = elementRem
    updateAll()

def createInfile(fdf):
    f = open(lpath + os.sep + 'infile', 'w')
    print(fdf.num_loci)
    f.write(str(fdf))
    f.close()

def update_load_status(curr):
    global loadPanel
    loadPanel.update_status(curr)


def runDatacal(after):
    global frame, loadPanel
    loadPanel = LoadDialog(frame, "Load Status")
    thread.start_new_thread(endRunDatacal, (after,))

def endRunDatacal(after):
    global fdc, selRec2, sampSize, locusFst, lpath
    global empiricalPanel, isDominant, systemPanel
    global tempSamples, isTemporal
    #createInfile(convert_genepop_to_fdist(selRec2))
    createInfile(convert_genepop_to_fdist(selRec2, update_load_status))

    if isDominant:
        crit = empiricalPanel.getCrit()
        beta = empiricalPanel.getBeta()
        fst, sampSize, loci, pops, F, obs = fdc.run_datacal(
            data_dir = lpath, version = 2,
            crit_freq=crit, p=0.5, beta=beta)
    elif isTemporal:
        dc = Datacal()
        dc.compute(lpath + os.sep + "infile", lpath + os.sep + "data_fst_outfile")
        sampSize = dc.getSampleSize()
        dc.computeNe(tempSamples[-1] - tempSamples[0])
        ne = dc.getNe()
    else:
        fst, sampSize = fdc.run_datacal(data_dir = lpath)
        print(fst, sampSize)
    if not isTemporal:
        if fst < 0.0:
            systemPanel.force.setEnabled(False)
            systemPanel.force.setSelected(False)
        else:
            systemPanel.force.setEnabled(True)
    f = open(lpath + os.sep + 'data_fst_outfile')
    locusFst = []
    l = f.readline()
    myPos = 0
    while l != '':
        if isDominant:
            lhe, lfst, lheold, llocus = l.rstrip().split(' ')
            while int(llocus)>myPos:
                locusFst.append(None)
                myPos += 1
            myPos += 1
        else:
            lhe, lfst = l.rstrip().split(' ')
            if lhe == "-nan":
                lhe = "nan"
            if lhe == "-nan":
                lhe = "nan"
            if lfst == "-nan":
                lfst = "nan"
            try:
                if float(lfst) < -10.0:
                    lfst = "nan"
            except ValueError:
                lfst = 'nan'
            try:
                if float(lhe) < -10.0:
                    lhe = "nan"
            except ValueError:
                lhe = 'nan'
        locusFst.append((float(lhe), float(lfst)))
        l = f.readline()
    while len(locusFst) < len(selRec2.loci_list):
        locusFst.append(None)
    f.close()
    if sampSize > 50:
        sampSize = 50
    if isTemporal:
        empiricalPanel.setNe(ne)
    else:
        empiricalPanel.setFst(fst)
    empiricalPanel.setSampleSize(sampSize)
    if isTemporal:
       info (frame, "Dataset Ne: %d" % int(ne))
    else:
       info (frame, "Dataset Fst: %f" % fst)
    after()
    loadPanel.dispose()


def getSelLoci(pv):
    global selRec2, locusFst
    global systemPanel, isDominant
    selLoci = []
    ci = 1.0 - systemPanel.getCI()
    currPos = 0
    def getP(pvLine):
        #there is a copy of this on selPanel
        if isDominant:
            p1 = pvLine[2]
            p2 = pvLine[3]
            p3 = pvLine[4]
            p = p1 - 0.5 * (p1+p2-1)
            return p
        else:
            return pvLine[3]
    for i in range(len(selRec2.loci_list)):
        if not locusFst[i]:
            continue
        #print pv[currPos], ci
        p = getP(pv[currPos])
        if p < ci/2 or p > 1.0 - ci/2:
            #print i
            selLoci.append(selRec2.loci_list[i])
        currPos += 1
    return selLoci

def getMut(mutStr):
    #print mutStr
    if mutStr == 'Infinite Alleles':
        return 0
    else:
        return 1


def changeChartCI(changeNotes=True):
    global systemPanel, chartPanel
    global fdc, selRec2, isDominant, isTemporal
    if isTemporal:
        confLines = CPlot.calcCPlot(systemPanel.getCI(),
                                    lpath + os.sep + "out.dat")
    elif isDominant:
        confLines = fdc.run_cplot(systemPanel.getCI(), lpath, version=2)
    else:
        confLines = fdc.run_cplot(systemPanel.getCI(), lpath, version=1)
    top, avg, bottom = [], [], []
    oldX = -1
    for group in confLines:
        if oldX == float(group[0]):
            continue #strange but possible
        oldX = float(group[0])
        if not isDominant:
            top.append((float(group[0]), float(group[3])))
            avg.append((float(group[0]), float(group[2])))
            bottom.append((float(group[0]), float(group[1])))
        else:
            top.append((float(group[0]), float(group[4])))
            avg.append((float(group[0]), float(group[3])))
            bottom.append((float(group[0]), float(group[2])))

    chartPanel.setBottom(bottom)
    #chartPanel.setAvg(avg)
    chartPanel.setTop(top)
    chartPanel.updateChartDataset(False)
    if changeNotes:
        if isDominant:
            pv = fdc.run_pv(data_dir =  lpath, version=2)
        else:
            pv = fdc.run_pv(data_dir =  lpath, version=1)
        selLoci = getSelLoci(pv)
        chartPanel.setSelLoci(pv, selRec2.loci_list, selLoci)
    return confLines

def report(fst):
    global numAttempts
    global fda, fdc, fdRequest, runState, selRec2, splitSize
    global chartPanel, simsDonePanel, systemPanel, empiricalPanel
    global empiricalPanel, menuHandles, statusPanel, frame
    global myFst, maxRun, minRun # This is really a private var to be reused
    global isTemporal, tempSamples, fdt
    if isTemporal:
        fdt.acquire()
    else:
        fda.acquire()
        if myFst < 0:
            myFst = empiricalPanel.getFst()
        if maxRun < 0:
            maxRun = 1.0
            minRun = 0.0
    ext = FDistExtra.getExt()
    fdc = FDistController('.', ext)
    ci = systemPanel.getCI()
    chartPanel.drawCI = True
    confLines = changeChartCI(False)
    simsDonePanel.increment(splitSize / 1000.0)
    if isTemporal:
        desiredNe = empiricalPanel.getNe()
    else:
        desiredFst = empiricalPanel.getFst()
    if simsDonePanel.getRange() == simsDonePanel.getValue():
        #print runState
        if isTemporal:
            fdt.release()  # We are the last one, this is safe
        else:
            fda.release()  # We are the last one, this is safe
        if runState == 'ForceBeforeNeutral' or runState == 'Force':
            os.remove(lpath + os.sep + 'out.dat') #careful, not for 5000 case
            #print "max", maxRun, "min", minRun
            nextFst, maxRun, minRun = approximate_fst(desiredFst, fst, myFst,
                maxRun, minRun)
            #print "obtained", fst, "desired", desiredFst, "next", nextFst, "max", maxRun, "min", minRun
            numAttempts += 1
            if nextFst == myFst or numAttempts == 20:
                numSims = systemPanel.getNumSims()
                if runState == 'Force':
                    statusPanel.setStatus('Running final simulation', Color.YELLOW)
                    runState = 'Final'
                else:
                    runState = 'Neutral'
                    statusPanel.setStatus('Simulation pass to determine initial neutral set', Color.CYAN)
            else:
                statusPanel.setStatus('Forcing correct mean Fst, current error is ' +
                                str(round(abs(fst - desiredFst), 3)), Color.RED)
                numSims = 50000
                myFst = nextFst
            npops = empiricalPanel.getTotalPops()
            nsamples = countPops(selRec2)
            numCores = systemPanel.getNumCores()
            sampSize = empiricalPanel.getSampleSize()
            if isDominant:
                theta = empiricalPanel.getTheta()
                beta = empiricalPanel.getBeta()
                crit = empiricalPanel.getCrit()
                mut = None
            else:
                theta = beta = crit = None
                mutStr = empiricalPanel.mut.getSelectedItem()
                mut = getMut(mutStr)
            if isTemporal:
                pass #XXX
            else:
                runFDistPart(False, selRec2, mut, numSims, npops, nsamples,
                    myFst, sampSize, theta, beta, crit, numCores)
        elif runState == 'Neutral':
            maxRun = -1
            minRun = -1
            myFst  = -1
            if isDominant:
                pv = fdc.run_pv(data_dir =  lpath, version=2)
            else:
                pv = fdc.run_pv(data_dir =  lpath, version=1)
            #pv = get_pv(data_dir = lpath)
            selLoci = getSelLoci(pv)
            if fdRequest == 'Neutral':
                runState = 'Final'
                numSims  = systemPanel.getNumSims()
                statusPanel.setStatus('Running final simulation', Color.YELLOW)
            else:
                runState = 'Force'
                numAttempts = 0
                statusPanel.setStatus('Forcing correct mean Fst for final pass', Color.RED)
                numSims  = 50000
            neutralRec = FileParser.read(selRec2.fname)
            #for locus in selLoci:
            neutralRec.remove_loci_by_name(selLoci, lpath+os.sep+"nr.tmp")
            shutil.copyfile(lpath + os.sep + "nr.tmp",
                    lpath + os.sep + "nr")
            neutralRec = FileParser.read(lpath + os.sep + "nr")
            createInfile(convert_genepop_to_fdist(neutralRec))
            if isTemporal:
                dc = Datacal()
                dc.compute(lpath + os.sep + "infile", lpath + os.sep + "data_fst_outfile")
                dc.computeNe(tempSamples[-1] - tempSamples[0])
                myNe = dc.getNe()
            elif isDominant:
                crit = empiricalPanel.getCrit()
                beta = empiricalPanel.getBeta()
                myFst, _sampSize, _loci, _pops, _F, _obs = \
                    fdc.run_datacal(data_dir = lpath,
                    version=2, crit_freq=crit, p=0.5, beta=beta)
            else:
                myFst, _sampSize = fdc.run_datacal(data_dir = lpath)
            #if myFst < 0.005:
            #    myFst = 0.005
            if isTemporal:
                empiricalPanel.setNe(myNe) #actually it is Ne
            else:
                empiricalPanel.setFst(myFst)
                if not isDominant:
                    mutStr = empiricalPanel.mut.getSelectedItem()
                    mut = getMut(mutStr)
                else:
                    mut = None
            npops = empiricalPanel.getTotalPops()
            nsamples = countPops(selRec2)
            numCores = systemPanel.getNumCores()
            sampSize = empiricalPanel.getSampleSize()
            if isDominant:
                theta = empiricalPanel.getTheta()
                beta = empiricalPanel.getBeta()
                crit = empiricalPanel.getCrit()
            else:
                theta = beta = crit = None
            os.remove(lpath + os.sep + 'out.dat') #careful, not for 5000 case
            createInfile(convert_genepop_to_fdist(selRec2))
            if isTemporal:
                dc = Datacal()
                dc.compute(lpath + os.sep + "infile", lpath + os.sep + "data_fst_outfile")
                dc.computeNe(tempSamples[-1] - tempSamples[0])
                ne = dc.getNe()
            elif isDominant:
                _fst, _sampSize, _loci, _pops, _F, _obs = \
                    fdc.run_datacal(data_dir = lpath, version=2,
                        crit_freq = crit, p=0.5, beta=beta)
            else:
                _fst, _sampSize = fdc.run_datacal(data_dir = lpath)
            if isTemporal:
                runFtempPart(False, selRec2, numSims, npops, nsamples, ne,
                    sampSize, numCores)
            else:
                runFDistPart(False, selRec2, mut, numSims, npops, nsamples,
                    myFst, sampSize, theta, beta, crit, numCores)
        elif runState == 'Final':
            maxRun = -1
            minRun = -1
            myFst  = -1
            statusPanel.setStatus('Done (preparing selection table, please wait...)', Color.GRAY)
            if isDominant:
                pv = fdc.run_pv(data_dir =  lpath, version=2)
            else:
                pv = fdc.run_pv(data_dir =  lpath, version=1)
            selLoci = getSelLoci(pv)
            chartPanel.setSelLoci(pv, selRec2.loci_list, selLoci)
            sp = SelPanel(frame, chartPanel, selRec2.loci_list, pv,
                    systemPanel.getCI(), confLines, locusFst, isDominant,
                    systemPanel.getFDR())
            if isTemporal:
                info(frame, "Done")
            else:
                info(frame, "Simulated Fst: %f" % (fst,))
            statusPanel.setStatus('Done')
            sp.show()
            enablePanel(empiricalPanel)
            enablePanel(systemPanel)
            enableAllMenus(True)
            systemPanel.enableChartFun = True
    else:
        if isTemporal:
            fdt.release()
        else:
            fda.release()

def cancelFDist():
    global empiricalPanel, systemPanel, statusPanel, frame
    global fda, fdt, isTemporal
    if not yesNo(frame, 'Are you sure you want to cancel (cancel will take a few seconds to complete)?'):
        return
    if isTemporal:
        fdt.acquire()
        fdt.report_fun = None
        fdt.release()
        fdt.stop()
        fd = fdt
    else:
        fda.acquire()
        fda.report_fun = None
        fda.release()
        fda.stop()
        fd = fda
    while len(fd.async.running) > 0:
        remaining = str(len(fd.async.running))
        time.sleep(0.1)
    enablePanel(empiricalPanel)
    enablePanel(systemPanel)
    enableAllMenus()
    statusPanel.setStatus('Computation interrupted')


def runFDist(more=False):
    global numAttempts
    global selRec2, frame, fdRequest, runState
    global empiricalPanel, systemPanel, statusPanel, chartPanel
    global isDominant, isTemporal
    chartPanel.resetData(True)
    try:
        if not more:
            os.remove(lpath + os.sep + 'out.dat') # careful, not for 5000 case
    except OSError:
        pass  # Its ok if it doesn't exist
    disableAllMenus()
    disablePanel(empiricalPanel)
    disablePanel(systemPanel)
    npops = empiricalPanel.getTotalPops()
    nsamples = countPops(selRec2)
    if nsamples > npops:
        error(frame, "Expected total populations lower then selected populations")
        return
    if isTemporal:
        ne = empiricalPanel.getNe()
    else:
        fst = empiricalPanel.getFst()
    if not isTemporal and not isDominant:
        mutStr = empiricalPanel.mut.getSelectedItem()
        mut = getMut(mutStr)
    if isDominant:
        theta = empiricalPanel.getTheta()
        beta = empiricalPanel.getBeta()
        crit = empiricalPanel.getCrit()
        mut = None
    else:
        theta = beta = crit = None
    if more:
        statusPanel.setStatus('Running an extra 5000 simulations', Color.YELLOW)
        numSims = 5000
    else:
        numSims = systemPanel.getNumSims()
    numCores = systemPanel.getNumCores()
    sampSize = empiricalPanel.getSampleSize()
    if not more:
        if not isTemporal:
            force = systemPanel.getForce()
        else:
            force = False
        neutral = systemPanel.getNeutral()
        if neutral and force:
            statusPanel.setStatus('Forcing correct mean Fst for first pass', Color.RED)
            fdRequest = 'NeuFor'
            runState  = 'ForceBeforeNeutral'
            numAttempts = 0
            numSims   = 50000
        elif neutral:
            statusPanel.setStatus('First simulation pass to determine initial neutral set', Color.CYAN)
            fdRequest = 'Neutral'
            runState  = 'Neutral'
        elif force:
            statusPanel.setStatus('Forcing correct mean Fst for final simulation', Color.RED)
            fdRequest = 'Force'
            runState  = 'Force'
            numAttempts = 0
            numSims   = 50000
        else:
            statusPanel.setStatus('Running simulation', Color.YELLOW)
            fdRequest = ''
            runState  = 'Final'
    else:
        fdRequest = ''
        runState  = 'Final'
    if isTemporal:
        runFtempPart(more, selRec2, numSims, npops, nsamples, ne,
            sampSize, numCores)
    else:
        runFDistPart(more, selRec2, mut, numSims, npops, nsamples, fst,
            sampSize, theta, beta, crit, numCores)

def runFtempPart(more, selRec2, numSims, npops, nsamples, ne,
        sampSize, numCores):
    global fdt, tempSamples
    global chartPanel, simsDonePanel
    global splitSize
    splitSize = max([500, numSims/(numCores*10)])
    #print splitSize
    fdt = Ftemp.Split(report, numCores, splitSize, '..')
    if more:
        oldRange = simsDonePanel.getValue() #range = value when done
        simsDonePanel.setRange(oldRange + numSims / 1000)
        simsDonePanel.setValue(oldRange)
    else:
        simsDonePanel.setRange(numSims / 1000)
        simsDonePanel.setValue(0)
    fdt.run_ftemp(npops, ne, sampSize, tempSamples, numSims, lpath)

def runFDistPart(more, selRec2, mut, numSims, npops,
        nsamples, fst, sampSize, theta, beta, crit, numCores):
    global fda, isDominant
    global chartPanel, simsDonePanel
    global splitSize
    #createInfile(convert_genepop_to_fdist(selRec2))
    #print npops, nsamples, fst, sampSize, mut, numSims
    ext = FDistExtra.getExt()
    splitSize = max([500, numSims/(numCores*10)])
    #print splitSize
    fda = Async.SplitFDist(report, numCores, splitSize, '..', ext)
    #Fdist directory is an hack, we know it is above the data dir
    if more:
        oldRange = simsDonePanel.getValue() #range = value when done
        simsDonePanel.setRange(oldRange + numSims / 1000)
        simsDonePanel.setValue(oldRange)
    else:
        simsDonePanel.setRange(numSims / 1000)
        simsDonePanel.setValue(0)
    if isDominant:
        fda.run_fdist(npops, nsamples, fst, sampSize, mut, numSims, lpath,
            True, theta, beta, crit)
    else:
        fda.run_fdist(npops, nsamples, fst, sampSize,
            mut, numSims, lpath)

def getChartConf(chart):
    global chartPanel
    chartPanel.markerColor = chart.getMarkerColor()
    chartPanel.balColor = chart.getBalColor()
    chartPanel.neuColor = chart.getNeuColor()
    chartPanel.posColor = chart.getPosColor()
    chartPanel.labelSelected = chart.getSelLabel()
    chartPanel.labelNeutral = chart.getNeuLabel()
    chartPanel.updateChartDataset()

def configChart():
    global chartPanel, frame
    cc = ChartConf(
        frame,
        chartPanel,
        getChartConf)
    cc.show()

def checkLoci():
    global chartPanel, selRec2, systemPanel, fdc, isDominant, locusFst
    if isDominant:
        pv = fdc.run_pv(data_dir =  lpath, version=2)
        confLines = fdc.run_cplot(systemPanel.getCI(), lpath, version=2)
    else:
        pv = fdc.run_pv(data_dir =  lpath, version=1)
        confLines = fdc.run_cplot(systemPanel.getCI(), lpath)
    sp = SelPanel(frame, chartPanel, selRec2.loci_list, pv,
         systemPanel.getCI(), confLines, locusFst, isDominant,
         systemPanel.getFDR())
    sp.show()

def displayCitation():
    if isTemporal:
        info(frame, """If you use LosiTemp please cite:
        ...
        """)
    elif isDominant:
        info(frame, """If you use Mcheza please cite:
Antao T, Beaumont MA (2011)
Mcheza: A workbench to detect selection using dominant markers
Bioinformatics doi: 10.1093/bioinformatics/btr253
    """)
    else:
        info(frame, """If you use LOSITAN please cite both:

Beaumont MA, Nichols RA (1996)
Evaluating loci for use in the genetic analysis of population structure
Proceedings of the Royal Society of London B 263: 1619-1626

AND

LOSITAN: A workbench to detect molecular adaptation based on a Fst-outlier method
Tiago Antao, Ana Lopes, Ricardo J Lopes, Albano Beja-Pereira, Gordon Luikart
BMC Bioinformatics 2008, 9:323
    """)

class doAction(ActionListener):
    def actionPerformed(self, event):
        global frame, chartPanel
        global popNames, rec2, remLoci, remPops #, rec
        global isDominant
        option = event.getActionCommand()
        #print option
        if option == 'Open':
            chooseFile()
        elif option == 'LoadPop':
            loadPopNames()
        elif option == 'EditPop':
            editPopNames()
        elif option == 'SavePop':
            savePopNames()
        elif option == 'Example':
            useExampleData()
        elif option == 'Citation':
            displayCitation()
        elif option == 'ChooseLoci':
            selLoci = rec2.loci_list[:]
            for locus in remLoci:
                selLoci.remove(locus)
            rd = RestrictionDialog(frame, 'Choose loci',
                selLoci, remLoci, updateLoci)
            rd.show()
        elif option == 'ChoosePops':
            selPops = popNames[:]
            for pop in remPops:
                selPops.remove(pop)
            rd = RestrictionDialog(frame, 'Choose Populations',
                selPops, remPops, updatePops)
            rd.show()
        elif option == 'RunFDist':
            runFDist()
        elif option == 'CancelFDist':
            cancelFDist()
        elif option == 'Run5000':
            runFDist(True)
        elif option == 'CheckLoci':
            checkLoci()
        elif option == 'ConfGrp':
            configChart()
        elif option == 'Help':
            if isDominant:
                info(frame, 'For help please visit http://popgen.eu/soft/mcheza')
            else:
                info(frame, 'For help please visit http://popgen.eu/soft/lositan')
        elif option == 'SavePNG':
            chartPanel.save(frame, 'PNG')
        elif option == 'SaveSVG':
            chartPanel.save(frame, 'SVG')
        elif option == 'SavePDF':
            chartPanel.save(frame, 'PDF')
        elif option == 'Exit':
            sys.exit(-1)

def createParametersPanel(manager):
    global systemPanel, menuHandles, isTemporal
    systemPanel = SystemPanel(changeChartCI, isTemporal)
    global summPanel
    summPanel = SummPanel(isTemporal)
    global empiricalPanel, isDominant
    empiricalPanel = EmpiricalPanel(menuHandles, manager, isDominant,
            systemPanel, isTemporal)
    global simsDonePanel
    simsDonePanel = Meter(300, 120, 10)
    panel = JPanel()
    panel.setBorder(LineBorder(Color.GREEN))
    panel.add(systemPanel)
    panel.add(empiricalPanel)
    panel.add(summPanel)
    panel.add(simsDonePanel)
    return panel

def createChartPanel():
    global chartPanel
    if isDominant:
        chartPanel = Chart(980, 380)
    else:
        chartPanel = Chart(980, 480, isTemporal)
    return chartPanel

def createButton(text, command, manager):
    button = JButton(text)
    button.setActionCommand(command)
    button.addActionListener(manager)
    return button

def createMenuItem(text, command, manager):
    mi = JMenuItem(text)
    mi.setActionCommand(command)
    mi.addActionListener(manager)
    return mi

def createMenuBar(manager):
    global menuHandles, isDominant, isTemporal
    menuHandles = {}
    menuBar = JMenuBar()

    fmenu = JMenu("File")
    menuHandles['File'] = fmenu
    fmenu.setMnemonic(KeyEvent.VK_F)
    menuBar.add(fmenu)
    fmenu.add(createMenuItem('Open Genepop data', "Open", manager))
    fmenu.add(createMenuItem('Use Example data', "Example", manager))
    fmenu.addSeparator()
    fmenu.add(createMenuItem('Citation', "Citation", manager))
    fmenu.addSeparator()
    fmenu.add(createMenuItem("Exit", "Exit", manager))

    if not isTemporal:
        pmenu = JMenu("Populations")
        menuHandles['Populations'] = pmenu
        pmenu.setEnabled(False)
        pmenu.setMnemonic(KeyEvent.VK_P)
        menuBar.add(pmenu)
        pmenu.add(createMenuItem('Load population names', "LoadPop", manager))
        pmenu.add(createMenuItem('Edit population names', "EditPop", manager))
        pmenu.add(createMenuItem('Save population names', "SavePop", manager))

    umenu = JMenu("Data used")
    menuHandles['Data used'] = umenu
    umenu.setEnabled(False)
    umenu.setMnemonic(KeyEvent.VK_U)
    menuBar.add(umenu)
    umenu.add(createMenuItem('Loci Analyzed', "ChooseLoci", manager))
    if isTemporal:
        umenu.add(createMenuItem('Samples Analyzed', "ChoosePops", manager))
    else:
        umenu.add(createMenuItem('Populations Analyzed', "ChoosePops", manager))

    if isDominant:
        fdmenu = JMenu("DFDist")
    elif isTemporal:
        fdmenu = JMenu("FTemp")
    else:
        fdmenu = JMenu("FDist")
    menuHandles['FDist'] = fdmenu
    fdmenu.setEnabled(False)
    fdmenu.setMnemonic(KeyEvent.VK_D)
    menuBar.add(fdmenu)
    if isTemporal:
        fdmenu.add(createMenuItem('Run FTemp', "RunFDist", manager))
    else:
        fdmenu.add(createMenuItem('Run FDist', "RunFDist", manager))
    item5000 = createMenuItem('Run more 5000 sims', "Run5000", manager)
    item5000.setEnabled(False)
    menuHandles['item5000'] = item5000
    fdmenu.add(item5000)
    checkLoci = createMenuItem('Check Loci Status', "CheckLoci", manager)
    checkLoci.setEnabled(False)
    menuHandles['checkLoci'] = checkLoci
    fdmenu.add(checkLoci)

    gmenu = JMenu("Graphic")
    gmenu.setEnabled(False)
    menuHandles['Graphic'] = gmenu
    gmenu.setMnemonic(KeyEvent.VK_G)
    menuBar.add(gmenu)
    gmenu.add(createMenuItem('Colors and loci labels', "ConfGrp", manager))
    #gmenu.add(createMenuItem('Save Graphic as PNG', "SavePNG", manager))
    gmenu.add(createMenuItem('Save as PNG', "SavePNG", manager))
    gmenu.add(createMenuItem('Export as PDF', "SavePDF", manager))
    gmenu.add(createMenuItem('Export as SVG', "SaveSVG", manager))

    menuBar.add(Box.createHorizontalGlue())

    hmenu = JMenu("Help")
    hmenu.setMnemonic(KeyEvent.VK_H)
    menuBar.add(hmenu)
    hmenu.add(createMenuItem('Help', "Help", manager))

    return menuBar

def createMenuPanel(manager):
    panel = JPanel()
    panel.setLayout(GridLayout(3, 6))
    panel.add(createButton('Open Genepop data', "Open", manager))
    panel.add(createButton('Load pop names', "LoadPop", manager))
    panel.add(createButton('Choose populations', "ChoosePops", manager))
    panel.add(createButton('Run FDist', "RunFDist", manager))
    panel.add(createButton('Configure Graphic', "ConfGrp", manager))
    panel.add(createButton('Exit', "Exit", manager))

    panel.add(createButton('Use Example data', "Example", manager))
    panel.add(createButton('Edit pop names', "EditPop", manager))
    panel.add(createButton('Choose loci', "ChooseLoci", manager))
    panel.add(createButton('Run more 5000 sims', "Run5000", manager))
    panel.add(createButton('Save Graphic', "SaveGrp", manager))
    panel.add(JLabel(""))

    panel.add(JLabel(""))
    panel.add(createButton('Save pop names', "SavePop", manager))
    panel.add(JLabel(""))
    panel.add(JLabel(""))
    panel.add(JLabel(""))
    panel.add(JLabel(""))
    return panel

def createStatusPanel():
    global statusPanel
    statusPanel = StatusPanel()
    return statusPanel

def disablePanel(panel, exclude = []):
    attrs = dir(panel)
    for attrStr in attrs:
        try:
            attr = getattr(panel, attrStr)
            if isinstance(attr, Component) and \
                not attrStr.endswith('Ancestor') and \
                attrStr not in exclude:
                attr.setEnabled(False)
        except AttributeError: #Some attributes are write only
            pass
        except TypeError: #Some attributes are write only
            pass

def enablePanel(panel, exclude = []):
    attrs = dir(panel)
    for attrStr in attrs:
        try:
            attr = getattr(panel, attrStr)
            if isinstance(attr, Component) and \
                not attrStr.endswith('Ancestor') and \
                attrStr not in exclude:
                attr.setEnabled(True)
        except AttributeError: #Some attributes are write only
            pass
        except TypeError: #Some attributes are write only
            pass


def doPrettyType(frame, manager):
    global menuHandles
    frame.setLayout(BorderLayout())
    frame.setJMenuBar(createMenuBar(manager))
    #disableAllMenus()
    #menuHandles['File'].setEnabled(True)
    #frame.add(createMenuPanel(manager), BorderLayout.PAGE_START)
    frame.add(createStatusPanel(), BorderLayout.PAGE_START)
    frame.add(createChartPanel(), BorderLayout.CENTER)
    frame.add(createParametersPanel(manager), BorderLayout.PAGE_END)
    frame.pack()

def createFrame():
    global isDominant
    manager = doAction()
    if isTemporal:
        frame = JFrame("LosiTemp - LOoking for Selection In TEMPoral datasets")
    elif isDominant:
        frame = JFrame("Mcheza - Dominant Selection Workbench")
    else:
        frame = JFrame("LOSITAN - Selection Workbench")
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
    doPrettyType(frame, manager)
    frame.setVisible(1)
    frame.setResizable(0)
    return frame

def styleApp():
    uiDefaults = UIManager.getDefaults()
    e = uiDefaults.keys()
    while e.hasMoreElements():
       obj = e.nextElement()
       if type(obj) == types.StringType:
           if obj.endswith("background") and \
              isinstance(uiDefaults.get(obj), Color):
               if str(obj).startswith('List.'):
                   uiDefaults.put(obj, Color(240, 240, 240))
               else:
                   uiDefaults.put(obj, Color.WHITE)

def openDir():
    osName = System.getProperty('os.name').lower()
    if osName.find('mac os x')>-1:
        os.system('chmod a+rw ' + lpath)
        os.system('chmod a+rw ' + lpath + '*')

def prepareFDist():
    global fdc
    #print lpath
    FDistExtra.compile(lpath)
    ext = FDistExtra.getExt()
    fdc = FDistController('.', ext)

global lpath
global isDominant
if len(sys.argv)>1:
    if sys.argv[1] == "temp":
        isDominant = False
        isTemporal = True
    else:
        isDominant = True
        isTemporal = False
else:
    isDominant = False
    isTemporal = False
lpath = None
if isTemporal:
    myPath = ".lositemp"
elif isDominant:
    myPath = ".mcheza"
else:
    myPath = ".lositan"
for path in sys.path:
    if path.find(myPath) > -1 and path.find("jar") == -1 and \
            path.find("libs") == -1:
        lpath = path
if not lpath: #local mode
    for path in sys.path:
        if path.find('scratch') > -1 and path.find("jar") == -1 and \
                path.find("libs") == -1:
            lpath = path
Locale.setDefault(Locale.US)
openDir()
prepareFDist()
styleApp()
frame = createFrame()
dataPath = None
disablePanel(empiricalPanel, ["theta", "beta1", "beta2", "crit"])
