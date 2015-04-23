Untiming
========

A fully automatic time tracker with python that logs the title of focused windows.

Untiming can log the title of the applications that you've been working on and provide you with query based reports (in text and bar charts). Some applications put active tab names in their titles too (like browsers, eclipse, ...) so you can even query Untiming for information about the tabs (e.g. How many hours did I spend in GMail today?).

Note: Untiming automatically detects when you are not using your system (idle time) with the help of **xprintidle**.

Requirements
------------
1. A Linux distro
1. xprintidle

Usage
------------
Just run it with python:

    python untiming.py
    
To get a report run:

    python untiming.py report <list of keywords>
    
For example this will give you the usage reports for the gmail tab in your browser, eclipse and firefox:

    python untiming.py report firefox eclipse gmail
    
To generate this month's chart run (an HTML chart will be generated with the name of **untiming_report.html**):

    python untiming.py graph <list of keywords>
