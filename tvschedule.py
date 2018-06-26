# -*- coding: utf-8 -*-
import re
import urllib2

def getHTML(url):
    res = urllib2.urlopen(url)
    html = res.read()
    return html

