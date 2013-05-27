#!/bin/bash

wget http://sourceforge.net/projects/jfreechart/files/3.%20JCommon/1.0.16/jcommon-1.0.16.tar.gz/download
mv download jcommon-1.0.16.tar.gz

wget http://sourceforge.net/projects/jfreechart/files/1.%20JFreeChart/1.0.13/jfreechart-1.0.13.tar.gz/download
mv download jfreechart-1.0.13.tar.gz

wget http://www.gtlib.gatech.edu/pub/apache/xmlgraphics/batik/batik-1.7.zip

wget http://sourceforge.net/projects/itext/files/iText/iText5.0.2/iText-5.0.2.jar/download
mv download iText-5.0.2.jar

wget http://sourceforge.net/projects/jython/files/jython/2.5.1/jython_installer-2.5.1.jar/download
mv download jython_installer-2.5.1.jar

git clone git://github.com/biopython/biopython.git

rm -rf tmp
mkdir tmp
mv *tar.gz *zip *jar biopython tmp
