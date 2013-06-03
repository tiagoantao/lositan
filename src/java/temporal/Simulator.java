package temporal;


import java.io.BufferedWriter;
import java.io.FileWriter;

/**
 *
 * @author Nina Overgaard Therkildsen
 * @author Samitha Samaranayake
 */
public class Simulator {
	    
    /**
     * Creates the allele frequency for each locus in the initial generation. The frequency values are
     * picked such that the frequency is sampled from a distribution that will result in a uniform
     * distribution of heterozygosity.
     * @param numberOfLoci - Number of loci to create
     * @returns frequency values for the first generation
     */
    private double[] createInitialGeneration(int numberOfLoci) {
        double[] firstGeneration = new double[numberOfLoci];
        int discSize = 10000;
        double[] p = new double[discSize];
        double h=0;

        // Create the allele frequency distribution
        for (int i=0; i<discSize; i++) {
            h = (0.5/discSize)*(i+1);
            p[i] = 0.5*(1-Math.sqrt(1-2*h)); // From inverting h = 2*p(1-p)
        }

        // Create the first generation by sampling from this distribution
        for (int i=0; i<numberOfLoci; i++) {
            h = Math.random();
            firstGeneration[i] = p[(int)Math.floor(h*discSize)];
        }
        return firstGeneration;
    }

    /**
     * Advances the population one generation forward by computing the allele frequencies
     * of the new generation.
     * @param prevFreq - Allele frequencies in the previous generation
     * @param populationSize - Size of the population from which to regenerate
     * @returns Allele frequencies of the current generation
     */
    private double computeNewFreq(double prevFreq, int populationSize) {
        double newFreq = 0;
        // Sampling from a pool of population_size * 2 with replacement
        for (int i=0; i<populationSize*2; i++) {
            if (Math.random() < prevFreq) {
                newFreq ++;
            }
        }
        newFreq = newFreq/(populationSize*2);
        return newFreq;
    }

    /**
     * Creates a vector of specific realized sample sizes for each simulated locus. 
     * Varies between 0.85 and 1 * the input sampleSize to mimic the presence of missing data and reduce discretization of He and Ftemp
     */
    private double[] createSamplingVector(int numberOfLoci, int sampleSize) {
        double samplingVariance = 0.15;
		double[] samplingVector = new double[numberOfLoci];
        for (int i=0; i<numberOfLoci; i++) {  
            samplingVector[i] = Math.round(sampleSize * (1 - Math.random()*samplingVariance));
        }
        return samplingVector;
    }
    
   
    /**
     * Simulates the dynamics of the population over a number of generations
     * @param initialGeneration - The allele frequencies of the initial generation
     * @param numberOfGenerations - The number of generations to simulate
     * @param populationSize - The size of the population (needed for regeneration)
     * @returns Allele frequencies over all generations
     */
    private double[][] simulateGenerations(double[] initialGeneration, int numberOfGenerations,
            int populationSize) {
        int numberOfLoci = initialGeneration.length;
        double[][] freqOverGenerations = new double[numberOfGenerations][numberOfLoci];
        for (int i=0;i<numberOfGenerations;i++) {
            if (i==0) {
                freqOverGenerations[0] = initialGeneration;
            } else {
                for (int j=0;j<numberOfLoci;j++) {
                    freqOverGenerations[i][j] = computeNewFreq(freqOverGenerations[i-1][j], populationSize);
                }
            }
        }

        return freqOverGenerations;
    }

