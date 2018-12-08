# -*- coding: utf-8 -*-
import channels
import datetime
from Tkinter import *

wcell = 300
hcell = 30

chs = {'TVTokyo': channels.TVTokyo(), 'TokyoMX': channels.TokyoMX(), 'TBS': channels.TBS()}

width = wcell * len(chs) + 30
height = hcell * 27

root = Tk()
root.title(u'tvschedule')
root.geometry(str(width) + 'x' + str(height))

for hour in range(4, 30):
    handle = Label(text=unicode(hour))
    handle.place(x = 0, y = (hour - 3) * hcell)

i = 0
for chname, ch in chs.items():
    handle = Label(text=chname)
    handle.place(x = 30 + i * wcell, y = 0)
    # fetch programs
    ch.fetch()
    print('{}: fetch completed'.format(chname))
    for program in ch.programs:
        if program['date'] != datetime.date.today().strftime('%Y%m%d'):
            continue
        handle = Label(text=program['title'], font=('', 10))
        h = program['time'] / 100
        m = program['time'] % 100
        handle.place(x = 30 + i * wcell, y = hcell * (h - 3 + m / 60.0))
    i = i + 1
    
root.mainloop()
