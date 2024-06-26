"""NgSpice connector to Python

This Script allows the users to call NgSpice through Python code and get the returned 
value back , it also allow some modification to be done to the NgSpice accepted file

This file can also be imported as a module and contains the following
functions:

    * TODO write this part
"""

import subprocess  # import the subproccess module used to call binaries of the system
import re
import json

import matplotlib.axes._axes
from matplotlib import pyplot as plt, colors as plc
import numpy as np
from numpy import linspace
from utils import *  # don't remove this


# pySpice module

# ANSII Colors 
class Colors:
    """ A class used to provide different ANSI color codes

    Attributes
    ----------
    Color : ANSI color code
        a color code used to color the text printed out to the terminal

    Note
    ----------
    END : ANSI color code 
        is used to clear the color of the text that comes afterward
    """

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


# constants
# here some constants are defined just to avoid writing them over and over
pySpice_name = f'{Colors.YELLOW}py{Colors.END}{Colors.BLUE}Spice{Colors.END}'


class PySpice:
    """ The main PySpice class which acts as a connector from NgSpice to Python

    Methods
    ----------
    read_txt(file_path)
        Gets a file as input and returns list containing it's lines
    runFile(filename,verbose=True)
        Calls the NgSpice with Pythons subprocess package ; saves the output and and exits the 
            NgSpice
    runFileAndPrintOutput(filename,verbose=True)
        Gets a file as input and prints the output to the terminal
    replacePyspiceNotations(input_filename,output_filename)
        TODO describe it
    pySpiceParser(pySpiceFilePath,outFile=None)
        TODO describe it
    regexReplaceAssign(theMatch)
        TODO describe it
    regexReplaceParam(theMatch)
        TODO describe it
    regexReplaceFileName(theMatch)
        TODO describe it
    parseNgSpiceFile(ngSpiceFilePath)
        TODO describe it
    setVariables()
        TODO describe it
    """

    def __init__(self):
        self.variables = {}
        self.acDcCount = 0
        print("""
        """ + pySpice_name + """
        This program uses PATH variable to find 'ngspice' program
        Please include 'ngspice' into PATH if you are using MS-Windows
        """)
        # input()

    @staticmethod
    def read_txt(file_path):
        """ Gets a file as input and returns list containing it's lines

        Parameters
        ----------
        file_path : str
            the path of the file that is going to be read - if its in the same directory 
            and only the filename was given then the file with matching name in the working directory
            will be opened

        Returns
        ----------
        List
            a list containing the lines of the given file 
        """

        file = open(file_path, "r")
        lines = [x for x in file.readlines()]
        file.close()
        return lines

    def runFile(self, filename: str, verbose=True):
        """ Calls the NgSpice with Pythons subprocess package ; saves the output and and exits the 
            NgSpice 

        Parameters
        ----------
        filename
            Takes the filename of the input file which sould be passed to NgSpice
        verbose
            If set to true will print additional messages about the process

        Returns
        ----------
        List
            A list containing the lines of the given file - the list is returned by using the method read_txt

        Note
        ----------
        NgSpice doesn't exit automatically or keeps the shell open which leads to PySpice wait for it to finish,
          the file ngSpiceExitter acts as an Stdin and helps quitting the NgSpice so that PySpice can continue!
        """

        # TODO implemet different output file
        with open('ngSpiceExitter', "w+") as f:
            subprocess.run(['ngspice', f'{filename}', '-o', f'{filename[:-4]}Output.txt', '-a'],
                           close_fds=True,
                           stdin=f)
        if verbose is True:
            print(
                f'The output is saved in {filename[:-4]}Output.txt')
        return self.read_txt(f'{filename[:-4]}Output.txt')

    def runFileAndPrintOutput(self, filename: str, verbose=True):
        """ Gets a file as input and prints the output to the terminal

        Parameters
        ----------
        filename
            Takes the filename of the input file which sould be passed to NgSpice
        verbose
            If set to true will print additional messages about the process
        """

        for i in self.runFile(filename, verbose):
            print(i)

    def replacePyspiceNotations(self, input_filename, output_filename):
        """
        Replaces all occurrences of '{{function a(x, y)}}' in the input file with the return value of function_a(x, y).

        Args:
            input_filename (str): The name of the input file.
            output_filename (str): The name of the output file (optional).

        Returns:
            None
        """

        def regEx_replace_func(theMatch):
            for key in self.variables:
                # TODO ASK what does this code does ? ig it replaces sth
                exec(f"{key} = '{self.variables[key]}'")
            return str(eval(theMatch.group(1)))

        with open(input_filename, 'r') as input_file:
            text = input_file.read()

        replaced_text = re.sub(r"\{\{pyspice ((?:(?!\{\{pyspice).)*)}}", regEx_replace_func, str(text))

        if output_filename:
            with open(output_filename, 'w') as output_file:
                output_file.write(replaced_text)
        # TODO ASK why the else acts like it prints some sort of a success message ?
        else:
            print("Replaced content:\n")
            print(replaced_text)

    def pySpiceParser(self, pySpiceFilePath: str, pySpiceVarsFilePath: str, outFile=None):
        # TODO ASK what is self.variable and what this line below does ?
        if pySpiceFilePath[-7:] == 'pyspice':
            self.getVariables(pySpiceVarsFilePath)
            if outFile is not None:
                self.variables["outFileRawName"] = outFile
            self.replacePyspiceNotations(pySpiceFilePath, pySpiceFilePath[:-8] + '.net')
        else:
            print('File format is not supported!')

    def getVariables(self, filePath):
        with open(filePath, 'r') as file:
            variables = json.load(file)
            for var in variables:
                if var not in self.variables:
                    self.variables[var] = variables[var]

    def regexReplaceAssign(self, theMatch):
        # TODO ASK ok ik what it does but common it has no docs
        self.variables[theMatch.group(1)] = theMatch.group(4)
        return (theMatch.group(1) + theMatch.group(2) + "=" + theMatch.group(3) + "{{pyspice " + theMatch.group(1) +
                "}}" + theMatch.group(5))

    def regexReplaceParam(self, theMatch):
        # TODO ASK what this regex is for
        return ".param" + theMatch.group(1) + re.sub(r"([\w\d]*)( *)=( *)([.\de]*)(\w*)", self.regexReplaceAssign,
                                                     theMatch.group(2))

    def regexReplaceFileName(self, theMatch):
        rawFileName = theMatch.group(1)[:theMatch.group(1).find('.')]
        fileExt = theMatch.group(1)[theMatch.group(1).find('.'):]
        params = theMatch.group(2)
        self.variables["outFileRawName"] = rawFileName
        print(self.variables["outFileRawName"])
        self.variables["writeParams"] = params
        print(self.variables["writeParams"])
        return "wrdata " + "{{pyspice outFileRawName}}" + fileExt + " {{pyspice writeParams}}\n"

    def regexReplaceFileNameEchoPrint(self, theMatch):
        echoOrPrint = theMatch.group(1)
        params = theMatch.group(2)
        rawFileName = theMatch.group(3)[:theMatch.group(3).find('.')]
        fileExt = theMatch.group(3)[theMatch.group(3).find('.'):]
        self.variables["outFileRawName"] = rawFileName
        print(self.variables["outFileRawName"])
        self.variables["writeParams"] = params
        print(self.variables["writeParams"])
        return echoOrPrint + " {{pyspice writeParams}}>> " + "{{pyspice outFileRawName}}" + fileExt + "\n"

    def regexReplaceTran(self, theMatch):
        self.variables["tran"] = theMatch.group(1)
        return ".tran {{pyspice tran}}"

    def regexReplaceSet(self, theMatch):
        self.variables["set"] = theMatch.group(3)
        return f".control {theMatch.group(1)}set{theMatch.group(2)}" + "{{pyspice set}}"

    def regexReplaceAcDc(self, theMatch):
        varName = f"ac_dc{self.acDcCount}"
        self.acDcCount += 1
        self.variables[varName] = theMatch.group(2)
        return theMatch.group(1) + "{{pyspice " + varName + " }}" + theMatch.group(3)

    def parseNgSpiceFile(self, ngSpiceFilePath: str):
        fileContent = ""
        with open(ngSpiceFilePath) as file:
            for line in file.readlines():
                fileContent += line

        fileContent = re.sub(r"\.param( *)(.*)", self.regexReplaceParam, fileContent)
        fileContent = re.sub(r"wrdata\s+([.\w]*)\s+([\w()\s]*)(\n|$)", self.regexReplaceFileName, fileContent)
        fileContent = re.sub(r"(echo|print) ([\s\w()].*)>>\s*([.\w]*)\s*(\n|$)", self.regexReplaceFileNameEchoPrint,
                             fileContent)
        fileContent = re.sub(r"\.tran ([.\w\s{}*]*)", self.regexReplaceTran, fileContent)
        fileContent = re.sub(r"\.control(\s*)set(\s*)([\w_]*)", self.regexReplaceSet, fileContent)
        fileContent = re.sub(r"(\s|^)(ac|dc)(\s|$)", self.regexReplaceAcDc, fileContent)

        with open(ngSpiceFilePath[:ngSpiceFilePath.rfind('.')] + ".pyspice", "w+") as file:
            file.write(fileContent)

        with open(ngSpiceFilePath[:ngSpiceFilePath.rfind('.')] + ".pyspice.vars", "w+") as file:
            json.dump(self.variables, file)

    def setVariables(self, **newVariables):
        for var in newVariables:
            self.variables[var] = newVariables[var]

    def convertAllVoltagesTo(self, value="ac"):
        for var in self.variables:
            if "ac_dc" in var:
                self.variables[var] = value

    def getWriteParams(self):
        return list(filter(lambda x: x.strip() != "", self.variables["writeParams"].split(" ")))

    def runFileAndShowDataAsPlot(self, filePath: str, params: list | None = None, width=20, height=20, dpi=100,
                                 allInOne=False):
        if params is None:
            params = self.getWriteParams()
        outFile = self.variables["outFileRawName"] + ".txt"
        self.runFileAndPrintOutput(filePath)
        with open(outFile, "r") as file:
            values = {}
            names = ['time', *params]
            for line in file.readlines():
                value = np.array(
                    list(map(lambda x: float(x), filter(lambda x: x.strip() != "", line.strip().split(" ")))))
                for j in range(len(names)):
                    if names[j] not in values:
                        values[names[j]] = []
                    values[names[j]].append(value[j])

            matplotColors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
            if allInOne:
                plt.figure(figsize=(width, height), dpi=dpi)
                for i in range(1, len(names)):
                    plt.plot(values[names[0]], values[names[i]], matplotColors[i % len(matplotColors)],
                             label=names[i])
                plt.legend()
            else:
                fig, axs = plt.subplots(len(names) - 1)
                if len(names) - 1 == 1:
                    axs = [axs]
                fig.suptitle('PySpice')
                fig.set_figwidth(width)
                fig.set_figheight(height)
                fig.set_dpi(dpi)
                for i in range(1, len(names)):
                    axs[i - 1].plot(values[names[0]], values[names[i]], matplotColors[i % len(matplotColors)],
                                    label=names[i])
                    axs[i - 1].legend()

            plt.xlabel(names[0])
            plt.show()


def main():
    pySpice = PySpice()
    pySpice.parseNgSpiceFile('../testFolder/Ex2_4driver_2CoupledLine.net')
    for i in range(1):
        pySpice.setVariables(length=130 + i // 5, supply1=1.2 + i / 10, outFileRawName=f"my_out")
        pySpice.pySpiceParser('../testFolder/Ex2_4driver_2CoupledLine.pyspice',
                              '../testFolder/Ex2_4driver_2CoupledLine.pyspice.vars', outFile=None)
        pySpice.runFileAndShowDataAsPlot('../testFolder/Ex2_4driver_2CoupledLine.net', allInOne=True)


if __name__ == "__main__":
    main()
