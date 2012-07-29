/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package temporal;
/**
 *
 * @author Nina Overgaard Therkildsen
 * @author Samitha Samaranayake
 */

import java.io.*;

public class Datacal {

    private double[] harmonicMeanSampleSize;
    private int[][] sampleSize;
    private double Ne;
    private double NeOldStyle[];
    private double[] ftempvals;
    private double[] heterozygosity;
    private boolean initialzed;
    private int numberOfSampledYears;
    private double[][] sampleFreqOverGenerations;
    /**
     * Takes an input file of the form given below and writes a file with the heterozygosity and
     * ftemp values.
     * Input format:
     * - 1/0 indicator. alleles by rows in data matrix (1), or generations by rows (0).
     * - No of generations
     * - No of loci
     * - No of alleles at locus 1 # Always 1 or 2, otherwise throw error
     * - Matrix of data at locus 1 either with each row corresponding to the same allele or to the
     *      same generations. # unlike in the simulation setup, all the allele frequencies are specified
     * - No of alleles at locus 2 # Always 1 or 2, otherwise throw error
     * - Matrix...
     *   .
     *   .
     *   .
     * etc.
     * @param inputFile - input file name with path
     * @param outputFile - output file name with path
     * @throws none
     * @returns none
     */
    public void compute(String inFile, String outFile) {
        int indicator;
        int numberOfLoci;
        int numberOfAlleles = 0;
        double invSampleSizeSum;
        int temp;
        int[] numValidGenerations;
        int[][] validGenerations;
        initialzed = true;
        try {
            FileInputStream fstream = new FileInputStream(inFile);
            DataInputStream in = new DataInputStream(fstream);
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String strLine;
            String strLine2;
            String[] strVector;
            String[] strVector2;
            int locusCount=0;
            // Read the file one line at a time
            // Read indicator value
            strLine = readNewLine(br);
            indicator = Integer.parseInt(strLine);
            if (indicator != 0 && indicator !=1) {
                throw new IllegalArgumentException("Indicator must be 0 or 1");
            }
            // Read number of generations
            strLine = readNewLine(br);
            numberOfSampledYears = Integer.parseInt(strLine);
            // Read number of loci
            strLine = readNewLine(br);
            numberOfLoci = Integer.parseInt(strLine);
            sampleFreqOverGenerations = new double[numberOfSampledYears][numberOfLoci];
            harmonicMeanSampleSize = new double[numberOfLoci];
            numValidGenerations = new int[numberOfLoci];
            validGenerations = new int[numberOfLoci][numberOfSampledYears];
            sampleSize = new int[numberOfSampledYears][numberOfLoci];
            for (locusCount=0; locusCount<numberOfLoci; locusCount++) {
                strLine = readNewLine(br);
                numberOfAlleles = Integer.parseInt(strLine);
                numValidGenerations[locusCount] = numberOfSampledYears;
                if (numberOfAlleles != 1 && numberOfAlleles !=2) {
                    throw new IllegalArgumentException("number_of_alleles must be 1 or 2");
                }
                if (indicator == 0) { // generations by rows in data matrix
                    invSampleSizeSum=0;
                    for (int i=0; i<numberOfSampledYears; i++) {
                        strLine = readNewLine(br);
                        strVector = strLine.split("[ ]+");
                        temp = Integer.parseInt(strVector[0]);
                        if (numberOfAlleles == 2) {
                            sampleSize[i][locusCount] = temp + Integer.parseInt(strVector[1]);
                            if (sampleSize[i][locusCount] != 0) {
                                invSampleSizeSum = invSampleSizeSum + (double)1/sampleSize[i][locusCount];
                                sampleFreqOverGenerations[i][locusCount] = (double)temp / sampleSize[i][locusCount];
                                validGenerations[locusCount][i] = 1;
                            } else  {
                                sampleFreqOverGenerations[i][locusCount] = 0;
                                numValidGenerations[locusCount] = numValidGenerations[locusCount] - 1;
                                validGenerations[locusCount][i] = 0;
                            }
                        } else {
                            sampleFreqOverGenerations[i][locusCount] = 1;
                            invSampleSizeSum = invSampleSizeSum + (double)1/temp;
                            validGenerations[locusCount][i] = 1;
                        }
                    }
                    harmonicMeanSampleSize[locusCount] = numValidGenerations[locusCount]/(invSampleSizeSum*2);
                } else {
                    strLine = readNewLine(br);
                    strVector = strLine.split("[ ]+");
                    invSampleSizeSum = 0;
                    if (numberOfAlleles == 2) {
                        strLine2 = readNewLine(br);
                        strVector2 = strLine2.split("[ ]+");
                        for (int i = 0; i < numberOfSampledYears; i++) {
                            temp = Integer.parseInt(strVector[i]);
                            sampleSize[i][locusCount] = temp + Integer.parseInt(strVector2[i]);
                            if (sampleSize[i][locusCount] != 0) {
                                invSampleSizeSum = invSampleSizeSum + (double) 1 / sampleSize[i][locusCount];
                                sampleFreqOverGenerations[i][locusCount] = (double) temp / sampleSize[i][locusCount];
                                validGenerations[locusCount][i] = 1;
                            } else {
                                sampleFreqOverGenerations[i][locusCount] = 0;
                                numValidGenerations[locusCount] = numValidGenerations[locusCount] - 1;
                                validGenerations[locusCount][i] = 0;
                            }
                        }
                    } else {
                        for (int i = 0; i < numberOfSampledYears; i++) {
                            sampleFreqOverGenerations[i][locusCount] = 1;
                            invSampleSizeSum = invSampleSizeSum + (double) 1/Integer.parseInt(strVector[i]);
                            validGenerations[locusCount][i] = 1;
                        }
                    }
                    harmonicMeanSampleSize[locusCount] = numValidGenerations[locusCount] / (invSampleSizeSum * 2);
                }
            }
            //Close the input stream
            in.close();
            Simulator simulator = new Simulator();
            ftempvals = simulator.computeFTemp(
                    sampleFreqOverGenerations, harmonicMeanSampleSize, numValidGenerations, validGenerations);
            heterozygosity = simulator.computeHetroz(
                    sampleFreqOverGenerations, numValidGenerations);
            writeFile(outFile, heterozygosity, ftempvals);

        } catch (Exception e){//Catch exception if any
            System.out.println("Error: " + e.getMessage());
        }
    }

