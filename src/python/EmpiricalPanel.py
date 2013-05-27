from Shared import warn, error
from java.text import NumberFormat
from java.util import Locale
from javax.swing import JButton, JPanel, JLabel, JComboBox, JCheckBox, JFormattedTextField
from java.awt import GridLayout
from java.awt.event import ItemListener
from java.beans import PropertyChangeListener

class EmpiricalPanel(JPanel, PropertyChangeListener, ItemListener):
    def propertyChange(self, evt):
        if self.ignoreChanges: return
        change = False
        if not self.isTemporal:
            if evt.getSource() == self.fst and evt.getPropertyName() == 'value':
                new = float(evt.getNewValue())
                old = float(evt.getOldValue())
                if new > 0.99:
                    evt.getSource().setValue(old)
                if new < -0.2:
                    evt.getSource().setValue(old)
                elif new< 0.0:
                    self.systemPanel.force.setSelected(False)
                    self.systemPanel.force.setEnabled(False)
                else:
                    self.systemPanel.force.setEnabled(True)
        else:
            if evt.getSource() == self.ne and evt.getPropertyName() == 'value':
                new = int(evt.getNewValue())
                old = int(evt.getOldValue())
                if new < 0:
                    evt.getSource().setValue(old)
        if self.isDominant and evt.getSource() in [self.theta, self.beta1,
            self.beta2, self.crit] and evt.getPropertyName() == 'value':
            new = float(evt.getNewValue())
            old = float(evt.getOldValue())
            if new > 0.99 or new < -0.2:
                evt.getSource().setValue(old)
        if evt.getSource() == self.sampleSize and evt.getPropertyName() == 'value':
            change = True
            new = int(evt.getNewValue())
            old = int(evt.getOldValue())
            if new > 50 and old > 4:
                warn(self, 'A sample size bigger than 50 is not expected to produce better results, while it slows the computation')
            if new < 5 and (new!=0 and not self.isDominant):
                evt.getSource().setValue(old)
        if evt.getSource() == self.pops and evt.getPropertyName() == 'value':
            change = True
            new = int(evt.getNewValue())
            old = int(evt.getOldValue())
            if new > 100:
                error(self, 'Maximum value for total populations is 100')
                evt.getSource().setValue(100)
            if new < self.knownPops:
                error(self,
                'Expected total populations has to be at least the same as the number of populations under study.'
                )
                evt.getSource().setValue(self.knownPops)
        if not self.isTemporal:
            if evt.getSource() == self.mut:
                change = True
        if not change: return
        if self.menuHandles['item5000'].isEnabled():
            self.menuHandles['item5000'].setEnabled(False)
            warn(self, "Changed parameter will require restarting simulations")

    def itemStateChanged(self, evt):
        self.propertyChange(evt)

    def getTotalPops(self):
        return self.pops.getValue()
    def setTotalPops(self, numPops):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.pops.setValue(numPops)
        self.ignoreChanges = ignoreChanges

    def getFst(self):
        return self.fst.getValue()
    def setFst(self, fst):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.fst.setValue(fst)
        self.ignoreChanges = ignoreChanges

    def getNe(self):
        return self.ne.getValue()
    def setNe(self, ne):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.ne.setValue(int(ne))
        self.ignoreChanges = ignoreChanges

    def getTheta(self):
        return self.theta.getValue()
    def setTheta(self, theta):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.theta.setValue(theta)
        self.ignoreChanges = ignoreChanges

    def getBeta(self):
        return (self.beta1.getValue(), self.beta2.getValue())
    def setBeta(self, beta):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.beta1.setValue(beta[0])
        self.beta2.setValue(beta[1])
        self.ignoreChanges = ignoreChanges

    def getCrit(self):
        return self.crit.getValue()
    def setCrit(self, crit):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.crit.setValue(crit)
        self.ignoreChanges = ignoreChanges

    def getSampleSize(self):
        return self.sampleSize.getValue()
    def setSampleSize(self, sampleSize):
        ignoreChanges =  self.ignoreChanges
        self.ignoreChanges = True
        self.sampleSize.setValue(sampleSize)
        self.ignoreChanges = ignoreChanges

    def __init__(self, menuHandles, manager, isDominant, systemPanel,
            isTemporal = False):
        self.systemPanel = systemPanel
        self.knownPops = 0
        self.ignoreChanges = True
        JPanel()
        self.menuHandles = menuHandles
        self.isDominant = isDominant
        self.isTemporal = isTemporal
        if isDominant:
            self.setLayout(GridLayout(8,2))
        else:
            self.setLayout(GridLayout(5,2))
        if isTemporal:
            self.add(JLabel('Ne'))
            ne = JFormattedTextField(NumberFormat.getNumberInstance(Locale.US))
            ne.addPropertyChangeListener(self)
            self.ne = ne
            self.add(ne)
            self.add(JLabel('Expected total samples'))
        else:
            self.add(JLabel('Attempted Fst'))
            fst = JFormattedTextField(NumberFormat.getNumberInstance(Locale.US))
            fst.addPropertyChangeListener(self)
            self.fst = fst
            self.add(fst)
            self.add(JLabel('Expected total pops'))
        pops = JFormattedTextField(NumberFormat.getIntegerInstance(Locale.US))
        pops.addPropertyChangeListener(self)
        #self.pops = JComboBox(['1', '2', '4', '8', '12', '16'])
        self.pops = pops
        self.add(self.pops)
        if not isDominant and not isTemporal:
            self.add(JLabel('Mutation model'))
            self.mut = JComboBox(['Infinite Alleles', 'Stepwise'])
            self.mut.addItemListener(self)
            self.add(self.mut)
        self.add(JLabel('Subsample size'))
        sampleSize = JFormattedTextField(
                NumberFormat.getIntegerInstance(Locale.US))
        sampleSize.addPropertyChangeListener(self)
        self.sampleSize = sampleSize
        self.add(self.sampleSize)
        if isDominant:
            self.add(JLabel('Theta'))
            theta = JFormattedTextField(
                NumberFormat.getNumberInstance(Locale.US))
            theta.addPropertyChangeListener(self)
            self.theta = theta
            self.add(theta)
            theta.setValue(0.1)

            self.add(JLabel('Beta-a'))
            beta1 = JFormattedTextField(
                NumberFormat.getNumberInstance(Locale.US))
            beta1.addPropertyChangeListener(self)
            self.beta1 = beta1
            self.add(beta1)
            beta1.setValue(0.25)

            self.add(JLabel('Beta-b'))
            beta2 = JFormattedTextField(
                NumberFormat.getNumberInstance(Locale.US))
            beta2.addPropertyChangeListener(self)
            self.beta2 = beta2
            self.add(beta2)
            beta2.setValue(0.25)

            self.add(JLabel('Critical frequency'))
            crit = JFormattedTextField(
                NumberFormat.getNumberInstance(Locale.US))
            crit.addPropertyChangeListener(self)
            self.crit = crit
            self.add(crit)
            crit.setValue(0.99)

        run = JButton('Run!')
        run.addActionListener(manager)
        run.setActionCommand('RunFDist')
        self.run = run
        self.add(run)
