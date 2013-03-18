mkdir scratch 2>/dev/null
cp support/*example* scratch
cd scratch
unzip ../support/allfdist >/dev/null
cd ../src/java
javac -cp . -source 1.6 -target 1.6 temporal/Simulator.java
javac -cp . -source 1.6 -target 1.6 temporal/Datacal.java
