from java.awt import BorderLayout, Dimension, GridLayout
from java.awt.event import ActionListener
from javax.swing import DefaultListModel, JDialog, JLabel, JButton, JPanel, JList, JScrollPane, JTextField
from javax.swing.event import ListSelectionListener

def _changeList(list, model, newValue):
    sel = list.getSelectedIndex()
    if sel == -1:
        return
    model.set(sel, newValue)

class EditTextList(JDialog, ActionListener, ListSelectionListener):
    def valueChanged(self, event):
        idx = event.getFirstIndex()
        text = self.ent_list.getSelectedValue()
        #print text
        self.text.setText(text)
        self.pack()

    def actionPerformed(self, event):
        option = event.getActionCommand()
        #print option
        if option == 'Change':
            _changeList(self.ent_list, self.ent, self.text.getText())
        elif option == 'Exit':
            ent = []
            entElems = self.ent.elements()
            while entElems.hasMoreElements():
                ent.append(str(entElems.nextElement()))
            self.pingFun(ent)
            self.dispose()

    def createList(self, content):
        model = DefaultListModel()
        for elem in content:
            model.addElement(elem)
        list = JList(model)
        list.addListSelectionListener(self)
        listPane = JScrollPane(list) 
        listPane.setPreferredSize(Dimension(250, 400))
        return listPane, list, model

    def __init__(self, frame, what, entries, pingFun):
        JDialog(frame, what)
        self.frame   = frame
        self.entries = entries
        self.pingFun = pingFun
        pane = self.getRootPane().getContentPane()

        self.ent_pane, self.ent_list, self.ent = self.createList(entries)
        pane.add(self.ent_pane, BorderLayout.WEST)

        actionPanel = JPanel()
        actionPanel.setLayout(GridLayout(20, 1))
        self.text = JTextField(20)
        actionPanel.add(self.text)
        change = JButton('Change')
        change.setActionCommand('Change')
        change.addActionListener(self)
        actionPanel.add(change)
        actionPanel.add(JLabel(''))
        quit = JButton('Exit')
        quit.setActionCommand('Exit')
        quit.addActionListener(self)
        actionPanel.add(quit)
        actionPanel.add(JLabel(''))
        pane.add(actionPanel, BorderLayout.CENTER)

        self.pack()

