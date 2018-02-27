# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

import sys
import os
import csv
from collections import OrderedDict

# Sorts the nests for a given city

ext = ".tsv"
citypath = "cities/"

# set this to the empty string to run it in production mode and overwrite the city's file
# put something here to run in test mode and generate a separate output file
tstext = ""


# asks the user for the name of the city they want to sort
def getcity():
    return input("Which city would you like to sort? ") + ext

city = None
if len(sys.argv) > 1:
    city = sys.argv[1] + ext


# checks if the city has a file in the cities directory
def validate_cityfile(city):
    if os.path.isfile(citypath+city):
        return True
    else:
        print(city + " is not a valid file in the " + citypath + " directory.")
        return False


# pick a file from the city folder archive
def choose_city(city=None):
    while city is None or validate_cityfile(city) is False:
        city = getcity()
    return citypath+city


# reads a tsv city nest list into memory and returns it
def read_city(cfile):
    cmem = open(cfile, "r")
    nestin = csv.DictReader(cmem, delimiter="\t")
    nestout = {}
    nestout[""] = {}
    first = True
    for nest in nestin:
        # convert to lower case and hope for the best with non-ASCII names
        # print(nest) # debugging the inputs
        sortkey = nest["Primary Name"].lower() + nest["Location"].lower()
        nestout[sortkey] = {}
        for key in nest.keys():
            nestout[sortkey][key] = nest[key]
            if first is True:
                nestout[""][key] = ""
        first = False
        #print(nestout[sortkey])
    cmem.close()
    return nestout


# sorts the nestlist
def sort_nests(nestlist):
    sorted_nests = OrderedDict(sorted(nestlist.items()))
    return sorted_nests


# writes the sorted nests back to the file
def write_nests(nestlist, cfile):
    out = open(cfile+tstext, "w")
    #print(nestlist)
    writer = csv.DictWriter(out, delimiter="\t", fieldnames=nestlist[""], quoting=csv.QUOTE_ALL)
    writer.writeheader()
    del nestlist[""] # remove the header row (different use than rest of the list)
    for nest in nestlist:
        writer.writerow(nestlist[nest])
    out.close()
    return


# main method and all
def main():
    cfile = choose_city(city)
    nestlist = read_city(cfile)
    nestlist = sort_nests(nestlist)
    write_nests(nestlist, cfile)
    print("Successfully sorted " + cfile)
    return

if __name__ == "__main__":
    main()
