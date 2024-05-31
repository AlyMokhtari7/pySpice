import subprocess  # import the subproccess module used to call binaries of the system
import re
import json
from utils import *  # don't remove this


# pySpice module

# ANSII Colors 
class Colors:
    """ ANSI color codes """
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
pySpice_name = f'{Colors.YELLOW}py{Colors.END}{Colors.BLUE}Spice{Colors.END}'


class PySpice:
    def __init__(self):
        self.variables = {}

    @staticmethod
    def read_txt(file_name):
        file = open(file_name, "r")
        lines = [x for x in file.readlines()]
        file.close()
        return lines

    def runFile(self, filename: str, verbose=True):
        """
            takes the filename and returns a list that contains the lines of the output
            also saves the output file
            if Verbose is set to True it will print more details
        """
        print(
            f"{pySpice_name} is about to run the ngSpice , after viewing the desired logs type {Colors.RED}Exit{Colors.END}\n {Colors.LIGHT_WHITE} ! pySpice will take care of the rest !{Colors.END}")
        with open('ngSpiceExitter', "w+") as f:
            process = subprocess.run(['ngspice', f'{filename}', '-o', f'{filename[:-4]}Output.txt', '-a'],
                                     close_fds=True,
                                     stdin=f)
        # process.stdin.write('quit')
        if verbose is True:
            print(
                f'TNX, now {pySpice_name} takes care of the rest \n {Colors.LIGHT_WHITE}FYI{Colors.END} the output is saved in {filename[:-4]}Output.txt')
        return self.read_txt(f'{filename[:-4]}Output.txt')

    def runFileAndPrintOutput(self, filename: str, verbose=True):
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
                exec(f"{key} = '{self.variables[key]}'")
            return str(eval(theMatch.group(1)))

        with open(input_filename, 'r') as input_file:
            text = input_file.read()

        replaced_text = re.sub(r"\{\{pyspice ((?:(?!\{\{pyspice).)*)}}", regEx_replace_func, str(text))

        if output_filename:
            with open(output_filename, 'w') as output_file:
                output_file.write(replaced_text)
        else:
            print("Replaced content:\n")
            print(replaced_text)

    def pySpiceParser(self, pySpiceFilePath: str, pySpiceVarsFilePath: str, outFile=None):
        if pySpiceFilePath[-7:] == 'pyspice':
            self.getVariables(pySpiceVarsFilePath)
            self.variables["pySpice__outFileName"] = outFile if outFile is not None else ""
            self.replacePyspiceNotations(pySpiceFilePath, pySpiceFilePath[:-8] + '.net')
        else:
            print('File format is not supported!')

    def getVariables(self, filePath):
        with open(filePath, 'r') as file:
            self.variables = json.load(file)

    def regexReplaceAssign(self, theMatch):
        self.variables[theMatch.group(1)] = theMatch.group(4)
        return (theMatch.group(1) + theMatch.group(2) + "=" + theMatch.group(3) + "{{pyspice " + theMatch.group(1) +
                "}}" + theMatch.group(5))

    def regexReplaceParam(self, theMatch):
        return ".param" + theMatch.group(1) + re.sub(r"([\w\d]*)( *)=( *)([.\de]*)(\w*)", self.regexReplaceAssign,
                                                     theMatch.group(2))

    def regexReplaceFileName(self, theMatch):
        rawFileName = theMatch.group(1)[:theMatch.group(1).find('.')]
        fileExt = theMatch.group(1)[theMatch.group(1).find('.'):]
        self.variables["pySpice__outFileRawName"] = theMatch.group(1)
        return "wrdata " + rawFileName + "{{pyspice pySpice__outFileName}}" + fileExt

    def parseNgSpiceFile(self, ngSpiceFilePath: str):
        content = ""
        with open(ngSpiceFilePath) as file:
            for line in file.readlines():
                content += line

        fileContent = re.sub(r"\.param( *)(.*)", self.regexReplaceParam, content)
        fileContent = re.sub(r"wrdata ([.\w]*)", self.regexReplaceFileName, fileContent)

        with open(ngSpiceFilePath[:ngSpiceFilePath.rfind('.')] + ".pyspice", "w+") as file:
            file.write(fileContent)

        with open(ngSpiceFilePath[:ngSpiceFilePath.rfind('.')] + ".pyspice.vars", "w+") as file:
            json.dump(self.variables, file)

    def setVariables(self, **newVariables):
        for var in newVariables:
            self.variables[var] = newVariables[var]


def main():
    pySpice = PySpice()
    pySpice.parseNgSpiceFile('Ex2_4driver_2CoupledLine.net')
    # pySpice.setVariables(length=5)
    pySpice.pySpiceParser('Ex2_4driver_2CoupledLine.pyspice', 'Ex2_4driver_2CoupledLine.pyspice.vars', outFile=None)
    pySpice.runFileAndPrintOutput('Ex2_4driver_2CoupledLine.net')


if __name__ == "__main__":
    main()