    // Deprecated
    // The Fk mertic is used instead of Fc now
    private double computeFc(double x, double y) {
        return (double)Math.pow(x-y,2) / ((x+y)/2 - x*y);
    }

    private double computeFk(double x, double y) {
        return (double)Math.pow(x-y,2) / ((x+y)/2 - Math.pow((x+y)/2,2));
    }

    // Deprecated
    // This is the old version of the function that uses the Fc metric instead of Fk
    private void computeNeWrapperOld(int startGen, int endGen, int numberOfGenerations) {
        NeOldStyle = new double[sampleFreqOverGenerations[0].length];
        double Fc;
        int startSampleSize, endSampleSize;
        for (int i=0; i<sampleFreqOverGenerations[0].length;i++) {
            Fc = computeFc(sampleFreqOverGenerations[startGen][i], sampleFreqOverGenerations[endGen][i]);
            startSampleSize = sampleSize[startGen][i];
            endSampleSize = sampleSize[endGen][i];
            if (Double.isNaN(Fc)) {
                NeOldStyle[i] = Double.NaN;
            } else {
                NeOldStyle[i] = (numberOfGenerations) / (double)(2*(Fc - 1/(double)(2*startSampleSize) - 1/(double)(2*endSampleSize)));
                // Negative Ne estimate implies that Ne is infinitely large, so we replace it by a "large" number
                if (NeOldStyle[i] < 0) {
                    NeOldStyle[i] = 100000;
                }
            }
        }
    }

