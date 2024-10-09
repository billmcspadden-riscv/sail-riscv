#! /usr/bin/env python3
# vim: set tabstop=4 shiftwidth=4 expandtab set textwidth=79
# ===========================================================================79
# Filename:    run_tests.py
#
# Description: Converting run_tests.sh to python
#
#               Based on run_test.sh
#
#               Same as run_test.sh:
#                   1. output into .xml file is the same
#                   2. colorization of output
#
#               Differences with run_test.sh
#                   1. Does not depend upon .elf file extension for filetype.
#                       Uses the unix 'file' command to get filetype
#                   2. Added usage function
#                   3. Added run switches (which didn't exist in run_test.sh)
#                       See the print_usage() function for a descriptionm of
#                       the supported switches.
#                   4. Default search directories, rather than just one.
#                   5. Removed use of $RISCV env var.
#                   6. requires python3
#                   7. Added support to ignore tests via the --test_ignore_pyfile
#                       switch
#                   8. Added support to supply switches to the riscv_sim command
#                       via the --test_switch_pyfile.
#
# Author(s):   Bill McSpadden (bill@riscv.org)
#
# History:     See revision control log
# ===========================================================================79

# ===========================================================================79
# Necessary imports for this script:
import os               # needed for os command interactions
import glob             # needed for file list gathering useing wildcards
import re               # regular expression
import sys              # needed for command line arguments
import signal           # needed for signal handling (cntl-C especially)
import getopt           # needed for command line arguments
import collections      # needed for dequeues
import subprocess       # needed for subprocesses where stdout is needed
from pathlib import Path
from inspect import currentframe, getframeinfo
from abc import ABC, abstractmethod
from copy import deepcopy
# Necessary imports for this script
# ===========================================================================79


# ===========================================================================79
# General data for use in this script.
# ===========================================================================79
# Data structure for sim command line arguments
# TODO:  make the key a regex
sim_test_command_line_switch_dict = { }
sim_test_command_line_switch = { }
my_ignore_test_tuple = []

# Allowed command line options
opts, args = getopt.getopt (
    sys.argv[1:],
    "dhuo:",
    [
    "help",
    "usage",
    "outfile=",
    "test_dir=",
    "32bit=",
    "64bit=",
    "c_sim=",
    "sailcov=",
    "clean_build=",
    "test_dir=",
    "test_switch_pyfile=",
    "test_ignore_pyfile=",
    "debug"
    ]
    )

# Variables to be overridden with command line switches
xml_outfile         = "./tests.xml"
run_32bit_tests     = True
run_64bit_tests     = True
run_csim            = True
sailcov             = False
clean_build         = True
test_dir_list       = [ "isa", "riscv-tests" ]
sail_riscv_rootdir  = 'SAIL_RISCV_ROOTDIR'
test_switch_pyfile  = ''
test_ignore_pyfile  = ''
debug               = False

# Variables for tracking test status and test output
RED     = '\033[0;91m'
GREEN   = '\033[0;92m'
YELLOW  = '\033[0;93m'
NC      = '\033[0m'
test_pass   = 0
test_fail   = 0
all_pass    = 0
all_fail    = 0
SUITE_XML   = ""
SUITES_XML  = ""
# ===========================================================================79

# ===========================================================================79
# Function prototypes:
# ====================================
#  Print Levels:
#   print()         Normal python print function.  Goes to stdout
#   debug_print()   Print debug information. Goes to stdout.
#   error_print()   Print error message.  Goes to stdout.  Generally most errors should be fatal errors
#   fatal_print()   Print fatal error message. Exit with status 1.  Generally most errors should be fatal errors. Goes to stdout.
#   TRACE()         For bringup debug only.  TRACE() instances should be removed.

def debug_print (text = "") :
    if debug :
        cf = currentframe()
        of = cf.f_back
        fi = getframeinfo(of)
        filename = os.path.basename(fi.filename)
        print("debug: file: " + filename + " line: " + str(of.f_lineno) + " : " + text)
    return

