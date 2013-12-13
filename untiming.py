#!/usr/bin/env python

"""
    Untiming ver 0.1 - An automatic time tracker
    Copyright (C) 2013  Mohammad A.Raji <moa@dragonfli.es>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import gtk
import sys
import wnck
import glib
import datetime
import logging

script_path = os.path.realpath(__file__)
os.chdir(script_path[:script_path.rfind("/")])

class Untiming(object):
    TIMEFORMAT = "%a, %d %b %Y %H:%M:%S"
    LOG_FILENAME = "untiming.log"
    TEMPLATE_FILENAME = "untiming.tpl.html"
    REPORT_FILENAME = "untiming_report.html"

    def __init__(self):
        #Setup the logger
        self.log = logging.getLogger()
        ch = logging.StreamHandler()
        fh = logging.FileHandler(Untiming.LOG_FILENAME)
        self.log.addHandler(ch)
        self.log.addHandler(fh)
        fmt = logging.Formatter("%(message)s")
        ch.setFormatter(fmt)
        fh.setFormatter(fmt)
        self.log.setLevel(logging.INFO)
        
        self.lastTitleWasIdle = False

    def run(self):
        self.title = None
        glib.timeout_add(100, self.printInfo)

    def getTitle(self):
        return wnck.screen_get_default().get_active_window().get_name()

    def printInfo(self):
        try:
            title = self.getTitle()
            if self.isIdle() and self.lastTitleWasIdle == False:
                now = datetime.datetime.now()
                now_str = now.strftime(Untiming.TIMEFORMAT)
                self.log.info(now_str + "\t " + "[Idle]")
                self.lastTitleWasIdle = True
                
            elif self.isIdle() == False and (self.title != title or self.lastTitleWasIdle == True):
                self.title  = title
                now = datetime.datetime.now()
                now_str = now.strftime(Untiming.TIMEFORMAT)
                self.log.info(now_str + "\t " + self.title)
                self.lastTitleWasIdle = False
        except AttributeError:
            pass
        return True
    
    def isIdle(self):
        if self.getIdleTime() / 60000 > 3:
            return True
        else:
            return False
        
    def getIdleTime(self):
        return int(os.popen("xprintidle").read())

    def report(self, word="", day=-1, show=True):
        log_file = file(Untiming.LOG_FILENAME)
        log_file_lines = log_file.readlines()
        total_time = datetime.timedelta()
        today = datetime.date.today()
        
        for idx, line in enumerate(log_file_lines):
            if line.lower().find(word) != -1 or word == "":
                info = line.split('\t')
                start = datetime.datetime.strptime(info[0], Untiming.TIMEFORMAT)
                if (day != -1 and start.date().day != day):
                    continue
                
                if (idx < len(log_file_lines) - 1):
                    next_line_info = log_file_lines[idx + 1].split('\t')
                    end = datetime.datetime.strptime(next_line_info[0], Untiming.TIMEFORMAT)
                else:
                    break

                total_time += end - start
                #if end - start > datetime.timedelta(minutes=1):
                if show:
                    print info[0] + " - " + str(end - start) + "\t" + info[1]

        if show:
            print "Total duration: " + str(total_time)
        return total_time

    def generateHTMLGraph(self, words):
        template_f = file(Untiming.TEMPLATE_FILENAME)
        tpl = template_f.read()
        tpl = tpl.replace("{{MONTH}}", datetime.datetime.now().strftime("%B"))
        tpl = tpl.replace("{{YEAR}}", datetime.datetime.now().strftime("%Y"));
        
        today = datetime.date.today().day
        data = ""
        data_list = "["
        wl = len(words)
        for idx, word in enumerate(words):
            data += "var s" + str(idx+1) + "=["
            data_list += "s" + str(idx+1)
            if (idx != wl - 1):
                data_list += ", "
            for day in range(1, today + 1):
                data += str(self.report(word, day, False).seconds / 60)
                if day != today:
                    data += ", "
            data += "];"

        tpl = tpl.replace("{{DATA}}", data);
        data_list += "]"
        tpl = tpl.replace("{{DATA_LIST}}", data_list)

        labels = ""
        for idx, label in enumerate(words):
            labels += "{label:'" + label + "'}"
            if idx != wl - 1:
                labels += ","

        tpl = tpl.replace("{{LABELS}}", labels)
        tpl = tpl.replace("{{TICKS}}", str(range(1, today + 1)))
        tpl = tpl.replace("{{SYSNAME}}", os.uname()[1]);
        tpl = tpl.replace("{{TIME}}", datetime.datetime.now().strftime(Untiming.TIMEFORMAT))
        
        report = file(Untiming.REPORT_FILENAME, 'w')
        report.write(tpl)
        
    def cleanLog(self):
        log_file = file(Untiming.LOG_FILENAME, 'r')
        log_file_lines = log_file.readlines()
        now = datetime.datetime.now()
        this_month_stamp = now.strftime("%b %Y")
        new_log_lines = ""
        for line in log_file_lines:
            if line.find(this_month_stamp) != -1:
                new_log_lines += line
        
        log_file.close()
        log_file = file(Untiming.LOG_FILENAME, 'w')
        log_file.writelines(new_log_lines)

if __name__ == '__main__':
    unt = Untiming()
    if len(sys.argv) > 1:
        if sys.argv[1] == "report":
            if len(sys.argv) > 2:
                unt.report(sys.argv[2])
            else:
                unt.report()
        elif sys.argv[1] == "graph":
            unt.generateHTMLGraph(sys.argv[2:])
    else:
        unt.cleanLog()
        unt.run()
        gtk.main()

