#!/usr/bin/env python

# searchUrl = www.redfin.com/stingray/do/query-location?location=<mls>
# Get URL field from response

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

class NotFoundException(Exception):
    pass

class RetrievalError(Exception):
    pass

REDFINURL = "http://www.redfin.com"
REDFINRE = "http://www.redfin.com/stingray/do/query-location?location={mls}"

def tovalue(price):
    return "".join(price.split(',')).strip("$")

def retrieve(mls, state="md"):
    url = None 
    # Get the first page for the redirection to the list of matches
    try:
        url = REDFINRE.format(mls=mls)
        (a,b,c) = dl.retrieve_url(url)
        # c contains meta data, but not all of it
        del b
    except:
        raise NotFoundException("Error retrieving {0}".format(mls))

    try:
        url = re.search('"URL":"([a-zA-Z0-9\/\\-_]+)",', c).group(1)
        url = REDFINURL + url
        (a,b,c) = dl.retrieve_url(url)
        del b
        return c
    except:
        raise RetrievalError("Failed!")

DIVIDENDS = {
    "Annually": 12,
    "Quarterly": 3,
    "Semi-Annually": 6,
}

def _find_hoa(b):
    try:
        h = b.findAll('h4', text="Homeowners Association Information")[0]
        if h is None:
            return 0
        ul = h.findNext('ul')  
        fee = ""
        freq = ""
        for li in ul.findChildren('li'):
            text = li.getText()
            m = re.match("Fee:\s\$(.*)", text)
            if m is not None:
                fee = m.group(1)
            m = re.match("Fee\sPayment\sFrequency:\s(.*)", text)
            if m is not None:
                freq = m.group(1)
        #print("HOA       : {0} {1}".format(fee, freq))
        div = DIVIDENDS.get(freq, 1)
        price = float(fee)/float(div)
        #print("Calculated: {0:.02}".format(price))
        return price
    except:
        #print("Couldn't find HOA")
        return 0

def _find_status(b):
    try:
        status = "Unknown"
        for t in b.findAll('td', attrs={'class':'property_detail_label left_column'}):
            if t.getText().strip() == "Status:":
                u = t.nextSibling
                status = u.findNext('a').getText()
                #print("Status    : {0}".format(status))
        return status
    except:
        #print("Couldn't find status")
        raise

def _find_address(b):
    try:
        addr1 = b.findAll('span', attrs={"class":"street-address"})[0].getText()
        locality = b.findAll('span', attrs={'class':'locality'})[0].getText()
        region = b.findAll('span', attrs={'class':'region'})[0].getText()
        zip = b.findAll('span', attrs={'class':'postal-code'})[0].getText()
        address = "{0}, {1}, {2}  {3}".format(addr1, locality, region, zip) 
        #print("Address   : {0}".format(address))
        return address
    except:
        #print("Could not get address")
        return ""

def _find_price(b):
    try:
        price = b.findAll('div', attrs={"class":"price"})[0].getText()
        m = re.search("Listed\sat:(.*)", price)
        if m is not None:
            price = m.group(1).strip()
        else:
            price = tovalue(price)
        #print("Price     : {0}".format(str(price)))
        return float(util.format_number(price))
    except:
        print("Couldn't find price")
        raise

def _find_taxes(b):
    try:
        taxes = None
        for l in b.findAll('li'):
            text = l.getText()
            m = re.search(r"Total\sTaxes:\s\$(.*)", text)
            if m is not None:
                taxes = m.group(1)
                #print("Taxes     : {0}".format(taxes))
        if taxes is None:
            return 0
        return taxes
    except:
        #print("Couldn't find taxes")
        raise

def _find_beds(b):
    try:
        beds = "Error" 
        for t in b.findAll('td', attrs={'class':'property_detail_label left_column'}):
            if t.getText().strip().lower() == "beds:":
                u = t.nextSibling
                beds = u.findNext('td').getText().strip()
                #print("Status    : {0}".format(status))
        return beds
    except:
        #print("Couldn't find status")
        raise

def _find_baths(b):
    try:
        baths = "Error" 
        for t in b.findAll('td', attrs={'class':'property_detail_label left_column'}):
            if t.getText().strip().lower() == "baths:":
                u = t.nextSibling
                baths = u.findNext('td').getText().strip()
                #print("Status    : {0}".format(status))
        return baths
    except:
        #print("Couldn't find status")
        raise

def parse_house(data, mlsnum):
    try:
        b = bs.BeautifulSoup(data)
        mls = b.findAll('td', attrs={"id":"mls_id"})[0].getText()
        if mls is None:
            raise NotFoundException("Couldn't find the house")
        price = _find_price(b)
        address = _find_address(b)
        taxes = _find_taxes(b)       
        status = _find_status(b)
        hoa = _find_hoa(b)
        beds = _find_beds(b)
        baths = _find_baths(b)
    except IndexError:
        raise NotFoundException("Error finding")
    except:
        print("Error retrieving {0}".format(mlsnum))
        raise
        
    h = house.House(MLS=mls, 
                    Price=price, 
                    Address=address, 
                    HOA=hoa, 
                    Status=status,
                    Taxes=util.format_number(taxes),
                    Beds=beds,
                    Baths=baths
                    )

    return h

def get_house(mls, state="md"):
    try:
        data = retrieve(mls, state=state)
        if data is None:
            return None
        else:
            h = parse_house(data, mls)
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
        data = retrieve(mls, state=state)
        h = parse_house(data, mls)
        print("{0}".format(str(h)))
    except RetrievalError:
        print("Could not find {0}".format(mls))
        sys.exit(1)
