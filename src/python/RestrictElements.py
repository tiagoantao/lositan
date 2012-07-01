from Shared import error
from java.awt import BorderLayout, Dimension, GridLayout
from java.awt.event import ActionListener
from javax.swing import DefaultListModel, JDialog, JLabel, JButton, JPanel, JList, JScrollPane

def _changeList(dialog, orig_list, orig_model, dest_model, requiresTwo = True):
    #sel = orig_list.getSelectedIndex()
    #if sel == -1:
    #    return
    #value = orig_model.get(sel)
    #orig_model.remove(sel)
    #dest_model.addElement(value)
    sels = orig_list.getSelectedIndices()
    if requiresTwo:
        if len(sels) > orig_model.getSize() - 2:
            error(dialog, 'At least 2 elements have to remain')
            return
    selsA = []
    for sel in sels:
        selsA.append(sel)
    selsA.sort(lambda x, y : cmp(y,x))
    for sel in selsA:
        value = orig_model.get(sel)
        orig_model.remove(sel)
        dest_model.addElement(value)

class RestrictionDialog(JDialog, ActionListener):
    def actionPerformed(self, event):
        option = event.getActionCommand()
        #print option
        if option == 'Select':
            _changeList(self, self.rem_list, self.rem, self.sel, False)
        elif option == 'Remove':
            _changeList(self, self.sel_list, self.sel, self.rem)
        elif option == 'Exit':
            sel = []
            selElems = self.sel.elements()
            while selElems.hasMoreElements():
                sel.append(str(selElems.nextElement()))
            rem = []
            remElems = self.rem.elements()
            while remElems.hasMoreElements():
                rem.append(str(remElems.nextElement()))
            self.pingFun(sel, rem)
            self.dispose()

    def createList(self, content):
        model = DefaultListModel()
        for elem in content:
            model.addElement(elem)
        list = JList(model)
        listPane = JScrollPane(list) 
        listPane.setPreferredSize(Dimension(250, 400))
        return listPane, list, model

    def __init__(self, frame, what, all, removed, pingFun):
        JDialog.__init__(self,frame, what)
        self.frame   = frame
        self.all     = all
        self.removed = removed 
        self.pingFun = pingFun
        pane = self.getRootPane().getContentPane()

        self.sel_pane, self.sel_list, self.sel = self.createList(all)
        pane.add(self.sel_pane, BorderLayout.WEST)

        button_panel = JPanel()
        button_panel.setLayout(GridLayout(8,1))
        button_panel.add(JLabel('<-- Selected'))
        button_panel.add(JLabel('Removed -->'))
        select = JButton('Select')
        select.setActionCommand('Select')
        select.addActionListener(self)
        button_panel.add(select)
        button_panel.add(JLabel(''))
        restrict = JButton('Remove')
        restrict.setActionCommand('Remove')
        restrict.addActionListener(self)
        button_panel.add(restrict)
        button_panel.add(JLabel(''))
        quit = JButton('Exit')
        quit.setActionCommand('Exit')
        quit.addActionListener(self)
        button_panel.add(quit)
        button_panel.add(JLabel(''))
        pane.add(button_panel, BorderLayout.CENTER)

        self.rem_pane, self.rem_list, self.rem = self.createList(removed)
        pane.add(self.rem_pane, BorderLayout.EAST)


        warning_panel = JPanel()
        warning_panel.add(JLabel("Warning: Removing/adding loci or pops might take some time!"))
        pane.add(warning_panel, BorderLayout.NORTH)

        self.pack()