    /**
     * Samples a subset of the population from a caller specified set of generations
     * @param freqOverGenerations - Allele frequencies over all generations
     * @param populationSize - The size of the population
     * @param generationsToSample - The set of generations from which to sample
     * @param samplingVector - A vector a specific sample size for each locus in every generation
     * @returns Allele frequencies for the sample set in each of the specified generations
     */
    public double[][] sampleGenerations(double[][] freqOverGenerations, int populationSize, int[] generationsToSample,
                                        double[] samplingVector) {
        double[][] sampleFreqOverGenerations = new double[generationsToSample.length][freqOverGenerations[0].length];
        double temp;
        int adjustedPopulation;
        for (int i=0; i < generationsToSample.length; i++) {
            for (int j=0; j < freqOverGenerations[0].length; j++) {
                sampleFreqOverGenerations[i][j] = 0;
                // calculate the total number of alleles in the population corresponding to the frequency
                temp = freqOverGenerations[generationsToSample[i]][j]*(populationSize*2);
                adjustedPopulation = populationSize*2; // population size after members are sampled out
                // sample without replacement
                for (int k=0;k<(samplingVector[j]*2);k++) {
                   // pick a random number between 0 and the adjustedPopulation size
                    if (Math.random()*adjustedPopulation < temp) {
                        // we've picked an allele of the type we're counting if the random number
                        // is less than the allele count
                        sampleFreqOverGenerations[i][j] = sampleFreqOverGenerations[i][j] + 1;
                        temp = temp - 1;
                    }
                    // remove a member of the population at each step
                    adjustedPopulation = adjustedPopulation - 1;
                }
                // divide by the sampleSize for the given locus to get the frequency
                sampleFreqOverGenerations[i][j] = sampleFreqOverGenerations[i][j]/(samplingVector[j]*2);
            }
        }
        return sampleFreqOverGenerations;
    }

    /**
     * Computes the ftemp metric for each locus using the formula var[p]/E[p](1-E[p]) - 1/2n
     * @param freqMatrix - Allele frequencies over all generations
     * @param samplingVector - A vector a specific sample size for each locus in every generation
     * @returns ftemp value for each locus
     */
    public double[] computeFTemp(double[][] freqMatrix, double[] samplingVector) {
        double fTemp[] = new double[freqMatrix[0].length];
        double mean, var;
        for (int i=0; i < fTemp.length; i++) {
            mean = findColMean(freqMatrix, i);
            var = findColVariance(freqMatrix, mean, i);
            fTemp[i] = var/(mean*(1-mean)) - (double)1/(2*samplingVector[i]);
        }
        return fTemp;
    }

    public double[] computeFTemp(double[][] freqMatrix, double[] samplingVector, int[] numValidGenerations,
            int[][] validGenerations ) {
        double fTemp[] = new double[freqMatrix[0].length];
        double mean, var;
        for (int i=0; i < fTemp.length; i++) {
            mean = findColMean(freqMatrix, i, numValidGenerations[i]);
            var = findColVariance(freqMatrix, mean, i, numValidGenerations[i], validGenerations[i]);
            fTemp[i] = var/(mean*(1-mean)) - (double)1/(2*samplingVector[i]);
        }
        return fTemp;
    }

    /**
     * Computes the heterozygosity for each locus using the formula 2p(1-p)
     * @param freqMatrix - Allele frequencies over all generations
     * @returns heterozygosity for each locus
     */
    public double[] computeHetroz(double[][] freqMatrix) {
        double[][] hetroz = new double[freqMatrix.length][freqMatrix[0].length];
        double[] meanHetroz = new double[freqMatrix[0].length];
        double maxHetroz=0;
        for (int i=0; i < freqMatrix.length; i++) {
            for (int j=0; j < freqMatrix[0].length; j++) {
                hetroz[i][j] = 2*freqMatrix[i][j]*(1-freqMatrix[i][j]);
            }
        }
        for (int j=0; j < freqMatrix[0].length; j++) {
                meanHetroz[j] = findColMean(hetroz,j);
        }
        return meanHetroz;
    }

