from javax.swing import JPanel, JLabel, JComboBox, JCheckBox, SwingConstants
from java.awt import GridLayout, Dimension
from Bio.PopGen.GenePop import FileParser

def countPops(rec):
    f2 = FileParser.read(rec.fname)
    pop = 1
    while f2.skip_population():
        pop += 1
    return pop


class SummPanel(JPanel):
    def __init__(self, isTemporal):
        self.isTemporal = isTemporal
        JPanel()
        self.setLayout(GridLayout(6,2))
        self.add(JLabel('Total data'))
        self.add(JLabel(''))
        self.add(JLabel('# Pops' if not isTemporal else "# Gens"))
        self.totalPops = JLabel('0', SwingConstants.RIGHT)
        self.add(self.totalPops)
        self.add(JLabel('# Loci'))
        self.totalLoci = JLabel('0', SwingConstants.RIGHT)
        self.add(self.totalLoci)
        self.add(JLabel('Selected'))
        self.add(JLabel(''))
        self.add(JLabel('# Pops' if not isTemporal else "# Gens"))
        self.selPops = JLabel('0', SwingConstants.RIGHT)
        self.add(self.selPops)
        self.add(JLabel('# Loci'))
        self.selLoci = JLabel('0', SwingConstants.RIGHT)
        self.add(self.selLoci)

    def update(self, rec, popNames, remPops, remLoci):
        total_pops = countPops(rec)
        sel_pops = total_pops - len (remPops)
        total_loci = len(rec.loci_list)
        sel_loci = total_loci - len(remLoci)
        self.totalPops.setText(str(total_pops))
        self.selPops.setText(str(sel_pops))
        self.totalLoci.setText(str(total_loci))
        self.selLoci.setText(str(sel_loci))
