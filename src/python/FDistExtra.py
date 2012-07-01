from os import sep, system
from java.lang import System
import sys


def compileFile(directory, files, binName):
    system(
        'cd ' + directory + '; ' +
        'gcc -o ' + binName + ' -O ' + files + ' -lm')

def getExt():
    osName = System.getProperty('os.name').lower()

    if osName.find('mac os x')>-1:
        return '.mac'
    elif osName.find('windows')>-1:
        return '.exe'
    else:
        return ''

def compile(directory):
    osName = System.getProperty('os.name').lower()
    if osName.find('windows')>-1:
        return
    elif osName.find('mac os x')>-1:
        chmodLine = 'chmod a+x ' + (' ' + directory + sep).join([
            '', 'datacal.mac', 'pv.mac', 'fdist2.mac', 'cplot.mac',
            'Ddatacal.mac', 'pv2.mac', 'Dfdist.mac', 'cplot2.mac'
            ])
        #print chmodLine
        system(chmodLine)
    else:
        compileFile(directory, 'fdist2.c', 'fdist2')
        compileFile(directory, 'datacal.c', 'datacal')
        compileFile(directory, 'cplot.c as100.c as99.c', 'cplot')
        compileFile(directory, 'pv.c as100.c as99.c', 'pv')
        compileFile(directory, 'Dfdist.c', 'Dfdist')
        compileFile(directory, 'Ddatacal.c', 'Ddatacal')
        compileFile(directory, 'cplot2.c as100.c as99.c', 'cplot2')
        compileFile(directory, 'pv2.c as100.c as99.c', 'pv2')