    public double[] computeHetroz(double[][] freqMatrix, int[] validGenerations) {
        double[][] hetroz = new double[freqMatrix.length][freqMatrix[0].length];
        double[] meanHetroz = new double[freqMatrix[0].length];
        double maxHetroz=0;
        for (int i=0; i < freqMatrix.length; i++) {
            for (int j=0; j < freqMatrix[0].length; j++) {
                hetroz[i][j] = 2*freqMatrix[i][j]*(1-freqMatrix[i][j]);
            }
        }
        for (int j=0; j < freqMatrix[0].length; j++) {
                meanHetroz[j] = findColMean(hetroz,j,validGenerations[j]);
        }
        return meanHetroz;
    }

    /**
     * Finds the mean value of a given column in a matrix
     * @param matrix - Input matrix
     * @param column - The column number of which to compute the mean
     * @returns The mean value of the column of interest
     */
    private double findColMean(double[][] matrix, int column) {
        double mean=0;
        for (int i=0;i < matrix.length; i++) {
            mean = mean + matrix[i][column];
        }
        mean = mean/matrix.length;
        return mean;
    }

    private double findColMean(double[][] matrix, int column, int numValidGens) {
        double mean=0;
        for (int i=0;i < matrix.length; i++) {
            mean = mean + matrix[i][column];
        }
        mean = mean/numValidGens;
        return mean;
    }

    /**
     * Finds the population variance (NOT sample variance) of a given column in a matrix.
     * @param matrix - Input matrix
     * @param column - The column number of which to compute the variance
     * @returns The variance of the column of interest
     */
    private double findColVariance(double[][] matrix, double mean, int column) {
        double var=0;
        for (int i=0;i < matrix.length; i++) {
            var = var + Math.pow((matrix[i][column] - mean),2);
        }
        var = var/matrix.length;
        return var;
    }
    private double findColVariance(double[][] vector, double mean, int column, int numValidGens,
            int[] validGens) {
        double var=0;
        for (int i=0;i < vector.length; i++) {
            if (validGens[i] == 1) {
                var = var + Math.pow((vector[i][column] - mean),2);
            }
        }
        var = var/numValidGens;
        return var;
    }

     /**
     * Finds the maximum value of the vector
     * @param matrix - Input vector
     * @returns The maximum value in the vector
     */
    private int vectorMax(int[] matrix) {
        int max=0;
        for (int i=0;i < matrix.length; i++) {
           max = Math.max(max, matrix[i]);
        }
        return max;
    }
    private double vectorMax(double[] vector) {
        double max=0;
        for (int i=0;i < vector.length; i++) {
           max = Math.max(max, vector[i]);
        }
        return max;
    }

    private void writeFile(String fileName, double[] heterozygosity, double[] ftemp) {
        try {
            // Create file
            String line;
            String fline;
            FileWriter fstream = new FileWriter(fileName);
            BufferedWriter out = new BufferedWriter(fstream);
            for (int i=0; i< heterozygosity.length; i++) {
                if (heterozygosity[i] > 0) {
                    line = "%.4f %.4f%n";
                    fline = String.format(line, heterozygosity[i], ftemp[i]);
                    out.write(fline);
                }
            }
            //Close the output stream
            out.close();
        } catch (Exception e){//Catch exception if any
            System.err.println("Error: " + e.getMessage());
        }
    }

    /**
     * Displays a matrix
     * @param matrix - Matrix to display
     * @returns none
     */
    public void displayOutput(double[][] matrix) {
        for (int i=0; i < matrix.length; i++) {
            for (int j=0; j < matrix[0].length; j++) {
                System.out.format(matrix[i][j] +  " ");
            }
            System.out.println("");
        }
        System.out.println("");
    }

    /**
     * Displays a vector
     * @param vector - Vector to display
     * @returns none
     */
    public void displayOutput(double[] vector) {
        for (int i=0; i < vector.length; i++) {
                System.out.print(vector[i] +  " ");
        }
        System.out.println("");
        System.out.println("");
    }

