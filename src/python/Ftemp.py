import os
import shutil
import thread
import time

from java.lang import String
import jarray

from Bio.PopGen.Async import Local

from temporal import Simulator

class FtempAsync():
    """Asynchronous ftemp execution.
    """

    def run_job(self, parameters, input_files):
        """Runs ftemp asynchronously.

           Gets typical ftemp parameters from a dictionary and
           makes a "normal" call. This is run, normally, inside
           a separate thread.
        """
        npops = parameters['npops']
        ne = parameters['ne']
        sample_size = parameters['sample_size']
        gens_sample = parameters['gens_sample']
        num_sims = parameters.get('num_sims', 20000)
        data_dir = parameters.get('data_dir', '.')
        outFileName = data_dir + os.sep + 'out.dat'
        ne = self.run_ftemp(npops, ne, sample_size, gens_sample,
            num_sims, outFileName)
        output_files = {}
        output_files['out.dat'] = open(outFileName, 'r')
        return ne, output_files

    def run_ftemp(self, npops, ne, sample_size, gens_sample,
            num_sims, outFileName):
        print ["0", str(num_sims), str(sample_size),
                str(ne), ] + map(lambda x:str(x), gens_sample)
        sim = Simulator()
        sim.simulate(num_sims, int(ne), int(sample_size),
                gens_sample, outFileName)
        return 0.5 #ignore


class Split(object):
    def __init__(self, report_fun = None,
        num_thr = 2, split_size = 1000, ftemp_dir = ''):
        self.async = Local.Local(num_thr)
        self.async.hooks['ftemp'] = FtempAsync()
        self.report_fun = report_fun
        self.split_size = split_size

    def monitor(self):
        while(True):
            time.sleep(1)
            self.async.access_ds.acquire()
            keys = self.async.done.keys()[:]
            self.async.access_ds.release()
            for done in keys:
                self.async.access_ds.acquire()
                ne, files = self.async.done[done]
                del self.async.done[done]
                out_dat = files['out.dat']
                f = open(self.data_dir + os.sep + 'out.dat','a')
                f.writelines(out_dat.readlines())
                f.close()
                out_dat.close()
                self.async.access_ds.release()
                for file in os.listdir(self.parts[done]):
                    os.remove (self.parts[done] + os.sep + file)
                os.rmdir(self.parts[done])
                #print fst, out_dat
                if self.report_fun:
                    self.report_fun(ne)
            self.async.access_ds.acquire()
            if len(self.async.waiting) == 0 and len(self.async.running) == 0 \
               and len(self.async.done) == 0:
                break
            self.async.access_ds.release()
            #print 'R', self.async.running
            #print 'W', self.async.waiting
            #print 'R', self.async.running

    def acquire(self):
        self.async.access_ds.acquire()

    def release(self):
        self.async.access_ds.release()

    #You can only run a ftemp case at a time
    def run_ftemp(self, npops, ne, sample_size, gens_sample,
            num_sims = 20000, data_dir='.'):
        num_parts = num_sims/self.split_size
        self.parts = {}
        self.data_dir = data_dir
        for directory in range(num_parts):
           full_path = data_dir + os.sep + str(directory)
           try:
               os.mkdir(full_path)
           except OSError:
               pass #Its ok, if it is already there
           if "ss_file" in os.listdir(data_dir):
               shutil.copy(data_dir + os.sep + "ss_file", full_path)
           id = self.async.run_program('ftemp', {
               'npops'       : npops,
               'ne'          : ne,
               'sample_size' : sample_size,
               'gens_sample' : gens_sample,
               'num_sims'    : self.split_size,
               'data_dir'    : full_path,
           }, {})
           self.parts[id] = full_path
        thread.start_new_thread(self.monitor, ())

