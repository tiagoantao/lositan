package temporal;

/**
 *
 * @author Nina Overgaard Therkildsen
 * @author Samitha Samaranayake
 */

import java.io.*;

public class Datacal {

    /**
     * Takes an input file of the form given below and writes a file with the heterozygosity and
     * fdist values.
     * Input format:
     * - 1/0 indicator. alleles by rows in data matrix (1), or generations by rows (0).
     * - No of generations
     * - No of loci
     * - No of alleles at locus 1 # Always 1 or 2, otherwise throw error
     * - Matrix of data at locus 1 either with each row corresponding to the same allele or to the
     *      same generations. # unlike in our setup, all the allele frequencies are specified
     * - No of alleles at locus 2 # Always 1 or 2, otherwise throw error
     * - Matrix...
     *   .
     *   .
     *   .
     * etc.
     * @param inputFile - Allele frequencies over all generations
     * @param outputDir - The set of generations from which to sample
     * @throws none
     * @returns none
     */
    public void compute(String inFile, String outFile) {
        int indicator;
        int numberOfGenerations;
        int numberOfLoci;
        int numberOfAlleles = 0;
        double invSampleSizeSum;
        int temp;
        int tempSum;
        double[][] sampleFreqOverGenerations;
        double[] harmonicMeanSampleSize;
        int[] numValidGenerations;
        int[][] validGenerations;
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
            numberOfGenerations = Integer.parseInt(strLine);
            // Read number of loci
            strLine = readNewLine(br);
            numberOfLoci = Integer.parseInt(strLine);
            sampleFreqOverGenerations = new double[numberOfGenerations][numberOfLoci];
            harmonicMeanSampleSize = new double[numberOfLoci];
            numValidGenerations = new int[numberOfLoci];
            validGenerations = new int[numberOfLoci][numberOfGenerations];
            for (locusCount=0; locusCount<numberOfLoci; locusCount++) {
                strLine = readNewLine(br);
                numberOfAlleles = Integer.parseInt(strLine);
                numValidGenerations[locusCount] = numberOfGenerations;
                if (numberOfAlleles != 1 && numberOfAlleles !=2) {
                    throw new IllegalArgumentException("number_of_alleles must be 1 or 2");
                }
                if (indicator == 0) { // generations by rows in data matrix
                    invSampleSizeSum=0;
                    for (int i=0; i<numberOfGenerations; i++) {
                        strLine = readNewLine(br);
                        strVector = strLine.split("[ ]+");
                        temp = Integer.parseInt(strVector[0]);
                        if (numberOfAlleles == 2) {
                            tempSum = temp + Integer.parseInt(strVector[1]);
                            if (tempSum != 0) {
                                invSampleSizeSum = invSampleSizeSum + (double)1/tempSum;
                                sampleFreqOverGenerations[i][locusCount] = (double)temp / tempSum;
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
                        for (int i = 0; i < numberOfGenerations; i++) {
                            temp = Integer.parseInt(strVector[i]);
                            tempSum = temp + Integer.parseInt(strVector2[i]);
                            if (tempSum != 0) {
                                invSampleSizeSum = invSampleSizeSum + (double) 1 / tempSum;
                                sampleFreqOverGenerations[i][locusCount] = (double) temp / tempSum;
                                validGenerations[locusCount][i] = 1;
                            } else {
                                sampleFreqOverGenerations[i][locusCount] = 0;
                                numValidGenerations[locusCount] = numValidGenerations[locusCount] - 1;
                                validGenerations[locusCount][i] = 0;
                            }
                        }
                    } else {
                        for (int i = 0; i < numberOfGenerations; i++) {
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
            double[] ftempvals = simulator.computeFTemp(
                    sampleFreqOverGenerations, harmonicMeanSampleSize, numValidGenerations, validGenerations);
            double[] heterozygosity = simulator.computeHetroz(
                    sampleFreqOverGenerations, numValidGenerations);
            for (int i=0; i<numberOfLoci; i++) {
                    System.out.format("%.4f %.4f%n", heterozygosity[i], ftempvals[i]);
            }
            writeFile(outFile, heterozygosity, ftempvals);

        } catch (Exception e){//Catch exception if any
            System.out.println("Error: " + e.getMessage());
        }
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
