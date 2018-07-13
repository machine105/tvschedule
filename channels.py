# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import urllib2
from HTMLParser import HTMLParser
import re

# get raw HTML from url
def getHTML(url):
    res = urllib2.urlopen(url)
    html = res.read()
    return html

class Channel(object):
    # endpoint: url in which the schedule is available
    def __init__(self, _endpoint):
        self.endpoint = _endpoint
        
    def fetch(self, date):
        raise NotImplementedError()

    def getProgramAt(self, date, time):
        raise NotImplementedError()

# HTMLParser for TVTokyo
#
# TVTokyo Format:
# [title]
#   <p class='txcms_unit13ProgramUnitTitle'> $TITLE$ </p>
# [time]
#   <p class='txcms_unit13ProgramUnitTimeText'> $TIME$ </p>
# [date]
#   <td class='txcms_cms_dYYYYMMDD'>...</td>
class TVTParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        # 
        self.programs = []
        # reading flags
        self.readingTitle = False
        self.readingTime = False
        # data buffer
        self.buf = {}

    def handle_starttag(self, tag, attr):
        attr = dict(attr)
        if tag == 'p':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'txcms_unit13ProgramUnitTitle' in splited:
                    self.readingTitle = True
                elif 'txcms_unit13ProgramUnitTimeText' in splited:
                    self.readingTime = True
        elif tag == 'td':
            if 'class' in attr:
                splited = attr['class'].split()
                for text in splited:
                    m = re.match(ur'txcms_cms_d([0-9]{8})', text)
                    if m:
                        self.buf['date'] = m.group(1)

    def handle_data(self, data):
        if self.readingTitle:
            #print data
            self.buf['title'] = data
        if self.readingTime:
            #print data
            self.buf['time'] = int(data.replace(':', '')) # hh:mm -> hhmm

    def handle_endtag(self, tag):
        if tag == 'p':
            if self.readingTitle:
                self.readingTitle = False
                self.programs.append(self.buf)
                self.buf = {}
            elif self.readingTime:
                self.readingTime = False
            
# TVTokyo
class TVTokyo(Channel):
    def __init__(self):
        super(TVTokyo, self).__init__('http://www.tv-tokyo.co.jp/index/timetable/')
        self.programs = []
    
    def fetch(self):
        html = getHTML(self.endpoint)
        parser = TVTParser()
        parser.feed(html)
        self.programs = parser.programs

    # get Program on air at TIME on DATE
    # if No Program on air then return None
    def getProgramAt(self, date, time):
        time = int(time)
        while True:
            for program in self.programs:
                if program['date'] == date and program['time'] == time:
                    return program
            time = time - 1
            if time < 300:
                return None
            
        