    public void simulate(int numberOfLoci, int populationSize, int sampleSize, int[] generationsToSample, String outFileName) {
        double initialGeneration[];
        double freqOverGenerations[][];
        double sampleFreqOverGenerations[][];
        double fTemp[];
        double meanHetroz[];
        int numberOfGenerations;
		double[] samplingVector;

        try {
                if (numberOfLoci < 1 || numberOfLoci > 100000) {
                    System.out.println("Number of Loci must be between 1 and 100000");
                }
                if (populationSize < 20 || populationSize > 5000) {
                    System.out.println("WARNING: population_size is outside the expected range of " +
                            "20-5000");
                }
                if (sampleSize > populationSize) {
                    throw new IllegalArgumentException("sample_size must be less than population_size");
                }
                if (sampleSize < 10 || sampleSize > 200) {
                    System.out.println("WARNING: sample_size is outside the expected range of " +
                            "10-200");
                }
                if (vectorMax(generationsToSample) > 20) {
                    System.out.println("WARNING: generations_to_sample is greater than the expected " +
                            "maximum of 20");
                }

                System.out.println("");
                System.out.println("Running with values of:");
                System.out.println("number_of_loci = " + numberOfLoci);
                System.out.println("samples_size = " + sampleSize);
                System.out.println("population_size = " + populationSize);
                System.out.print("generations_to_sample = " + generationsToSample[0] + " ");
                for (int i=1; i<generationsToSample.length; i++) {
                    System.out.print(generationsToSample[i] + " ");
                }
                System.out.println("");
                System.out.println("");

                numberOfGenerations = vectorMax(generationsToSample) + 1;

				// create sampling vector
				samplingVector = createSamplingVector(numberOfLoci, sampleSize);

                // create the initial generation
                initialGeneration = createInitialGeneration(numberOfLoci);

                // simulate the population up to the max generation number we want to sample
                freqOverGenerations = simulateGenerations(initialGeneration, numberOfGenerations,
                        populationSize);

                // sample the population in the generations we're interested in
                sampleFreqOverGenerations = sampleGenerations(freqOverGenerations, populationSize,
                        generationsToSample, samplingVector);

                // compute the ftemp vector
                fTemp = computeFTemp(sampleFreqOverGenerations, samplingVector);

                // compute the heterozygosity vector
                meanHetroz = computeHetroz(sampleFreqOverGenerations);

                // display final output in desired form
                //    System.out.println("Locus number: heterozygosity, ftemp");
                //    System.out.println("----------------------------------");
                //   for (int i=0; i<numberOfLoci; i++) {
                //        System.out.format("Locus %3d:     %.4f, %.4f%n", (i+1), meanHetroz[i], fTemp[i]);
                //    }
                
                    writeFile(outFileName, meanHetroz, fTemp);

        } catch (Exception e){ // if there are any exceptions catch them
            System.err.println("ERROR: " + e.getMessage());
        }

    }

