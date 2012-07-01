from javax.swing import JPanel, JLabel, SwingConstants
from java.awt import GridLayout, Color

class StatusPanel(JPanel):
    def __init__(self):
        JPanel()
        self.setLayout(GridLayout(1,1))
        #self.add(JLabel('SELWB 1.0'))
        self.statusLabel = JLabel('Idle', SwingConstants.CENTER)
        self.statusLabel.setBackground(Color.GREEN)
        self.statusLabel.setOpaque(True)
        self.add(self.statusLabel)

    def setStatus(self, str, bgColor = Color.GREEN):
        self.statusLabel.setText(str)
        self.statusLabel.setBackground(bgColor)
