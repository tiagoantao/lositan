from java.lang import String

from java.awt import BasicStroke, Color, Dimension, Font
from java.awt.image import BufferedImage
from javax.swing import JPanel, JLabel, ImageIcon

from org.jfree.chart import  ChartFactory, ChartPanel, JFreeChart
from org.jfree.chart.plot import DialShape, MeterInterval, MeterPlot
from org.jfree.data import Range
from org.jfree.data.general import DefaultValueDataset


class Meter(JPanel):
    def getValue(self):
        return self.plot.getDataset().getValue()

    def setValue(self, value):
        self.plot.setDataset(DefaultValueDataset(value))

    def increment(self, value):
        self.setValue(self.getValue() + value)

    def getRange(self):
        return self.range

    def setRange(self, range):
        self.range = range
        self.plot.clearIntervals()
        self.plot.setRange(Range(0, range))
        self.plot.addInterval(MeterInterval("", Range(range/2.0,range/2.0)))

    def __init__(self, width, height, range):
        JPanel()
        plot = MeterPlot(DefaultValueDataset(0))
        self.plot = plot
        self.setRange(range)
        #plot.addInterval(MeterInterval("Normal", Range(0.0, 35.0),
        #        Color.lightGray, BasicStroke(2.0),
        #        Color(0, 255, 0, 64)))
        #plot.addInterval(MeterInterval("Warning", Range(35.0, 50.0),
        #        Color.lightGray, BasicStroke(2.0), Color(255, 255, 0, 64)))
        #plot.addInterval(MeterInterval("Critical", Range(50.0, 60.0),
        #        Color.lightGray, BasicStroke(2.0),
        #        Color(255, 0, 0, 128)))
        plot.setNeedlePaint(Color.darkGray)
        plot.setDialBackgroundPaint(Color.white)
        plot.setDialOutlinePaint(Color.white)
        plot.setDialShape(DialShape.CHORD)
        plot.setMeterAngle(260)
        plot.setTickLabelsVisible(True)
        plot.setTickLabelFont(Font("Dialog", Font.BOLD, 10));
        plot.setTickLabelPaint(Color.darkGray)
        plot.setTickSize(5.0)
        plot.setTickPaint(Color.lightGray)

        plot.setValuePaint(Color.black)
        plot.setValueFont(Font("Dialog", Font.BOLD, 14));
        plot.setUnits("k sims")

        chart = JFreeChart("Simulations computed",
                JFreeChart.DEFAULT_TITLE_FONT, plot, False)
        self.chart = chart
        chart.setBackgroundPaint(Color.white)
        cp = ChartPanel(chart)
        cp.setPreferredSize(Dimension(width, height))
        self.add(cp)

