#!/usr/bin/env python
"""
To use this, get your list of favorites from Redfin.com and the spreadsheet of 
houses you're looking at, and then run this script against both csv files
"""

# Parse CSV downloads from redfin, compare against stored
from __future__ import print_function
from csvreader import read_csv

def mls_list(filename):
    lst = read_csv(filename)
    return map(lambda x: x['LISTING ID'], lst)

def read_file(filename):
    lst = read_csv(filename)
    houses = mls_nums(lst)
    return houses

def compare_lists(lst1, lst2, label1="Set 1", label2="Set 2"):
    """Determine which houses are in each list, and return the set of houses that are in 
    one but not the other, and indicate which set they're in"""
    dct = {}
    set1 = frozenset(lst1)
    set2 = frozenset(lst2)
    discrepant = set1.symmetric_difference(set2)
    for d in discrepant:
        if d in set1:
            dct[d] = label1
        else:
            dct[d] = label2
    return dct

if __name__ == "__main__":
    import csvreader
    import sys
    try:
        redfins = mls_list(sys.argv[1])
        watches = csvreader.mls_list(sys.argv[2])
        d = compare_lists(redfins, watches, label1="Redfin", label2="Spreadsheet")
        for k,v in d.iteritems():
            print("{0}: {1}".format(k,v))
    except IndexError:
        print("{0} <csv1> <csv2>".format(sys.argv[0]))
        sys.exit(1)
    