    private void computeNeWrapper(int startGen, int endGen, int numberOfGenerations) {
        double Fk;
        double Fmean = 0;
        double[] Fsum = new double[sampleFreqOverGenerations[0].length];
        int startSampleSize, endSampleSize;
        for (int i = 0; i < sampleFreqOverGenerations[0].length; i++) {
            if (alleleFreqCheck(i, startGen, endGen)) {
                Fk = computeFk(sampleFreqOverGenerations[startGen][i], sampleFreqOverGenerations[endGen][i]);
                startSampleSize = sampleSize[startGen][i];
                endSampleSize = sampleSize[endGen][i];
                if (Double.isNaN(Fk)) {
                    Fsum[i] = Double.NaN;
                } else {
                    Fsum[i] = Fk - (1 / (double) (startSampleSize)) - (1 / (double) (endSampleSize));
                }
            } else {
                Fsum[i] = Double.NaN;
            }
        }
        Fmean = vectorMean(Fsum);
        Ne = numberOfGenerations / (double) (2 * Fmean);
        if (Ne < 0) {
            Ne = 10000;
        }
    }

    private boolean alleleFreqCheck(int locus, int startGen, int endGen) {
        double startFreq = sampleFreqOverGenerations[startGen][locus];
        double endFreq = sampleFreqOverGenerations[endGen][locus];
        double meanFreq = (startFreq + endFreq) / 2;
        if (meanFreq > 0.05 && meanFreq < 0.95) {
            return true;
        } else {
            return false;
        }
    }
        /**
     * Takes the number of generations that the samples span and computes the Ne value for the population. 
     * @param numberOfGenerations - number of generations that the samples span. Could be different from the 
     *  index of the last sample number
     * @throws none
     * @returns none
     */
    public void computeNe(int numberOfGenerations) {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return;
        }
        computeNeWrapper(0,numberOfSampledYears-1, numberOfGenerations);
    }

    public double[] getFtemps() {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return null;
        }
        return ftempvals;
    }

    public double getFtempMean() {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return 0;
        }
        return vectorMean(ftempvals);
    }

    public double[] getHes() {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return null;
        }
        return heterozygosity;
    }

    public double getNe() {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return 0;
        }
        return Ne;
    }

    public double getSampleSize() {
        if (!initialzed) {
            System.out.println("Datacal class uninitialized! Please run Datacal.compute first.");
            return 0;
        }
        return vectorHarmMean(harmonicMeanSampleSize);
    }


    private String readNewLine(BufferedReader br) {
        String nl = "";
        try {
            do {
                nl = br.readLine();
            } while (nl.isEmpty());
        } catch (Exception e){//Catch exception if any
            System.out.println("Error: " + e.getMessage());
        }
        return nl;
    }

    private double vectorMean(double[] vector) {
        double sum=0;
        int length = vector.length;
        for (int i=0;i < vector.length; i++) {
            if (Double.isNaN(vector[i])) {
                length = length - 1;
            } else {
                sum = sum + vector[i];
            }
        }
        return sum/length;
    }

    private double vectorHarmMean(double[] vector) {
        double invSum=0;
        int length = vector.length;
        for (int i=0;i < vector.length; i++) {
            if (Double.isNaN(vector[i])) {
                length = length - 1;
            } else {
                invSum = invSum + 1/(double)vector[i];
            }
        }
        return length/(double)invSum;
    }

    private void writeFile(String fileName, double[] heterozygosity, double[] ftemp) {
      try {
        // Create file
          String line;
          String fline;
          FileWriter fstream = new FileWriter(fileName);
          BufferedWriter out = new BufferedWriter(fstream);
            for (int i=0; i< heterozygosity.length; i++) {
                line = "%.4f %.4f%n";
                fline = String.format(line, heterozygosity[i], ftemp[i]);
                out.write(fline);
            }
          //Close the output stream
          out.close();
          } catch (Exception e){//Catch exception if any
            System.err.println("Error: " + e.getMessage());
          }
      }

    public static void main(String[] args) {
        if (args.length == 0) {
                System.out.println("usage: debug_level number_of_loci number_of_samples " +
                     "population_size first_generation_to_sample [other_generations_to_sample]");
        } else {
            Datacal dc = new Datacal();
            dc.compute(args[0], args[1]);
        }
    }
}
