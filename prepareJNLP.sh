echo keytool -genkey -keyalg RSA -keystore keystore -keypass lositan -storepass lositan -alias lositan

. paths.sh
rm -rf deploy
mkdir deploy
mkdir deploy/selwb
mkdir deploy/lib
cp libs/*jar deploy/lib
#cp $JYTHONDIR/jython.jar deploy/lib
cp src/*.jnlp deploy
cp title.gif deploy
cp mcheza.jpg deploy

cp support/allfdist.zip deploy/selwb
mkdir deploy/selwb/py
mkdir deploy/selwb/temporal
cp src/python/* deploy/selwb/py
cp support/example* deploy/selwb/py
cp support/dexample* deploy/selwb/py
cp support/texample* deploy/selwb/py
cp -R libs/Lib/* deploy/selwb/py
cp -R libs/Bio deploy/selwb/py
find deploy -name \*pyc |xargs rm
find deploy -name \*class |xargs rm
find deploy -name \*~ |xargs rm
cd deploy/selwb/py
zip -r ../py.zip * >/dev/null
cd ..
rm -rf py
cd ../..
cd src/java
#javac -cp ../../deploy/lib/jython.jar Boot.java
javac -source 1.5 -target 1.5 -cp ../../deploy/lib/jython.jar Boot.java temporal/Datacal.java temporal/Simulator.java
cd ../..
cp src/java/Boot.class deploy/selwb
cp src/java/temporal/Simulator.class deploy/selwb/temporal
cp src/java/temporal/Datacal.class deploy/selwb/temporal
cd deploy/selwb
jar cvfm ../lib/selwb.jar ../../mymanifest .
cd ..
rm -rf selwb
cd lib
for i in *jar; do
    echo $i
    jarsigner -digestalg SHA1 -sigalg MD5withRSA -keystore ../../keystore -storepass lositan $i lositan;
done

cd ../..