def error_print (text = "") :
    cf = currentframe()
    of = cf.f_back
    fi = getframeinfo(of)
    filename = os.path.basename(fi.filename)
    print("error: file: " + filename + " line: " + str(of.f_lineno) + " : " + text)
    return

def fatal_print (text = "") :
    cf = currentframe()
    of = cf.f_back
    fi = getframeinfo(of)
    filename = os.path.basename(fi.filename)
    print("fatal error: file: " + filename + " line: " + str(of.f_lineno) + " : " + text)
    sys.exit(1)
    return  # never taken

def TRACE(text = "") :
    cf = currentframe()
    of = cf.f_back
    fi = getframeinfo(of)
    filename = os.path.basename(fi.filename)
    print("TRACE: file: " + filename + " line: " + str(of.f_lineno) + " : " + text)
    return
#  Print Levels:
# ====================================

# ====================================
# Subprocess support functions
def subproc(cmd) :
    try:
        debug_print("subproc: cmd: " + cmd)
        subprocess.check_call(cmd, shell = True)
    except KeyboardInterrupt as e:
        debug_print("interrupted: subproc: cmd: " + cmd)
        sys.exit(1)
    except:
        debug_print("subproc: cmd: " + cmd)
        return 1
    else:
        return 0
       
# Subprocess support functions
# ====================================

# ====================================
# Support for command line options
def print_usage(invocation) :
    print(invocation + " usage: " + invocation + " [<options>]")
    print("    Typically, invoke this script in the directory above where the elf-file tests live.")
    print("    The script looks into test_dir, finds all of the elf files and then runs the simulator")
    print("    with each elf file.")
    print("")
    print("    Output logs are put into [dir]/<testname>.cout (for C sim).")
    print("")
    print("    Some tests require specific command line switches to properly run.  To add these")
    print("    command line switches,  you must use the '--test_switch_pyfile=<file>' switch.")
    print("")
    print("  options:")
    print("    -h --help -u -usage             print out help/usage message")
    print("    -o/--outfile=<file>             name of xml tests results file to be generated. default: ./tests.xml ")
    print("    --32bit=[yes|y|no|n]            run 32-bit tests. default: yes")
    print("    --64bit=[yes|y|no|n]            run 64-bit tests. default: yes")
    print("    --c_sim=[yes|y|no|n]            run the C simulator. default: yes")
    print("    --sailcov=[yes|y|no|n]          compile and run to get Sail model coverage. default: no.  ")
    print("                                    NOTE: sets 'clean_build' to yes. Coverage is gathered seperately for ")
    print("                                    32 and 64 bit models")
    print("    --clean_build=[yes|y|no|n]      do a 'make clean' before running 32/64/c_sim set of tests. default: yes")
    print("    --test_dir=<dir>                directory where test elf files live. default:  ./isa ./riscv-tests")
    print("    --test_switch_pyfile=<file.py>  a python fragment file that allows the user to pass in command line switches to the")
    print("                                    riscv_sim command on a per-test basis.  The format of the file should be:")
    print("                                    sim_test_command_line_switch_dict = {")
    print("                                        \"<testname_A>\"          : \"<switch>  [<switch> ...] \",")
    print("                                        \"<testname_B>\"          : \"<switch>  [<switch> ...] \",")
    print("                                    }")
    print("    --test_ignore_pyfile=<file.py>  <file> contains a tuple (immutable list) of tests to be ignored.  The format of the file should be:")
    print("                                    ignore_test_tuple = [")
    print("                                        \"<testname_A>\",")
    print("                                        \"<testname_B>\",")
    print("                                    ]")
    print("    -d,--debug                      turn on debug output")

