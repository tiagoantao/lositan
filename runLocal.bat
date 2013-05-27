mkdir scratch
set JYTHONPATH=..\..\scratch;..\..\libs\Lib;..\..\libs;..\..\libs\batik-awt-util.jar;..\..\libs\batik-dom.jar;..\..\libs\batik-svggen.jar;..\..\libs\batik-util.jar;..\..\libs\batik-xml.jar;..\..\libs\iText-2.1.5.jar;..\..\libs\jcommon-1.0.16.jar;..\..\libs\jfreechart-1.0.13.jar
cd src/python
java -Xmx1024m -cp ..\java;..\..\libs\jython.jar org.python.util.jython Main.py
cd ..\..