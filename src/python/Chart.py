from jarray import array
from java.util import Random
from java.lang import String

from java.awt import Color, Dimension
from java.awt.geom import Ellipse2D, Rectangle2D
from java.io import File, OutputStreamWriter, FileOutputStream, BufferedOutputStream
from java.lang import String
from javax.swing import JPanel, JLabel, ImageIcon, JFileChooser
#from javax.swing.filechooser import FileNameExtensionFilter

from org.apache.batik.dom import GenericDOMImplementation
from org.apache.batik.svggen import SVGGraphics2D
from org.w3c.dom import DOMImplementation
from org.w3c.dom import Document

from com.lowagie.text import Document as TextDocument, Rectangle
from com.lowagie.text.pdf import PdfWriter, DefaultFontMapper

from org.jfree.chart import  ChartFactory, ChartPanel, JFreeChart, ChartUtilities
from org.jfree.chart.annotations import XYTextAnnotation
from org.jfree.chart.axis import NumberAxis
from org.jfree.chart.labels import StandardXYToolTipGenerator
from org.jfree.chart.plot import PlotOrientation
from org.jfree.chart.renderer.xy import DeviationRenderer, XYLineAndShapeRenderer, XYAreaRenderer, XYDifferenceRenderer, XYDotRenderer
from org.jfree.data.xy import XYSeriesCollection, YIntervalSeriesCollection, XYSeries, YIntervalSeries, DefaultTableXYDataset
from org.jfree.ui import TextAnchor

from Shared import info

class FDistToolTipGenerator(StandardXYToolTipGenerator):
    def __init__ (self, lociNames):
        self.lociNames = lociNames

    def generateToolTip(self, dataset, series, item):
        #print item, self.lociNames[item], dataset.getSeries(series).items[item].getX(),
        #print dataset.getSeries(series).items[item].getY()
        return self.lociNames[item]

