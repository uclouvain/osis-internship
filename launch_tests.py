#!/usr/bin/env python

from functools import reduce
import os,sys,getopt

# Tests Classes
#==============

# Unit tests classes
UNIT_TESTS_CLASSES = []

# Selenium tests classes
SELENIUM_TESTS_CLASSES = [
    'core.tests.selenium.score_encoding_tests',
]

# All tests classes
ALL_TESTS_CLASSES = UNIT_TESTS_CLASSES + SELENIUM_TESTS_CLASSES
COMMAND = PRECOMAND = 'python3 manage.py jenkins -v 2 --enable-coverage '


def main(argv):
    try:
        opts,args = getopt.getopt(argv,"hat:",["--help","type="])
    except getopt.GetoptError:
        print('Usage : launch_test.py <OPTIONS> [ARGS]]')
        print('Type launch_test.py -h to see options')
        sys.exit(2)
    for opt,arg in opts :
        if opt=='-h':
            print('launch_test.py <OPTIONS> [ARGS]')
            print('OPTIONS : ')
            print(' -h : Show this message')
            print(' -t <TYPE> : Launch the tests of a specific type')
            print('     TYPE :')
            print('      selenium : Selenium tests')
            print('      unit : Unit tests tests')
            print(' -a : Run tests of all types')
            sys.exit()
        elif opt == "-t" :
            if arg is None :
                print('Usage : launch_test.py <OPTIONS> [ARGS]')
                print('Type launch_test.py -h to see options')
                sys.exit(2)
            elif arg == "unit" :
                ARGS = reduce(lambda s1,s2 : s1+' '+s2, UNIT_TESTS_CLASSES)
                COMMAND = PRECOMAND + ARGS
            elif arg == "selenium" :
                ARGS = reduce(lambda s1,s2 : s1+' '+s2, SELENIUM_TESTS_CLASSES)
                COMMAND = PRECOMAND + ARGS
        elif opt == "-a" :
            ARGS = reduce(lambda s1,s2 : s1+' '+s2, ALL_TESTS_CLASSES)
            COMMAND = PRECOMAND + ARGS

    os.system(COMMAND)

if __name__ == "__main__" :
    main(sys.argv[1:])
