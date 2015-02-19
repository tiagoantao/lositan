#!/bin/bash
set -e
rm -rf libs
mkdir libs 2>/dev/null
cd tmp

tar zxf jfreechart-1.0.13.tar.gz
cp jfreechart-1.0.13/lib/jcommon-1.0.16.jar jfreechart-1.0.13/lib/iText-2.1.5.jar jfreechart-1.0.13/lib/jfreechart-1.0.13.jar  ../libs
rm -rf jfreechart-1.0.13

rm -rf batik-1.7
unzip batik-1.7.zip >/dev/null
cd batik-1.7/lib
cp batik-awt-util.jar batik-dom.jar batik-svggen.jar batik-util.jar batik-xml.jar ../../../libs
cd ../..
rm -rf batik-1.7


cp jython.jar ../libs
mkdir jopen
cd jopen
unzip ../jython.jar
mv Lib ../../libs
cd ..
rm -rf jopen

#cp iText-5.0.2.jar ../libs

cd biopython
rm -rf Tests/ Scripts/ BioSQL/ CONTRIB DEPRECATED LICENSE NEWS MANIFEST.in Doc/ setup.py README
cd Bio
ls -I _py3k -I PopGen -I __init__.py -I ParserSupport.py -I File.py | xargs rm -rf
cd ..
cd ..
cp -R biopython/Bio ../libs

cd ..
