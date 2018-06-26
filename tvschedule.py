# -*- coding: utf-8 -*-
import re
import urllib2

def getHTML(url):
    res = urllib2.urlopen(url)
    html = res.read()
    f = open('log.html', 'w')
    f.write(html)
    f.close()
    return html

def extract_titles(html):
    matches = re.finditer(r'<a class=\"title', html)
    for match in matches:
        print(match.group())
