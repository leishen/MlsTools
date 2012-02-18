#!/usr/bin/env python

from __future__ import print_function
import downloader as dl
import urllib2
import logging
import os.path
import re
import xml.dom.minidom as xmlparse
import house
import util
from xmlutils import getnodetext
try:
    import BeautifulSoup as bs
except ImportError:
    import sys
    print("Please download and install BeautifulSoup to use these utilities")
    sys.exit(1)

KEYMAP = {
    "MLSNumber": "MLS",
    "Price": "Asking Price",
    "Taxes": "Yearly Taxes",
}
 
class NotFoundException(Exception):
    pass

class RetrievalError(Exception):
    pass

REMAXRE = "http://www.remax.com/residential/property_search/mlsnumber_property_search/index.aspx?mls={mls}&state={state}&seo=1"

def retrieve(mls, state="md"):
    url = None 
    # Get the first page for the redirection to the list of matches
    try:
        url = REMAXRE.format(mls=mls, state=state)
        (a,b,c) = dl.retrieve_url(url)
        b = bs.BeautifulSoup(c)
        scripts = b.findAll('script')
        for s in scripts:
            m = re.search(r"window.location = '(.*)'", str(s))
            if m is not None:
                url = m.group(1)
        del b
        del c
    except:
        raise NotFoundException("Error retrieving {0}".format(mls))

    if url is None:
        raise NotFoundException("Error retrieving {0}".format(mls))

    # Get the second page for the list of matches, and grab the first match
    try:
        (a,b,c) = dl.retrieve_url(url)
        url = None
        b = bs.BeautifulSoup(c)
        links = b.findAll('a')
        for l in links:
            a = l.get('href')
            if a is not None:
                m = re.search(r"/property/(.*)", str(a))
                if m is not None:
                    #print("Matched on {url}".format(url=m.group(1)))
                    url = "http://www.remax.com/property/{rest}".format(rest=m.group(1))
                    break
        del b
        del c
    except KeyboardInterrupt:
        raise
    except Exception, e:
        raise NotFoundException("Retrieval error: {0}".format(e))

    if url is None:
        raise NotFoundException("Error retrieving {0}: Could not determine url".format(mls))

    try:
        # Get the house details page itself 
        (a,b,c) = dl.retrieve_url(url)
        xml = ''
        m = re.search("g_strXML = '(.*)'", str(c))
        if m is not None:
            xml = str(m.group(1))
            # Works better (read: at all) if we format it utf-8 instead of utf-16
            xml = re.sub("utf-16", "utf-8", xml)
        return xml
    except KeyboardInterrupt:
        raise
    except Exception, e:
        raise RetrievalError("Could not get details for {0}: {1}".format(mls, e))

def parse_house(xmlstr):
    x = xmlparse.parseString(xmlstr)
    try:
        mlsnum = getnodetext(x.getElementsByTagName('MLSNumber')[0])
        price = getnodetext(x.getElementsByTagName('Price')[0])
        status = getnodetext(x.getElementsByTagName('ListingStatus')[0])
    except:
        raise
        
    try:
        taxes = getnodetext(x.getElementsByTagName('Taxes')[0])
    except:
        taxes = None
    try:
        addr = x.getElementsByTagName('Address')[0]
        city = x.getElementsByTagName('City')[0]
        state = x.getElementsByTagName('State')[0]
        zip = x.getElementsByTagName('Zip')[0]
        address = '{0}, {1}, {2}  {3}'.format(getnodetext(addr), getnodetext(city), 
                                              getnodetext(state), getnodetext(zip))
    except:
        address = None
    try:
        nodes = x.getElementsByTagName('MainFeature') # Find the 'Rental Price' name element
        hoa = "0"
        for n in nodes:
            # RE/MAX stores the HOA in an element called 'Fees' but doesn't specify
            # whether it's annually, monthly, ...
            if n.getAttribute("Name") == "Fees":
                hoa = n.getAttribute("Value")
    except:
        pass

    h = house.House(MLS=mlsnum, 
                    Price=util.format_number(price), 
                    Address=address, 
                    HOA=util.format_number(hoa), 
                    Status=status,
                    Taxes=util.format_number(taxes))

    return h

def get_house(mls, state="md"):
    try:
        xml = retrieve(mls, state=state)
        if xml is None:
            return None
        else:
            h = parse_house(xml)
            return h
    except RetrievalError:
        raise 

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        print("{prog} <mls> [state]".format(prog=sys.argv[0]))
        sys.exit(1)
    if len(sys.argv) == 3:
        state = sys.argv[2]
    else:
        state = "md"
    mls = sys.argv[1]
    try:
        xml = retrieve(mls, state=state)
        house = get_house(mls, state=state)

        print("{0}".format(str(house)))
    except RetrievalError:
        print("Could not find {0}".format(mls))
        sys.exit(1)
