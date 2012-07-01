from Shared import error
from java.lang import Thread
from java.awt import BorderLayout, Dimension, GridLayout
from java.awt.event import ActionListener
from javax.swing import DefaultListModel, JDialog, JLabel, JButton, JPanel, JList, JScrollPane

class LoadDialog(JDialog, ActionListener):
    def __init__(self, frame, what):
        JDialog.__init__(self,frame, what, False)
        self.frame   = frame

        pane = self.getRootPane().getContentPane()

        panel = JPanel()
        panel.add(JLabel('Current population'))
        self.status = JLabel("                                ")
        panel.add(self.status)
        pane.add(panel)
        
        self.pack()
        self.show()

    def update_status(self, curr):
        self.status.setText("%d" % (curr,))
        Thread.yield()

