#!/usr/bin/env python
from __future__ import print_function
import csv
import remax
import house
import util
import xml
import xml.parsers
import xml.parsers.expat

try:
    from clint.textui import colored
    blue = colored.blue
    red = colored.red
    yellow = colored.yellow
    green = colored.green
except Exception, e:
    print("Error: {0}".format(e))
    print("'pip install clint' to get colored output")
    blue = str
    red = str
    yellow = str
    green = str

def read_csv(csvfile):
    try:
        fh = open(csvfile, "r")
        csv_reader = csv.DictReader(fh)
        # Rest of the rows are data
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

def mls_list(filename):
    lst = read_csv(filename)
    houses = read_houses(lst)
    return map(lambda x: x.MLS, houses)

def get_houses(filename):
    lst = read_csv(filename)
    houses = read_houses(lst)
    return houses

def find_updates(filename):
    houses = get_houses(filename)
    for t in houses:
        #print("{0}: ".format(t.MLS), end="")
        try:
            tocompare = remax.get_house(t.MLS)
        except xml.parsers.expat.ExpatError, e:
            print(yellow("{0}: Must manually lookup (xml parsing error): {1}".format(t.MLS, e)))
            continue
        except remax.RetrievalError:
            print(yellow("{0}: Error retrieving".format(t.MLS)))
            continue
        except remax.NotFoundException, e:
            print(red("{0}: House is no longer available!!!".format(t.MLS)))
            continue

        if tocompare is None:
            print(red("{0}: House is no longer available!!!".format(t.MLS)))
        elif tocompare.status() != "active":
            print(red("{0}: Status changed to '{1}'".format(t.MLS, tocompare.Status)))
        elif tocompare != t:
            print(blue("{0}: Price changed to '${1:.02f}'".format(t.MLS, tocompare.Price)))
        else:
            print("{0}: No change".format(t.MLS))

if __name__ == "__main__":
    import sys
    try:
        find_updates(sys.argv[1])
    except IndexError:
        print("{prog} <file>".format(sys.argv[0]))
    except KeyboardInterrupt:
        print("Interrupted!")   


