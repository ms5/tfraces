# readme.txt

# 10.02.14
# author: hullboy73

This is a little shoddy in places and forgive my novice hacking but it just about works.
I'm writing these notes briefly to aid any programmers and/or form students coming across this.  

What does this program do?
It scrapes the basic horse racing results data from Timeform at http://form.horseracing.betfair.com/

Requirements:
Python (Python is an interactive, object-oriented, extensible programming language - see http://python.org/)
Scrapy (Scrapy is a fast high-level screen scraping and web crawling framework - see http://scrapy.org/)

Example:
I'll try to upload jan_jun_2007.csv.
If the program is working smoothly it should scrape and create something like this file.
You can hopefully open this .csv file in a spreadsheet (Excel, Calc or similar).

Program:
The Scrapy framework has a structured format which generally consists of the following files:

tfraces (directory)
	|
    scrapy.cfg
	|
	items.py -- pipelines.py -- settings.py
			|
		the spider (in this case it's called tfraces3spider.py).

How to get this to work:
Install Python
Install Scrapy

A couple of adjustments to make in tfraces3spider.py. See the notes at lines 86-90 and make adjustments there
as required (it just depends what dates you want to scrape). 

Then go into the top level directory (tfraces) and from the command line run:

scrapy crawl 3tt

and the program should start scraping. That's the basic idea. Have a play.

