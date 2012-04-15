from __future__ import print_function
import xml.dom.minidom as xmlparse
import re
import downloader as dl
import remax

URLRE="http://maps.googleapis.com/maps/api/distancematrix/xml?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false&units=imperial"

def calculate_distance(x,y):
    try:
        x1 = re.sub(r' ', r'\+', x) 
        y1 = re.sub(r' ', r'\+', y)
        url = URLRE.format(x1, y1)
        (code, url, data) = dl.retrieve_url(url)
        x = xmlparse.parseString(data)
        distance = x.getElementsByTagName('distance')[0]
        value = remax.getnodetext(distance.getElementsByTagName('text')[0])
        return str(value)
    except Exception, e:
        print("Error: {0}".format(e))
        raise

if __name__ == "__main__":
    import sys
    try:
        distance = calculate_distance(sys.argv[1], sys.argv[2])
    except IndexError:
        print("{0} <addr1> <addr2>".format(sys.argv[0]))
        sys.exit(1)
