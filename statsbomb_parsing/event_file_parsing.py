#!/usr/bin/Python

# Created by: Christopher J Adams 5/2/2020

###############################################################################
###
### This script read through statsbomb event files
###
###############################################################################


import json
import getopt
import sys


def help(exit_num=1):
    print("""-----------------------------------------------------------------
ARGUMENTS
    -e => <yaml> event file                 REQUIRED


""")
    sys.exit(exit_num)


## MAIN ##

def main(argv):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "e:")
    
    except getopt.GetoptError:
        print("Error: Incorrect usage of getopts flags!")
        help()

    options_dict = dict(opts)

    ## Required arguments
    try:
        event_file = options_dict['-e']
    
    except KeyError:
        print("Error: One of your required arguments does not exist.")
        help()

    # Optional arguments

    print("Acceptable Inputs Given")

    driver(event_file)


def driver(event_file):

    event_dict = open_json_dict(event_file)
    count = 0
    for event in event_dict:
        #print(event)
        count += 1
        #if count == 10:
        #    break
    
    print(count)
def open_json_dict(f):
    
    with open(f, 'r') as j_file:
        d = json.load(j_file)

    return d


if __name__ == "__main__":
    main(sys.argv[1:])
