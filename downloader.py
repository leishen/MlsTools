#!/usr/bin/env python

import httplib
import urllib2
import logging

class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result

def format_url(url):
    if url.startswith("http://"):
        url = "".join(url[7:])
    elif "/" not in url:
        # Handle an escaped relative path
        url = urllib2.unquote(url)
    return url.partition("/")

def full_url(url):
    if not url.startswith("http://"):
        return "http://" + url
    return url

def url_to_path(url):
    if not url.startswith("http://"):
        raise ValueError("Need a full URL (with http://), not '%s'" % (url))
    url = "".join(url[7:])
    return url

def get_url_response(url):
    try:
        httplib.HTTPConnection.debuglevel = 1
        newurl = full_url(url)
        logging.debug("GET %s" % (newurl))
        request = urllib2.Request(newurl)
        res = urllib2.urlopen(request)
        logging.debug("[%3d] %s" % (res.code, res.url))
        return res
    except:
        return None

def retrieve_url_data(res):
    try:
        encoding = res.headers.getparam("charset")
    except:
        encoding = None
    #print str(dir(res))
    #print str(res.url)
    #print str(res.code)
    if encoding is not None:
        data = res.read().decode(encoding).encode('utf_8')
    else:
        data = res.read()
    #print "Data is %s" % (str(type(data)))
    return (res.code, res.url, data)

def retrieve_url(url):
    res = get_url_response(url)
    return retrieve_url_data(res)

if __name__ == "__main__":
    import sys
    try:
        url = sys.argv[2]
        fname = sys.argv[1]
    except IndexError, e:
        print "Usage: %s <file> <url>"
        sys.exit(0)
   
    retrieve_url(url, file=fname)

