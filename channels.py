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
#   <p class='txcms_unit13ProgramUnitTitle'><a> TITLE </a></p>
# [time]
#   <p class='txcms_unit13ProgramUnitTimeText'> TIME </p>
# [date]
#   <td class='txcms_cms_dYYYYMMDD'>...</td>
# [url]
#   <a href='URL'> TITLE </a>
#   OR if official link exists,
#   <div class='txcms_officialBtn'><a href='URL'>もっと詳しく</a></div>
class TVTParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        # 
        self.programs = []
        # reading flags
        self.readingProgram = False
        self.readingTitle = False
        self.readingTime = False
        self.readingOfficialURL = False # some programs have an official link
        # data buffer
        self.buf = {}

    def handle_starttag(self, tag, attr):
        attr = dict(attr)
        if tag == 'div':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'txcms_officialBtn' in splited:
                    self.readingOfficialURL = True
        elif tag == 'p':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'txcms_unit13ProgramUnitTitle' in splited:
                    self.readingTitle = True
                elif 'txcms_unit13ProgramUnitTimeText' in splited:
                    self.readingTime = True
        elif tag == 'td':
            if 'class' in attr:
                splited = attr['class'].split()
                if not 'txcms_isBlank' in splited and not 'txcms_unit13MainCell' in splited:
                    for text in splited:
                        m = re.match(ur'txcms_cms_d([0-9]{8})', text)
                        if m:
                            self.readingProgram = True
                            self.buf['date'] = m.group(1)
        elif tag == 'a':
            if self.readingTitle:
                self.buf['url'] = 'http://www.tv-tokyo.co.jp' + attr['href']
            elif self.readingOfficialURL:
                self.buf['url'] = attr['href']

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
            elif self.readingTime:
                self.readingTime = False
        elif tag == 'div':
            if self.readingOfficialURL:
                self.readingOfficialURL = False
        elif tag == 'td':
            if self.readingProgram:
                self.programs.append(self.buf)
                self.buf = {}
                self.readingProgram = False
            
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
            
        