class Chart(JPanel):
    def _createEmptyChart(self, dataset = None):
        if self.isTemporal:
            hText = "Hs"
            fText = "Fgt"
        else:
            hText = "He"
            fText = "Fst"
        chart = ChartFactory.createXYLineChart(
            self.title,               # chart title
            hText,                    # x axis label
            fText,                    # y axis label
            dataset,                  # data
            PlotOrientation.VERTICAL,
            True,                     # include legend
            True,                     # tooltips
            False                     # urls
        )
        chart.setBackgroundPaint(Color.white)
        # get a reference to the plot for further customisation...
        # change the auto tick unit selection to integer units only...
        #rangeAxis = plot.getRangeAxis()
        #rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits())
        self.confArea = None
        return chart

    def setSelLoci(self, pv, allLoci, selLoci):
        self.pv = pv
        self.allLoci = allLoci
        self.selLoci = selLoci
        self.drawLabels()

    def drawLabels(self):
        if not hasattr(self, 'pv'): return
        plot = self.chart.getPlot()
        plot.clearAnnotations()
        red = 0
        for i in range(len(self.valMarkers)):
            if not self.valMarkers[i]:
                red += 1
                continue
            if self.allLoci[i] in self.selLoci:
                if not self.labelSelected: continue
            else:
                if not self.labelNeutral: continue

            x = self.pv[i-red][0]
            y = self.pv[i-red][1]
            locus = self.allLoci[i]
            note = XYTextAnnotation(locus, x + 0.002, y + 0.002)
            note.setTextAnchor(TextAnchor.BOTTOM_LEFT)
            plot.addAnnotation(note)


    def setMarkers(self, markers):
        self.markers = XYSeries("Markers")
        self.maxX = 0.0
        self.maxY = 0.0
        self.minY = -0.05
        self.out = []
        self.valMarkers = markers
        for marker in markers:
            if not marker:
                continue
            if marker[0]<2 and marker[0] > self.maxX:
                self.maxX = marker[0]
            if marker[1]<2 and marker[1] > self.maxY:
                self.maxY = marker[1]
            if marker[1]>-2 and marker[1] < self.minY:
                self.minY = marker[1]

            #self.markers.add(marker[0], max([0.0, marker[1]]))
            self.markers.add(marker[0], marker[1])
        self.maxX = max([0.501, self.maxX + 0.001])
        self.maxX = min([1, self.maxX])
        self.maxY += 0.05
        self.minY -= 0.05

    def setTop(self, markers):
        #setBottom has to be done before, as setMarkers
        self.top = YIntervalSeries("Candidate neutral")
        self.limit = YIntervalSeries("Candidate positive selection")
        if len(markers) > 1:
            #if self.maxY > markers[0][1]:
            #    self.limit.add(0.0, markers[0][1], markers[0][0], markers[0][1])
            #else: #It does not really matter
            #    self.limit.add(0.0, -1, 1.1, 1.1)
            self.limit.add(0.0, markers[0][1], markers[0][1], 1.1)
        for i in range(len(markers)):
            self.top.add(markers[i][0], self.bottomList[i][1],self.bottomList[i][1],
                markers[i][1] )
            if self.maxY > markers[i][1]:
                self.limit.add(markers[i][0], markers[i][1],markers[i][1],
                    1.1)
            else: #It does not really matter
                self.limit.add(markers[i][0], markers[i][1],markers[i][1], 1.1)
            #if markers[i][0] > self.maxX: break
            #We do this at the end to fill the whole graphic

    def setBottom(self, markers):
        #print markers
        self.bottomList = map (
            lambda (x,y): (x,y),
            markers) #legacy, can remove...
        self.bottom = YIntervalSeries("Candidate balancing selection")
        if len(markers) > 0:
            self.bottom.add(0.0, -1.0, -1.0, self.bottomList[0][1])
        for marker in self.bottomList:
            self.bottom.add(marker[0], -1.0, -1.0, marker[1])
            #if marker[0] > self.maxX: break
            #We do this at the end to fill the whole graphic


    def updateChartDataset(self, drawLabels=True):
        dataset = XYSeriesCollection()
        #self._calculateConfArea()
        #dataset.addSeries(self.confArea)
        dataset.addSeries(self.markers)
        plot = self.chart.getPlot()
        rangeAxis = plot.getRangeAxis()
        domainAxis = plot.getDomainAxis()
        rangeAxis.setRange(self.minY, self.maxY) #change
        domainAxis.setRange(self.minX, self.maxX)
        #plot.setBackgroundPaint(Color.lightGray);
        #plot.setAxisOffset(new RectangleInsets(5.0, 5.0, 5.0, 5.0));
        #plot.setDomainGridlinePaint(Color.white);
        #plot.setRangeGridlinePaint(Color.white);

        markerRenderer = XYLineAndShapeRenderer(False, True)
        #print self.markerColor
        markerRenderer.setSeriesPaint(0, self.markerColor)
        markerRenderer.setSeriesShape(0, Ellipse2D.Double(-3, -3, 6, 6))
        #markerRenderer.setToolTipGenerator(FDistToolTipGenerator(self.pointNames))
        plot.setRenderer(0, markerRenderer)
        plot.setDataset(0, dataset)
        dataset = XYSeriesCollection()
        if self.drawCI:
            dataset = YIntervalSeriesCollection()
            CIRenderer = DeviationRenderer(True, False)
            #CIRenderer.setOutline(True)
            #CIRenderer.setRoundXCoordinates(True)
            dataset.addSeries(self.bottom)
            dataset.addSeries(self.top)
            dataset.addSeries(self.limit)
            CIRenderer.setSeriesFillPaint(0, self.balColor)
            CIRenderer.setSeriesFillPaint(1, self.neuColor)
            CIRenderer.setSeriesFillPaint(2, self.posColor)
            CIRenderer.setSeriesPaint(0, self.balColor)
            CIRenderer.setSeriesPaint(1, self.neuColor)
            CIRenderer.setSeriesPaint(2, self.posColor)
            plot.setDataset(1, dataset)
            plot.setRenderer(1, CIRenderer)
        plot.setDataset(1, dataset)
        if drawLabels: self.drawLabels()

    def resetData(self, justAnnots = False):
        if not justAnnots:
            self.markers = XYSeries("Markers")
        self.drawCI = False
        self.chart.getPlot().clearAnnotations()
        if hasattr(self, 'pv'):
            del(self.pv)
        self.updateChartDataset()

    def save(self, parent, format):
        chooser = JFileChooser()
        #filter = FileNameExtensionFilter(
        #    format + " files",
        #    array([format, format.lower()], String))
        #chooser.setFileFilter(filter);
        returnVal = chooser.showSaveDialog(parent)
        if returnVal == JFileChooser.APPROVE_OPTION:
            fileName = chooser.getSelectedFile().getPath()
            if not fileName.upper().endswith('.' + format):
                fileName += '.' + format.lower()
            file = File(fileName)
        else:
            return
        if format == 'PNG':
            ChartUtilities.saveChartAsPNG(file, self.chart, self.exportX, self.exportY)
        elif format == 'SVG':
            domImpl = GenericDOMImplementation.getDOMImplementation()
            doc = domImpl.createDocument(None, "svg", None)
            svgGen = SVGGraphics2D(doc)
            svgGen.getGeneratorContext().setPrecision(6)
            self.chart.draw(svgGen,
               Rectangle2D.Double(0, 0, self.exportX, self.exportY), None)
            out = OutputStreamWriter(FileOutputStream(file), "UTF-8")
            svgGen.stream(out, True) #True is for useCSS
            out.close()
        elif format == 'PDF':
            mapper = DefaultFontMapper()
            pageSize = Rectangle(self.exportX, self.exportY)
            doc = TextDocument(pageSize, 50, 50, 50, 50)
            out = BufferedOutputStream(FileOutputStream(file))
            writer = PdfWriter.getInstance(doc, out)
            doc.open()
            cb = writer.getDirectContent()
            tp = cb.createTemplate(self.exportX, self.exportY)
            g2 = tp.createGraphics(self.exportX, self.exportY, mapper)
            r2D = Rectangle2D.Double(0, 0, self.exportX, self.exportY)
            self.chart.draw(g2, r2D)
            g2.dispose()
            cb.addTemplate(tp, 0, 0)
            doc.close()
            #out.close()

    def __init__(self, width, height, isTemporal=False):
        JPanel()
        self.isTemporal = isTemporal
        self.minY = 0.0  # -0.05
        self.minX = 0.0  # -0.02
        self.maxX = 0.5  # 0.52
        self.maxY = 1.0
        self.drawCI = False
        if isTemporal:
            self.title = "Fgt/Hs"
        else:
            self.title = "Fst/He"
        self.labelSelected = True
        self.labelNeutral = False
        self.posColor = Color.RED
        self.neuColor = Color.LIGHT_GRAY
        self.balColor = Color.YELLOW
        self.markerColor = Color.BLUE
        self.exportX = width
        self.exportY = height
        self.chart = self._createEmptyChart()
        self.chart.setAntiAlias(False)
        self.resetData()
        self.cp = ChartPanel(self.chart)
        self.cp.setDisplayToolTips(True)
        self.cp.setPreferredSize(Dimension(width, height))
        self.add(self.cp)
