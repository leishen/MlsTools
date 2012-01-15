#!/usr/bin/env python
from __future__ import print_function
import csv
import remax
import exceptions
import house
import util
import xml

def read_csv(csvfile):
    try:
        fh = open(csvfile, "r")
        csv_reader = csv.DictReader(fh)
        # Reset of the rows are data
        return csv_reader
    except csv.Error, e:
        print("CSV Error: {0}".format(str(e)))
        raise
    except IOError, e:
        print("I/O Error: {0}".format(str(e)))
        raise

def read_houses(lst):
    houses = []
    for h in lst:
        t = house.House(MLS=h['MLS'], Price=util.format_number(h['Asking Price']), 
                        Taxes=util.format_number(h['Yearly Taxes']), 
                        HOA=util.format_number(h['HOA (Monthly)']), 
                        Address=h['Address'])
        houses.append(t)
    return houses

def lookup_houses(filename):
    lst = read_csv(filename)
    houses = read_houses(lst)
    for t in houses:
        print("{0}: ".format(t.MLS), end="")
        try:
            tocompare = remax.get_house(t.MLS)
            #print(str(dir(tocompare)))
        except xml.parsers.expat.ExpatError, e:
            print("Must manually lookup {0}".format(t.MLS))
            continue
        except remax.RetrievalError:
            print("Error retrieving {0}".format(t.MLS))
            continue
        if tocompare is None:
            print("House '{0}' is no longer available!!!".format(t.MLS))
        elif tocompare != t:
            print("Price changed to '${0:.02f}'".format(tocompare.Price))
            #print(str(t))
            #print(str(tocompare))
        elif tocompare.status() != "active":
            print("Status changed to '{0}'".format(tocompare.Status))
        else:
            print("No change")

if __name__ == "__main__":
    import sys
    try:
        lookup_houses(sys.argv[1])
    except IndexError:
        print("{prog} <file>".format(sys.argv[0]))
    except KeyboardInterrupt:
        print("Interrupted!")   