    /**
     *
     * @param args the command line arguments
     * @throws
     * @returns
     */
    public static void main(String[] args) {
        double initialGeneration[];
        double freqOverGenerations[][];
        double sampleFreqOverGenerations[][];
        double fTemp[];
        double meanHetroz[];
        int numberOfGenerations;
        double[] samplingVector;

        // set default values
        int numberOfLoci = 1000;
        int sampleSize = 30;
        int populationSize = 50; // must be larger than sampleSize
        int generationsToSample[];
        int debugLevel = 1;

        Simulator simulator = new Simulator();

        try {
            // use defaults if no input arguments are given
            if (args.length == 0) {
                System.out.println("usage: debug_level number_of_loci number_of_samples " +
                     "population_size first_generation_to_sample [other_generations_to_sample]");
            } else {
                // parse and do a sanity check of the inputs
                debugLevel = Integer.parseInt(args[0]);
                System.out.println("");
                numberOfLoci = Integer.parseInt(args[1]);
                if (numberOfLoci < 1 || numberOfLoci > 100000) {
                    System.out.println("Number of Loci must be between 1 and 100000");
                }
                populationSize = Integer.parseInt(args[3]);
                if (populationSize < 20 || populationSize > 5000) {
                    System.out.println("WARNING: population_size is outside the expected range of " +
                            "20-5000");
                }
                sampleSize = Integer.parseInt(args[2]);
                if (sampleSize > populationSize) {
                    throw new IllegalArgumentException("sample_size must be less than population_size");
                }
                if (sampleSize < 10 || sampleSize > 200) {
                    System.out.println("WARNING: sample_size is outside the expected range of " +
                            "10-200");
                }
                generationsToSample = new int[args.length-4];
                for (int i=0; i<args.length-4; i++) {
                    generationsToSample[i] = Integer.parseInt(args[i+4]);
                    if (generationsToSample[i] < 0) {
                        throw new IllegalArgumentException("generations_to_sample must be a " +
                                "non-negative integer value");
                    }
                    if (generationsToSample[0] != 0 || generationsToSample.length < 2) {
                        throw new IllegalArgumentException("generations_to_sample must start with 0 and " +
                                "have at least two generations to sample");
                    }
                }
                if (simulator.vectorMax(generationsToSample) > 20) {
                    System.out.println("WARNING: generations_to_sample is greater than the expected " +
                            "maximum of 20");
                }

                System.out.println("");
                System.out.println("Running with values of:");
                System.out.println("debug_level = " + args[0]);
                System.out.println("number_of_loci = " + args[1]);
                System.out.println("samples_size = " + args[2]);
                System.out.println("population_size = " + args[3]);
                System.out.print("generations_to_sample = " + generationsToSample[0] + " ");
                for (int i=0; i<args.length-5; i++) {
                    System.out.print(generationsToSample[i+1] + " ");
                }
                System.out.println("");
                System.out.println("");

                numberOfGenerations = simulator.vectorMax(generationsToSample) + 1;

  				// create sampling vector
				samplingVector = simulator.createSamplingVector(numberOfLoci, sampleSize);

                // create the initial generation
                initialGeneration = simulator.createInitialGeneration(numberOfLoci);

                // simulate the population up to the max generation number we want to sample
                freqOverGenerations = simulator.simulateGenerations(initialGeneration, numberOfGenerations,
                        populationSize);
                if (debugLevel > 0) {
                    System.out.println("Display freqOverGenerations");
                    simulator.displayOutput(freqOverGenerations);
                }

                // sample the population in the generations we're interested in
                sampleFreqOverGenerations = simulator.sampleGenerations(freqOverGenerations, populationSize, generationsToSample, samplingVector);
                if (debugLevel > 0) {
                    System.out.println("Display sampleFreqOverGenerations");
                    simulator.displayOutput(sampleFreqOverGenerations);
                }

                // compute the ftemp vector
                fTemp = simulator.computeFTemp(sampleFreqOverGenerations, samplingVector);
                if (debugLevel > 0) {
                    System.out.println("Display FTemp");
                    simulator.displayOutput(fTemp);
                }
                // compute the heterozygosity vector
                meanHetroz = simulator.computeHetroz(sampleFreqOverGenerations);
                if (debugLevel > 0) {
                    System.out.println("Display heterozygosity");
                    simulator.displayOutput(meanHetroz);
                }

                // display final output in desired form
                if (debugLevel > 0) {
                    System.out.println("Locus number: heterozygosity, ftemp");
                    System.out.println("----------------------------------");
                    for (int i=0; i<numberOfLoci; i++) {
                        System.out.format("Locus %3d:     %.4f, %.4f%n", (i+1), meanHetroz[i], fTemp[i]);
                    }
                }
                if (debugLevel == 0) {
                    for (int i=0; i<numberOfLoci; i++) {
                        if (meanHetroz[i] > 0) {
                            System.out.format("%.4f %.4f%n", meanHetroz[i], fTemp[i]);
                        }
                    }
                }
            }
        } catch (Exception e){ // if there are any exceptions catch them
            System.err.println("ERROR: " + e.getMessage());
        }
    }

}
