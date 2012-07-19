cwd=`pwd`
mkdir scratch 2>/dev/null
echo -n > x
find libs/ -name \*jar|xargs -I W echo -n :$cwd/W > x
JYTHONPATH=$cwd/scratch:$cwd/libs/Lib:$cwd/libs`cat x`
rm x
export JYTHONPATH
cd src/python

pwd
echo java -Xmx1024m -cp ../java:../../libs/jython.jar org.python.util.jython Main.py $@
java -Xmx1024m -cp ../java:../../libs/jython.jar org.python.util.jython Main.py $@
