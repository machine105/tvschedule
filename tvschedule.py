# -*- coding: utf-8 -*-
import re
import urllib2
import channels

def extract_titles(html):
    matches = re.finditer(r'<a class=\"title', html)
    for match in matches:
        print(match.group())

chs = channels.TVTokyo()
chs.fetch()

