import java.io.*;
import java.util.Properties;
import java.util.zip.*;
import org.python.core.*;
import org.python.util.*;

public class Boot {
  public String directory;

  public void getFDist(String file) {
    ZipInputStream zin = new ZipInputStream(this.getClass().getClassLoader().getResourceAsStream(file));
    try {
        ZipEntry zipe;
        while ( (zipe = zin.getNextEntry()) != null) {
            //System.out.println("fil " + zipe.getName());
            // Open the output file
            String outFilename = directory + File.separator + zipe.getName();
            OutputStream out = new FileOutputStream(outFilename);
    
            // Transfer bytes from the ZIP file to the output file
            byte[] buf = new byte[1024];
            int len;
            while ((len = zin.read(buf)) > 0) {
                out.write(buf, 0, len);
            }

            out.close();
        }
        zin.close();
    }
    catch (IOException ioe) {
    }
  }

  public void getPy(String file) {
    ZipInputStream zin = new ZipInputStream(this.getClass().getClassLoader().getResourceAsStream(file));
    try {
        // Get the first entry
        ZipEntry zipe;
        while ( (zipe = zin.getNextEntry()) != null) {
    
            if (zipe.isDirectory()) {
                File dirFile = new File(directory + File.separator + zipe.getName());
                dirFile.mkdirs();
                //System.out.println("dir " + zipe.getName());
            }
            else {
                //System.out.println("fil " + zipe.getName());
                // Open the output file
                String outFilename = directory + File.separator + zipe.getName();
                OutputStream out = new FileOutputStream(outFilename);
    
                // Transfer bytes from the ZIP file to the output file
                byte[] buf = new byte[1024];
                int len;
                while ((len = zin.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
    
                out.close();
            }
        }
        zin.close();
    }
    catch (IOException ioe) {
    }
  }

  public void go(boolean isDominant, boolean isTemporal) {
    String os = System.getProperty("os.name");
    String home = System.getProperty("user.home");
    String sep = System.getProperty("file.separator");
    System.out.println(os + " " + home + " " + sep);

    if (isTemporal) {
        directory = home + sep + ".lositemp";
    }
    else if (isDominant) {
        directory = home + sep + ".mcheza";
    }
    else {
        directory = home + sep + ".lositan";
    }
    
    (new File(directory)).mkdir();

    getPy("py.zip");
    /*
    if (os.equals("lemac")) {
        getFDist("fdist2Mac.zip");
    }
    else { //*nix or windoze
        getFDist("allfdist.zip");
    }
    */
    getFDist("allfdist.zip");

    Properties props = new Properties();
    props.setProperty("python.path", directory);
    String[] args;
    if (isTemporal) {
        args = new String[] {"fromJava", "temp"};
    }
    else if (isDominant) {
        args = new String[] {"fromJava", "dom"};
    }
    else {
        args = new String[] {"fromJava"};
    }
    PythonInterpreter.initialize(System.getProperties(),
            props, args);
    PythonInterpreter py = new PythonInterpreter();
    py.execfile(directory + File.separator + "Main.py");


  }

  public static void main(String[] args) {
    Boot b= new Boot();
    if (args.length>0) {
        if (args[0].equals("temp")) {
            b.go(false, true);
        }
        else {
            b.go(true, false);
        }
    }
    else {
        b.go(false, false);
    }

  }
}
