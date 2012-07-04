mkdir scratch 2>/dev/null
cp support/*example* scratch
cd scratch
unzip ../support/allfdist >/dev/null
cd ../src/java
javac temporal/Simulator.java
javac temporal/Datacal.java
