# -*- coding: utf-8 -*-
import urllib2
from HTMLParser import HTMLParser
import datetime
import re
import json

# get raw HTML from url
def getHTML(url):
    res = urllib2.urlopen(url)
    html = res.read()
    return html

class Channel(object):
    # endpoint: url in which the schedule is available
    def __init__(self, _endpoint):
        self.endpoint = _endpoint
        self.programs = []

    # get imformation of all programs
    def fetch(self, date = 'today'):
        raise NotImplementedError()

    # get program on air at TIME on DATE
    # if no program on air then return None
    def program_at(self, date, time):
        time = int(time)
        while True:
            for program in self.programs:
                if program['date'] == date and program['time'] == time:
                    return program
            time = time - 1
            if time < 300:
                return None

# TVTokyo Format:
#  information of programs can be get as json file at
#  [http://www.tv-tokyo.co.jp/tbcms/assets/data/YYYYMMDD.json]
#  
#  This json contains information as follows:
#   json
#    +- "HHMM"
#    |  +- "1"
#    |  |  +- "rowspan":    airtime[min]
#    |  |  +- "url":        url without 'http:'
#    |  |  +- "start_time": start time [H:MM]
#    |  |  +- "title":      title
#    |  |  +- "channel":    channel [tv-tokyo/bs-tv-tokyo/bs-tv-tokyo-4k]
#    |  |  +- other keys
#    |  +- "2"
#    |  |  +- ...
#    |  ...
#    ...
class TVTokyo(Channel):
    def __init__(self):
        super(TVTokyo, self).__init__('http://www.tv-tokyo.co.jp/tbcms/assets/data/')
        self.programs = []

    # arg date has no meaning in this function
    # fetches all programs in the week
    def fetch(self, date = 'today'):
        if date == 'today':
            date = datetime.datetime.now().strftime('%Y%m%d')
        res = urllib2.urlopen(self.endpoint + date + '.json')
        js = json.load(res)
        for time, prog in js.items():
            for key, info in prog.items():
                if info['channel'] == 'tv-tokyo':
                    tmp = {}
                    tmp['date'] = date
                    tmp['time'] = int(time)
                    tmp['title'] = info['title'] 
                    self.programs.append(tmp)

# HTMLParser for Tokyo MX
#
# TokyoMX Format:
# [overview]
#   <td class="sd1_cell_s ...">...</td>
# [endpoint]
#   http://s.mxtv.jp/bangumi_pc/?date=yyyymmdd
# [title]
#   <div class='oa_title'><a href=URL>TITLE</a></div>
# [time]
#   <div class='oa_time'>hh:mm</div>
# [date]
#   specified in [endpoint]
# [url]
#   specified in [title]
#   (no direct link to official pages)
class MXParser(HTMLParser, object):
    def __init__(self, date):
        super(MXParser, self).__init__()
        self.programs = []
        self.buf = {}
        self.date = date
        # reading flags
        self.readingProgram = False
        self.readingTitle = False
        self.readingTime = False

    def handle_starttag(self, tag, attr):
        attr = dict(attr)
        if tag == 'td':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'sd1_cell_s' in splited:
                    self.readingProgram = True
        elif tag == 'div':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'oa_time' in splited:
                    self.readingTime = True
                elif 'oa_title' in splited:
                    self.readingTitle = True
                elif 'oa_subtitle' in splited:
                    self.readingTitle = False
        elif tag == 'a':
            if self.readingTitle:
                self.buf['url'] = attr['href']

    def handle_data(self, data):
        if self.readingTime:
            self.buf['time'] = int(data.replace(':', ''))
        elif self.readingTitle:
            self.buf['title'] = data

    def handle_endtag(self, tag):
        if tag == 'div':
            if self.readingTime:
                self.readingTime = False
            elif self.readingTitle:
                self.readingTitle = False
        elif tag == 'td':
            if self.readingProgram:
                self.buf['date'] = self.date
                self.programs.append(self.buf)
                self.buf = {}
                self.readingProgram = False
                
        

# Tokyo MX        
class TokyoMX(Channel):
    def __init__(self):
        super(TokyoMX, self).__init__('http://s.mxtv.jp/bangumi_pc/')
        self.programs = []

    def fetch(self, date = 'today'):
        if date == 'today':
            date = datetime.date.today().strftime('%Y%m%d')
        html = getHTML(self.endpoint + '?date=' + date)
        parser = MXParser(date)
        parser.feed(html)
        self.programs = parser.programs

# HTMLParser for TBS
#
# TBS Format
# [overview]
#   <td class='day'><div class='info_wide'><a>...</a></div></td> (day = 'mon', 'tue', ..., 'sun')
# [title]
#   <strong> TITLE </strong>
# [time]
#   <span class="oa"> TIME </span>
#   NOTE: TIME is in 0:00 - 12:59
# [date]
#   inferred from day
# [url]
#   <a href='URL'>...</a>
class TBSParser(HTMLParser, object):
    def __init__(self):
        super(TBSParser, self).__init__()
        self.programs = []
        # reading flags
        self.readingProgram = False
        self.readingTitle = False
        self.readingTime = False
        self.amTime = True
        self.midTime = False
        # data buffer
        self.buf = {}
        
    def handle_starttag(self, tag, attr):
        attr = dict(attr)
        if tag == 'tr':
            if 'class' in attr:
                if 'tm-am' in attr['class'].split():
                    self.midTime = False
                    self.amTime = True
                elif 'tm-mid' in attr['class'].split():
                    self.midTime = True
                    self.amTime = False
                else:
                    self.midTime = False
                    self.amTime = False
        elif tag == 'td':
            if 'class' in attr:
                splited = attr['class'].split()
                if 'mon' in splited or 'tue' in splited or 'wed' in splited or 'thu' in splited or 'fri' in splited or 'sat' in splited or 'sun' in splited:
                    self.readingProgram = True
        elif tag == 'a' and self.readingProgram:
            if 'href' in attr:
                if not 'url' in self.buf:
                    self.buf['url'] = 'http://www.tbs.co.jp/tv/' + attr['href']
                    self.buf['date'] = attr['href'][:8]
        elif tag == 'span' and self.readingProgram:
            if 'class' in attr:
                if 'oa' in attr['class'].split():
                    self.readingTime = True
        elif tag == 'strong' and self.readingProgram:
            self.readingTitle = True

    def handle_data(self, data):
        if self.readingTitle:
            self.buf['title'] = data
            self.readingTitle = False
        elif self.readingTime:
            tmp = int(data.replace(':', ''))
            if self.amTime:
                self.buf['time'] = tmp
            elif self.midTime:
                self.buf['time'] = tmp + 2400
            else:
                self.buf['time'] = tmp + 1200

    def handle_endtag(self, tag):
        if self.readingProgram:
            if tag == 'span' and self.readingTime:
                self.readingTime = False
            elif tag == 'td':
                self.programs.append(self.buf)
                self.buf = {}
                self.readingProgram = False

class TBS(Channel):
    def __init__(self):
        super(TBS, self).__init__('http://www.tbs.co.jp/tv/index.html')
        self.programs = []

    def fetch(self, date='today'):
        html = getHTML(self.endpoint)
        parser = TBSParser()
        parser.feed(html)
        self.programs = parser.programs
        