def process_command_line_args(opts) :
    global xml_outfile
    global run_32bit_tests
    global run_32bit_tests
    global run_64bit_tests
    global run_csim
    global sailcov
    global clean_build
    global test_dir_list
    global test_switch_pyfile
    global test_ignore_pyfile
    global debug

    for opt, arg in opts :
        if opt in ('-h', '--help', '-u', '--usage') :
            print_usage(sys.argv[0])
            sys.exit(0)
        elif opt in ('-o', "--outfile") :
            xml_outfile = arg
        elif opt in ('--32bit') :
            if arg in ('yes', 'y') :
                run_32bit_tests = True
            elif arg in ('no', 'n') :
                run_32bit_tests = False
            else :
                fatal_print("invalid argument to '--32bit' switch: " + arg)
        elif opt in ('--64bit') :
            if arg in ('yes', 'y') :
                run_64bit_tests = True
            elif arg in ('no', 'n') :
                run_64bit_tests = False
            else :
                fatal_print("invalid argument to '--64bit' switch: " + arg)
        elif opt in ('--c_sim') :
            if arg in ('yes', 'y') :
                run_csim = True
            elif arg in ('no', 'n') :
                run_csim = False
            else :
                fatal_print("invalid argument to '--run_csim' switch: " + arg)
        elif opt in ('--sailcov') :
            if arg in ('yes', 'y') :
                sailcov = True
            elif arg in ('no', 'n') :
                sailcov = False
            else :
                fatal_print("invalid argument to '--sailcov' switch: " + arg)
                sys.exit(1)
        elif opt in ('--clean_build') :
            if arg in ('yes', 'y') :
                clean_build = True
            elif arg in ('no', 'n') :
                clean_build = False
            else :
                fatal_print("invalid argument to '--clean_build' switch: " + arg)
                sys.exit(1)
        elif opt in ('--test_dir') :
            if not os.path.exists(arg) :
                fatal_print("test_dir path, '" + arg + "', does not exist")
            test_dir_list = []
            test_dir_list.append(arg)
        elif opt in ('--test_switch_pyfile') :
            if not os.path.isfile(arg) :
                fatal_print("--test_switch_pyfile argument error. file, '" + arg + "', does not exist")
            test_switch_pyfile = arg
        elif opt in ('--test_ignore_pyfile') :
            if not os.path.isfile(arg) :
                fatal_print("--test_ignore_pyfile argument error. file, '" + arg + "', does not exist")
                sys.exit(1)
            test_ignore_pyfile = arg
        elif opt in ('-d', '--debug') :
            debug = True
        else :
            fatal_print("unexpected command line option: " + opt)

# print_optional_settings AFTER the inmplicit overrides have happened
def print_optional_settings() :
    global xml_outfile
    global run_32bit_tests
    global run_32bit_tests
    global run_64bit_tests
    global run_csim
    global sailcov
    global clean_build
    global test_dir_list
    global test_switch_pyfile
    global test_ignore_pyfile
    global debug

    print('================================================================')
    print('Run time variable settings: ')
    print('    {:32}'.format('debug: ')                         + str(debug))
    print('    {:32}'.format('outfile: ')                       +     xml_outfile)
    print('    {:32}'.format('run_32bit_tests: ')               + str(run_32bit_tests))
    print('    {:32}'.format('run_64bit_tests: ')               + str(run_64bit_tests))
    print('    {:32}'.format('run_csim: ')                      + str(run_csim))
    print('    {:32}'.format('sailcov: ')                       + str(sailcov))
    print('    {:32}'.format('clean_build: ')                   + str(clean_build))
    print('    {:32}'.format('test_dir_list: ')                 + str(test_dir_list))
    print('    {:32}'.format('test_ignore_pyfile: ')            +     test_ignore_pyfile)
    print('    {:32}'.format('ignore_test: ')                   + str(my_ignore_test_tuple))
    print('    {:32}'.format('test_switch_pyfile: ')            +     test_switch_pyfile)
    print('    {:32}'.format('sim_test_comand_line_switch: ')   + str(sim_test_command_line_switch))
    print('================================================================')

