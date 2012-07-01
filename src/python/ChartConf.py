from java.awt import GridLayout, Color
from java.awt.event import ActionEvent, ActionListener, MouseAdapter
from javax.swing import JCheckBox, JFrame, JDialog, JLabel, JTextField, JButton, JPanel, JColorChooser
from Chart import Chart

class MouseProcessor(MouseAdapter):
    def __init__(self, frame, panel):
        self.frame = frame
        self.panel = panel

    def mouseClicked(self, event):
        color = JColorChooser.showDialog(self.frame, "Enter Color",
            self.panel.getBackground())
        if color <> None:
            self.panel.setBackground(color)


class ChartConf(JDialog, ActionListener):
    def actionPerformed(self, event):
        option = event.getActionCommand()
        #print option
        if option == 'Change':
            self.pingFun(self)
        elif option == 'Exit':
            self.dispose()

    def getMarkerColor(self):
        return self.markerPanel.getBackground()

    def getPosColor(self):
        return self.posPanel.getBackground()

    def getNeuColor(self):
        return self.neuPanel.getBackground()

    def getBalColor(self):
        return self.balPanel.getBackground()

    def getSelLabel(self):
        return self.selLabel.isSelected()

    def getNeuLabel(self):
        return self.neuLabel.isSelected()

    def createColorPanel(self, color, pane):
        colorPanel = JPanel()
        colorPanel.setBackground(color)
        colorPanel.addMouseListener(MouseProcessor(self, colorPanel))
        pane.add(colorPanel)
        return colorPanel

    def __init__(self, frame, chart, pingFun):
        JDialog(frame)
        self.setTitle('Chart Settings')
        self.setModal(True)
        self.pingFun = pingFun
        pane = self.getRootPane().getContentPane()
        pane.setLayout(GridLayout(7,2))
        pane.add(JLabel('Marker color'))
        self.markerPanel = self.createColorPanel(chart.markerColor, pane)
        pane.add(JLabel('Positive selection color'))
        self.posPanel = self.createColorPanel(chart.posColor, pane)
        pane.add(JLabel('Neutral color'))
        self.neuPanel = self.createColorPanel(chart.neuColor, pane)
        pane.add(JLabel('Balancing selection color '))
        self.balPanel = self.createColorPanel(chart.balColor, pane)

        self.add(JLabel('Label candidate selected loci'))
        self.selLabel = JCheckBox()
        self.selLabel.setSelected(chart.labelSelected)
        self.add(self.selLabel)
        self.add(JLabel('Label candidate neutral loci'))
        self.neuLabel = JCheckBox()
        self.neuLabel.setSelected(chart.labelNeutral)
        self.add(self.neuLabel)

        change = JButton('Change')
        change.setActionCommand('Change')
        change.addActionListener(self)
        pane.add(change)
        exit = JButton('Exit')
        exit.setActionCommand('Exit')
        exit.addActionListener(self)
        pane.add(exit)
        self.pack()

if __name__ == '__main__':
    frame = JFrame("Selection Workbench")
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)
    chart = Chart(300, 200)
    cc = ChartConf(frame, chart, None)
    frame.pack()
    frame.setVisible(1)
    cc.show()

