mkdir scratch 2>/dev/null
cp support/*example* scratch
cd scratch
unzip ../support/allfdist >/dev/null
cd ../src/java
javac -source 1.5 -target 1.5 temporal/Simulator.java
javac -source 1.5 -target 1.5 temporal/Datacal.java