# Support for command line options
# ====================================

# ====================================
#  Functions from run_tests.sh
def green(test_str, ok_fail_str) :
    global test_pass
    global SUITE_XML
    global GREEN
    global NC
    test_pass += 1
    print(test_str + ':' + GREEN + ok_fail_str + NC)
    SUITE_XML += '    <testcase name="' + test_str + '"/>\n'

def yellow(test_str, ok_fail_str) :
    global test_fail
    global SUITE_XML
    global YELLOW
    global NC
    test_fail += 1
    print(test_str + ':' + YELLOW + ok_fail_str + NC)
    SUITE_XML += '    <testcase name="' + test_str + '">\n      <failure message="' + ok_fail_str + '">' + ok_fail_str + '</failure>\n    </testcase>\n'

def red(test_str, ok_fail_str) :
    global test_fail
    global SUITE_XML
    global RED
    global NC
    test_fail += 1
    print(test_str + ':' + RED + ok_fail_str + NC)
    SUITE_XML += '    <testcase name="' + test_str + '">\n      <failure message="' + ok_fail_str + '">' + ok_fail_str + '</failure>\n    </testcase>\n'

def finish_suite(suite_name) :
    global test_pass
    global test_fail
    global all_pass
    global all_fail
    global SUITE_XML
    global SUITES_XML

    print(suite_name + ': Passed ' + str(test_pass) + ' out of ' + str(test_pass + test_fail) + '\n\n')
    date_tmp = subprocess.check_output("date", shell=True, text=True)
    date = date_tmp.rstrip()
    SUITES_XML += '  <testsuite name="' + suite_name + '" tests=' + str(test_pass + test_fail ) + '" failures="' + str(test_fail) + '" timestamp="' + date + '">\n' + SUITE_XML + ' </testsuite>\n'
    SUITE_XML=""
    all_pass += test_pass
    all_fail += test_fail
    test_pass = 0
    test_fail = 0
#  Functions from run_tests.sh
# ====================================


# ====================================
#  Functions for determining file types
#
# TODO:  there MUST be an equivalent to the 'file' command in python.
#   Replace the 'file' command with a python equivalent.

def is_elf(filename) :
    cmd = "file -b " + filename + " | awk 'BEGIN { FS = \",\" } ; { print $1 } ' | grep -q \"ELF\" "
    ret = os.system(cmd)
    if ret == 0 :
        return 1
    else :
        return 0

def is_32bit(filename) :
    cmd = "file -b " + filename + " | awk 'BEGIN { FS = \",\" } ; { print $1 } ' | grep -q \"32-bit\" "
    ret = os.system(cmd)
    if ret == 0 :
        return 1
    else :
        return 0

def is_64bit(filename) :
    cmd = "file -b " + filename + " | awk 'BEGIN { FS = \",\" } ; { print $1 } ' | grep -q \"64-bit\" "
    ret = os.system(cmd)
    if ret == 0 :
        return 1
    else :
        return 0

def is_riscv(filename) :
    cmd = "file -b " + filename + " | awk 'BEGIN { FS = \",\" } ; { print $2 } ' | grep -q \"RISC-V\" "
    ret = os.system(cmd)
    if ret == 0 :
        return 1
    else :
        return 0

def is_riscv_elf(filename) :
    return is_elf(filename) and is_riscv(filename)

def is_riscv_elf_32(filename) :
    return is_riscv_elf(filename) and is_32bit(filename)

def is_riscv_elf_64(filename) :
    return is_riscv_elf(filename) and is_64bit(filename)

def ignore_test(testname) :
    for t in my_ignore_test_tuple :
        debug_print("ignore testname: " + os.path.basename(testname) + " t: " + t)
        if t == os.path.basename(testname) :
            return True
        else :
            continue
    return False
#  Functions for determining file types
# ====================================

