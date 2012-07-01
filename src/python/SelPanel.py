from jarray import array
from java.awt import BorderLayout, Color
from java.awt.event import ActionListener
from java.lang import Class, String, System
from java.util import Vector
from javax.swing import JDialog, JButton, JTable, JScrollPane
from javax.swing import JFileChooser, JLabel, JPanel
from javax.swing.table import TableCellRenderer


class ColorRenderer(TableCellRenderer):
    def __init__(self, data, ci, neuColor, balColor, posColor):
        self.color = []
        ci = 1 - ci
        for i in range(data.size()):
            try:
                stat = float(data.get(i)[3])
                if stat > 1 - ci/2:
                    self.color.append(posColor)
                elif stat < ci/2:
                    self.color.append(balColor)
                else:
                    self.color.append(neuColor)
            except ValueError:
                self.color.append(Color.WHITE)
    def getTableCellRendererComponent(
        self, table, text, isSelected, hasFocus, row, column):
        comp = JLabel(text)
        comp.setOpaque(True) #MUST do this for background to show up.
        comp.setBackground(self.color[row])
        return comp

class SelPanel(JDialog, ActionListener):
    def actionPerformed(self, event):
        option = event.getActionCommand()
        if option == 'Close':
          self.dispose()
        elif option == 'SCI':
            chooser = JFileChooser()
            returnVal = chooser.showSaveDialog(self)
            if returnVal == JFileChooser.APPROVE_OPTION:
                fileName = chooser.getSelectedFile().getPath()
                f = open(fileName, 'w')
                f.write("\t".join(["Het", "Fst", "0.5(1-pval)quantile", "median", "0.5(1+pval)quantile"]) + "\n")
                for line in self.confLines:
                    f.write('\t'.join(map(lambda x: str(x), line)) + "\n")
                f.close()
        elif option == 'SLL':
            chooser = JFileChooser()
            returnVal = chooser.showSaveDialog(self)
            if returnVal == JFileChooser.APPROVE_OPTION:
                fileName = chooser.getSelectedFile().getPath()
                f = open(fileName, 'w')
                f.write("\t".join(["Locus", "Het", "Fst", "P(Simul Fst<sample Fst)"]) + "\n")
                for i in range(self.data.size()):
                    line = self.data.elementAt(i)
                    lineList = [str(line.elementAt(0))]
                    lineList.append(str(line.elementAt(1)))
                    lineList.append(str(line.elementAt(2)))
                    lineList.append(str(line.elementAt(3)))
                    f.write("\t".join(lineList) + "\n")
                f.close()

    def getP(self, pvLine):
        #there is a copy of this on Main
        if self.isDominant:
            p1 = pvLine[2]
            p2 = pvLine[3]
            p3 = pvLine[4]
            p = p1 - 0.5 * (p1+p2-1)
            return p
        else:
            return pvLine[3]

    def calcFalsePositives(self, pv, ci, fdr):
        falses = []
        pys = []
        for i in range(len(pv)):
            p = self.getP(pv[i])
            py = 1-2*abs(p-0.5)
            pys.append(py)
            #if p > ci or p<1-ci:
            #    pys.append(py)
        pys.append(0.0)
        pys.sort()
        rate = []
        maxRank=0
        for i in range(len(pys)):
            if pys[i]<=fdr*i/len(pys):
                maxRank = i
        #print maxRank
        falseReports = []
        for pvLine in pv:
            p = self.getP(pvLine)
            py = 1-2*abs(p-0.5)
            if py in pys:
                if pys.index(py)<=maxRank:
                    falseReports.append("Outlier")
                else:
                    falseReports.append("--")
            else:
                falseReports.append("NA")


        return falseReports

    def initTable(self, lociNames, pv, ci, locusFst):
        colNames = Vector()
        colNames.add('Locus')
        colNames.add('Het')
        colNames.add('Fst')
        colNames.add('P(simulated Fst < sample Fst)')
        colNames.add('FDR')
        data = Vector()
        self.data = data
        falses = self.calcFalsePositives(pv, ci, self.fdr)
        currentPos = 0
        for i in range(len(lociNames)):
            line = Vector()
            locus = lociNames[i]
            line.add(locus)
            if not locusFst[i]:
                line.add("NA")
                line.add("NA")
                line.add("NA")
                line.add("NA")
            else:
                line.add(str(pv[currentPos][0]))
                line.add(str(pv[currentPos][1]))
                line.add(str(self.getP(pv[currentPos])))
                line.add(str(falses[currentPos]))
                currentPos += 1
            data.add(line)
        self.table = JTable(data, colNames)
        self.table.setDefaultRenderer(Class.forName("java.lang.Object"),
               ColorRenderer(data, ci, self.chart.neuColor,
                   self.chart.balColor, self.chart.posColor))

    def __init__(self, frame, chart, lociNames, pv,
                 ci, confLines, locusFst, isDominant, fdr):
        JDialog(frame)
        self.chart = chart
        self.frame = frame
        self.confLines = confLines
        self.isDominant = isDominant
        self.fdr = fdr
        pane = self.getRootPane().getContentPane()

        pane.setLayout(BorderLayout())

        self.initTable(lociNames, pv, ci, locusFst)
        scrollPane = JScrollPane(self.table)
        osName = System.getProperty('os.name').lower()

        if not System.getProperty('java.specification.version')[-1] == '5':
            self.table.setFillsViewportHeight(True)
        pane.add(scrollPane, BorderLayout.CENTER)

        buttonPane = JPanel()
        sll = JButton('Save loci list')
        sll.addActionListener(self)
        sll.setActionCommand('SLL')
        buttonPane.add(sll)
        sci = JButton('Save confidence intervals')
        sci.addActionListener(self)
        sci.setActionCommand('SCI')
        buttonPane.add(sci)
        close = JButton('Close')
        close.addActionListener(self)
        close.setActionCommand('Close')
        buttonPane.add(close)
        pane.add(buttonPane, BorderLayout.PAGE_END)


        self.pack()

