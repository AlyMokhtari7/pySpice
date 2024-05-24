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
PYSPICE_CODE_REG_EX = '\\{\\{pyspice (.*)}}'

# import the subproccess module used to call binaries of the system
import subprocess
import re
from utils import *


def read_txt(file_name):
    file = open(file_name, "r")
    lines = [x for x in file.readlines()]
    file.close()
    return lines


def runFile(filename: str, verbose=True):
    """
        takes the filename and returns a list that contains the lines of the output
        also saves the output file
        if Verbose is set to True it will print more details
    """
    print(
        f"{pySpice_name} is about to run the ngSpice , after viewing the desired logs type {Colors.RED}Exit{Colors.END}\n {Colors.LIGHT_WHITE} ! pySpice will take care of the rest !{Colors.END}")
    with open('ngSpiceExitter', "w+") as f:
        process = subprocess.run(['ngspice', f'{filename}', '-o', f'{filename[:-4]}Output.txt', '-a'], close_fds=True,
                                 stdin=f)
    # process.stdin.write('quit')
    if verbose is True:
        print(
            f'TNX, now {pySpice_name} takes care of the rest \n {Colors.LIGHT_WHITE}FYI{Colors.END} the output is saved in {filename[:-4]}Output.txt')
    return read_txt(f'{filename[:-4]}Output.txt')


def runFileAndPrintOutput(filename: str, verbose=True):
    for i in runFile(filename, verbose):
        print(i)


def replace_function_calls(input_filename, output_filename, **parameters):
    """
    Replaces all occurrences of '{{function a(x, y)}}' in the input file with the return value of function_a(x, y).

    Args:
        input_filename (str): The name of the input file.
        output_filename (str): The name of the output file (optional).

    Returns:
        None
    """

    def regEx_replace_func(theMatch):
        for key in parameters:
            exec(f"{key} = {parameters[key]}")
        return str(eval(theMatch.group(1)))

    with open(input_filename, 'r') as input_file:
        text = input_file.read()

    replaced_text = re.sub(PYSPICE_CODE_REG_EX, regEx_replace_func, str(text))

    if output_filename:
        with open(output_filename, 'w') as output_file:
            output_file.write(replaced_text)
    else:
        print("Replaced content:\n")
        print(replaced_text)


def pySpiceParser(pySpiceFilePath: str, **parameters):
    if pySpiceFilePath[-7:] == 'pyspice':
        replace_function_calls(pySpiceFilePath, pySpiceFilePath[:-8] + '.net', **parameters)
    else:
        print('File format is not supported!')


pySpiceParser('Ex2_4driver_2CoupledLine.pyspice', n=3)
# runFileAndPrintOutput('Ex2_4driver_2CoupledLine.net')