def signal_handler(sig, frame):
    degug_print("entering signal_handler() for signal ", sig)
    sys.exit(1)

# Function prototypes
# ===========================================================================79

# ===========================================================================79
# Start of execution....

process_command_line_args(opts)

debug_print("starting...")
debug_print("abspath to this script: " + os.path.abspath(sys.argv[0]))
debug_print("opts: " + str(opts))

# ====================================
# Implicit overrides of program varaibles
if sailcov :
    clean_build = True

if test_switch_pyfile  :
    exec(open(test_switch_pyfile).read())
    # check to see if variable set
    if 'sim_test_command_line_switch_dict' in locals() :
        sim_test_command_line_switch = sim_test_command_line_switch_dict;
    else :
        fatal_print("the python variable, sim_test_command_line_switch_dict, is not properly set in " + test_switch_pyfile)
        sys.exit(1)

if test_ignore_pyfile :
    exec(open(test_ignore_pyfile).read())
    if 'ignore_test_tuple' in locals() :
        my_ignore_test_tuple = ignore_test_tuple
    else :
        fatal_print("the python variable, ignore_test_tuple, is not properly set in " + test_ignore_pyfile)

# Debug print out of important program variables
if debug :
    print_optional_settings()

# TODO: check that only 1 dir in test_dir_list exists
for d in test_dir_list :
    if os.path.exists(d) :
        TESTDIR = d
    else :
        pass

debug_print('TESTDIR : ' + TESTDIR)

# DIR points to the invocation directory.
DIR = os.getcwd()
SEARCH_DIR = DIR
while SEARCH_DIR != '/' :
    if os.path.isfile(SEARCH_DIR + '/' + sail_riscv_rootdir) :
        RISCVDIR = SEARCH_DIR
        break
    if SEARCH_DIR == '/' :
        fatal_print("can't find root directory of repository")
    SEARCH_DIR = os.path.dirname(SEARCH_DIR)
debug_print("RISCVDIR: " + RISCVDIR)

if sailcov :
    MAKE_SAILCOV = "SAILCOV=true"
else :
    MAKE_SAILCOV = ""

if os.path.isfile(DIR + xml_outfile) != False :
    os.remove(DIR + xml_outfile)

# TODO:  Do you really want to run the tests from the RISCVDIR?
# TODO:  check for success/failure of chdir
os.chdir(RISCVDIR)

debug_print("DIR + '/' + TESTDIR + '/' + * :" + DIR + '/' + TESTDIR + '/' + "*")

# Do 'make clean' to avoid cross-arch pollution.

if clean_build :
    cmd = "make ARCH=RV32 clean"
    ret_val = subproc(cmd)
#    ret_val = os.system(cmd)
    if ret_val != 0 :
        fatal_print("non-zero exit value from command: '" + cmd + "'")
    else :
        pass
else :
    pass

if clean_build :
    cmd = "make ARCH=RV32 clean"
    ret_val = subproc(cmd)
#    ret_val = os.system(cmd)
    if ret_val != 0 :
        fatal_print("non-zero exit value from command: '" + cmd + "'")
        sys.exit(1)
    else :
        pass
else :
    pass

print("Building 32-bit RISCV specification...")
if run_csim :
    if run_32bit_tests :
        cmd = "make ARCH=RV32 " + MAKE_SAILCOV + " c_emulator/riscv_sim_RV32"
        ret_val = subproc(cmd)
#        ret_val = os.system(cmd)
        if ret_val == 0 :
            green("Building 32-bit RISCV C emulator", "ok")
        else :
            red("Building 32-bit RISCV C emulator","fail")
            error_print("non-zero exit value from command: '" + cmd + "'")

