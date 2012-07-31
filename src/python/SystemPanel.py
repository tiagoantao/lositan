from math import ceil, log
from javax.swing import JPanel, JLabel, JComboBox, JCheckBox, JFormattedTextField
from java.awt import GridLayout, Dimension, Color
from java.awt.event import ActionListener, ActionEvent, ItemListener
from java.lang.management import ManagementFactory
from Shared import warn
from java.beans import PropertyChangeListener
from java.text import NumberFormat
from java.util import Locale

class SystemPanel(JPanel, ActionListener, ItemListener, PropertyChangeListener):
    def propertyChange(self, evt):
        if evt.getSource() == self.fdr and evt.getPropertyName() == 'value':
            new = float(evt.getNewValue())
            old = float(evt.getOldValue())
            if new > 0.99:
                evt.getSource().setValue(old)
            if new < 0.005:
                evt.getSource().setValue(old)


    def itemStateChanged(self, e):
        if self.enableChartFun:
            self.chartFun()

    def actionPerformed(self, e):
        if e.getID() <> ActionEvent.ACTION_PERFORMED:
            return
        if e.getSource() == self.neutral:
            if self.isTemporal:
                warn(self, """
            Using a "neutral" mean Ne means doing a first simulation run to
            remove potential selected loci for computing the initial mean Ne.
            This effectively doubles the computation time, but it is the recommended
            option.
            If you are not sure of what you want, please check this option.
            """)
            else:
                warn(self, """
            Using a "neutral" mean Fst means doing a first simulation run to
            remove potential selected loci for computing the initial mean Fst.
            This effectively doubles the computation time, but it is the recommended
            option.
            If you are not sure of what you want, please check this option.
            """)
        elif e.getSource() == self.force:
            warn(self, """
            Simulating a PRECISE mean Fst is not possible outside ideal theoretical
            conditions (infinite populations, infinite allele model). SELWB can try to
            approximate a desired Fst, by running a bisection algorithm over repeated
            simulations.
            Checking this option will increase the computation time by a certain amount
            of time (in most cases it will double the computation time), this is still,
            the recommended option.
            If you are not sure of what you want, please check this option.
            """)

    def getForce(self):
        if self.force.getSelectedObjects() == None:
            return False
        else:
            return True

    def getNeutral(self):
        if self.neutral.getSelectedObjects() == None:
            return False
        else:
            return True

    def getCI(self):
        return float(self.ci.getSelectedItem())

    def getFDR(self):
        return self.fdr.getValue()


    def getNumCores(self):
        return int(self.cores.getSelectedItem())

    def getNumSims(self):
        return 1000*int(self.numSims.getSelectedItem())

    def __init__(self, chartFun, isTemporal = False):
        self.isTemporal = isTemporal
        JPanel()
        #self.setBackground(Color.LIGHT_GRAY)
        self.chartFun = chartFun
        self.enableChartFun = False
        self.setLayout(GridLayout(6,2))
        self.add(JLabel('CPU Cores'))
        cores = JComboBox(['1', '2', '4', '8', '16', '32', '64', '128'])
        nprocs = ManagementFactory.getOperatingSystemMXBean().getAvailableProcessors()
        pos = min([7, log(ceil(nprocs)) / log(2)])
        cores.setSelectedIndex(int(pos))
        cores.setMaximumSize(cores.getPreferredSize())
        self.cores = cores
        self.add(self.cores)
        self.add(JLabel('# of sims (x1000)  '))
        numSims = JComboBox(
            map(lambda x: str((10+x)*5), range(10)) +
            map(lambda x: str(x*100), range(1,11))
        )
        numSims.setMaximumSize(numSims.getPreferredSize())
        self.numSims = numSims
        self.add(self.numSims)
        if isTemporal:
            self.add(JLabel('"Neutral" Ne'))
            self.neutral = JCheckBox()
            self.neutral.addActionListener(self)
            self.add(self.neutral)
        else:
            self.add(JLabel('"Neutral" mean Fst'))
            self.neutral = JCheckBox()
            self.neutral.addActionListener(self)
            self.add(self.neutral)
            self.add(JLabel('Force mean Fst'))
            self.force = JCheckBox()
            self.force.addActionListener(self)
            self.add(self.force)
        self.add(JLabel('Confidence interval '))
        ci = JComboBox(['0.95', '0.99', '0.995'])
        ci.addItemListener(self)
        ci.setMaximumSize(cores.getPreferredSize())
        self.ci = ci
        self.add(self.ci)
        self.add(JLabel('False Disc. Rate'))
        fdr = JFormattedTextField(
            NumberFormat.getNumberInstance(Locale.US))
        fdr.setValue(0.1)
        fdr.addPropertyChangeListener(self)
        self.add(fdr)
        self.fdr = fdr