if run_32bit_tests and run_csim :
    for test in glob.glob(DIR + '/' + TESTDIR + '/' + "*") :
        if not is_riscv_elf_32(test) :
            continue
        if ignore_test(test) :
            debug_print("ignoring test: " + test)
            continue
        outfile = test + ".cout"
        sim_switch = ""
        for key in sim_test_command_line_switch :
            pat = re.compile(key)
            mo = pat.search(test)
            if mo != None:
                sim_switch = sim_test_command_line_switch[key]
                break

        if sailcov :
            run_sailcov = " --sailcov-file sailcov_RV32"
        else :
            run_sailcov = ""

        cmd = "timeout 5 " + RISCVDIR + "/c_emulator/riscv_sim_RV32" + run_sailcov + " " + sim_switch + " " + test + " > " + outfile + " 2>&1 && grep -q SUCCESS " + outfile
        debug_print("cmd: '" + cmd + "'")
        ret_val = subproc(cmd)
#        ret_val = os.system(cmd)
        if ret_val == 0 :
           green("C-32 " + os.path.basename(test), "ok")
        else :
           red("C-32 " + os.path.basename(test),  "fail")
else :
    pass

finish_suite("32-bit RISCV C-simulator tests")

if clean_build :
    cmd = "make ARCH=RV64 clean"
    ret_val = subproc(cmd)
#    ret_val = os.system(cmd)
    if ret_val != 0 :
        fatal_print("non-zero exit value from command: '" + cmd + "'")
    else :
        pass
else :
    pass

print("Building 64-bit RISCV specification...")

if clean_build :
    cmd = "make ARCH=RV64 clean"
    ret_val = subproc(cmd)
#    ret_val = os.system(cmd)
    if ret_val != 0 :
        fatal_print("non-zero exit value from command: '" + cmd + "'")
    else :
        pass
else :
    pass

print("Building 64-bit RISCV specification...")
if run_csim :
    if run_64bit_tests :
        cmd = "make ARCH=RV64 " + MAKE_SAILCOV + " c_emulator/riscv_sim_RV64"
        ret_val = subproc(cmd)
#        ret_val = os.system(cmd)
        if ret_val == 0 :
            green("Building 64-bit RISCV C emulator", "ok")
        else :
            red("Building 64-bit RISCV C emulator","fail")
            error_print("non-zero exit value from command: '" + cmd + "'")

if run_64bit_tests and run_csim :
    for test in glob.glob(DIR + '/' + TESTDIR + '/' + "*") :
        debug_print("test: " + test)
        if not is_riscv_elf_64(test) :
            continue
        if ignore_test(test) :
            debug_print("ignoring test: " + test)
            continue
        outfile = test + ".cout"
        sim_switch = ""
        for key in sim_test_command_line_switch :
            pat = re.compile(key)
            mo = pat.search(test)
            if mo != None:
                sim_switch = sim_test_command_line_switch[key]
                break

        if sailcov :
            run_sailcov = " --sailcov-file sailcov_RV64"
        else :
            run_sailcov = ""

        cmd = "timeout 5 " + RISCVDIR + "/c_emulator/riscv_sim_RV64" + run_sailcov + " " + sim_switch + " " + test + " > " + outfile + " 2>&1 && grep -q SUCCESS " + outfile
        ret_val = subproc(cmd)
#        ret_val = os.system(cmd)
        if ret_val == 0 :
           green("C-64 " + os.path.basename(test), "ok")
        else :
           red("C-64 " + os.path.basename(test),  "fail")
else :
    pass

finish_suite("64-bit RISCV C-simulator tests")

print('Passed ' + str(all_pass) + ' out of ' + str(all_pass + all_fail) + '\n\n')
XML = '<testsuites tests="' + str(all_pass + all_fail) + '" failures="' + str(all_fail) + '">\n' + SUITES_XML + '</testsuites>\n'

xml_outfile_fh = open(DIR + '/' + xml_outfile, 'w')
print(XML, file = xml_outfile_fh)
xml_outfile_fh.close()

if all_fail > 0 :
    sys.exit(1)
else :
    sys.exit(0)
