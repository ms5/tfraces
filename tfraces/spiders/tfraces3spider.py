# tfraces3Spider.py

import string
import re
import urlparse
import logging
from scrapy.log import ScrapyFileLogObserver
from scrapy import log
from scrapy.http.request import Request
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor 
from scrapy.selector import HtmlXPathSelector 
from datetime import date, timedelta
from tfraces.items import tfracesItem

def calc_wintime(text):
	data = re.findall(r'([\d+]+).', text)
	if len(data) < 2:
		return
	elif len(data) == 2:
		wintime = data[0] + '.' + data[1]
		return wintime
	elif len(data) == 3:
		wintime = str((int(data[0]))*60 + (int(data[1]))) + '.' + data[2]
		return wintime
	elif len(data) > 3:
		return
	else:
		return 

def calc_distance(text):
    if text == '':
        return
    else:
        miles = re.findall(r'([\d+]+)m', text)
        furlongs = re.findall(r'([\d+]+)f', text)
        yards = re.findall(r'([\d+]+)yds', text)
        if miles == []:
            ms = 0
        else:
            ms = int(miles[0])
        if furlongs == []:
            fs = 0
        else:
            fs = int(furlongs[0])        
        if yards == []:
            ys = 0
        else:
            ys = float(yards[0])
        distance = round((ms * 8) + fs + ys/220, 2)
        return distance

def translate(text, dic):
    # replaces items from a given list
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

def remove_brackets(somestring):
	somestring = somestring.replace("(", "")
	somestring = somestring.replace(")", "")
	return somestring	

def cleanup(somestring):
	""" removes whitespace, newline, euro, pound sign and bar from string""" 
	pClnUp = re.compile(r'\n|\t|\u20ac|\xa0|\xa3|\|')
	somestring = str(pClnUp.sub('',somestring))
	return somestring

def getuppers(text):
	newtext = ''.join([c for c in text if c.isupper()])
	newtext = newtext.lower()
	return newtext

class ScrapyRaceSpider(CrawlSpider):
	logfile = open('error_log.log', 'a')
	log_observer = ScrapyFileLogObserver(logfile, level=logging.ERROR)
	log_observer.start()
	logfile2 = open('info_log.log', 'a')
	log_observer2 = ScrapyFileLogObserver(logfile2, level=logging.INFO)
	log_observer2.start()
	name = "3tt"
	allowed_domains = ["form.horseracing.betfair.com"]
	newpages = []
	n = 0
	# IMPORTANT - ADJUST this figure for number of days you want scraped
	while n < 184:
		# IMPORTANT - ADJUST the date in date() for the start date to be scraped
		strdate = (date(2007,01,01)+timedelta(n)).strftime('%Y%m%d')
		newpage = 'http://form.horseracing.betfair.com/daypage?date=%s' % strdate
		newpages.append(newpage)
		n += 1
	# produces n x daypages
	start_urls = newpages

	def parse(self,response):
		hxs = HtmlXPathSelector(response) 
		racepath = hxs.select('//div[@data-location="RACING_COUNTRY_GB_IE"]/div[@class="secondary-module-content"]/div[@class="inner-daypage"]/div[@class="course"]/ul/li')
		items = []
		links = []
		item = tfracesItem()
		for eachrace in racepath:
			item = tfracesItem()
			item['racecourse'] = "".join(eachrace.select('.//ancestor::div[@class="course"]/p[@class="course-data"]/a/text()').extract()).strip()
			racedate = response.url[-8:]
			item['racedate'] = racedate
			# timeform racetimes are wrong for british summertime 2007 and 2008 
#			if int(racedate) >= 20070325 and int(racedate) <= 20071027:
#				racetime = "".join(eachrace.select('./a/text()').re(r'\d+')).strip()
#				racetime = str(int(racetime) - 100)
#				racetime = racetime[0:2] + ":" + racetime[2:4]
#				item['racetime'] = racetime
#			else:
			item['racetime'] = "".join(eachrace.select('./a/text()').extract()).strip() 
			racetype = "".join(eachrace.select('./@title').re(r'[A-Z].*\|')).strip()
			typereps = {' |' : '', 'PRO/AM) ' : ''}
			racetype = racetype.encode('utf-8', 'ignore')
			item['racetype'] = translate(racetype, typereps)
			link = "".join(eachrace.select('./a/@href').extract()).strip()
			item['racelink'] = link
			yield Request(urlparse.urljoin(response.url, link), meta={'item':item},callback=self.parse_listing_page)

	#scrape listing page to get content 
	def parse_listing_page(self,response): 
		hxs = HtmlXPathSelector(response) 
		item = response.request.meta['item'] 
		racehdrxpath = hxs.select('//div[@class="content"]/p[@class="clearer race-info"]')
		raceclassxpath = hxs.select('//div[@class="content"]/p[@class="race-description"]')
		raceftrxpath = hxs.select('//div[@class="extra-info"]/p[1]/text()')
		resevenxpath = hxs.select('//table[@class="full-results uk"]/descendant::tr[@class="even"]')
		resoddxpath = hxs.select('//table[@class="full-results uk"]/descendant::tr[@class="odd"]')
		j = 0
		while j < len(racehdrxpath):
			classinfo = "".join(raceclassxpath[j].select('.//text()').re(r'\(\d+\)')).strip()
			classreps = {'(' : '', ')' : ''}
			classinfo = translate(classinfo, classreps)
			if classinfo == "":
				item['raceclass'] = "n/a"
			else:
				item['raceclass'] = classinfo
			# get a list of words
			checkinfo = []
			goinginfo = []
			awgoing = []
			checkinfo = "".join(racehdrxpath[j].select('.//span[1]/text()').extract()).strip()
			# 3330 errors for jul_nov_2013 because going missing from racehdrxpath so this code block sorts that out
			# mainly by reducing the span[x] numbers in the x-path by one
			if "Distance:" in checkinfo:
				item['going'] = "n/a"
				distinfo = "".join(racehdrxpath[j].select('.//span[1]/text()').extract()).strip()
				if "Distance:" in distinfo:
					item['distance'] = calc_distance(cleanup(distinfo.replace("Distance: ", "")).strip())	
				agerinfo = "".join(racehdrxpath[j].select('.//span[2]/text()').extract()).strip()
				if "Age:" in agerinfo:
					item['agerange'] = cleanup(agerinfo.replace("Age: ", "")).strip()
				purseinfo = "".join(racehdrxpath[j].select('.//span[3]/text()').extract()).strip()
				purse = "".join(racehdrxpath[j].select('.//span[3]/text()').re(r'\d+')).strip()
				if "Total prize money: " in purseinfo:
					item['purse'] = purse
				else:
					item['purse'] = "n/a"		
				rnrsinfo = "".join(racehdrxpath[j].select('.//span[4]/text()').extract()).strip()
				if "Race Type:" in rnrsinfo:
					code = cleanup(rnrsinfo.replace("Race Type: ","")).strip()
					codereps = {'National Hunt Flat' : 'NH Flat'}
					code = code.encode('utf-8', 'ignore')
					item['code'] = translate(code, codereps)
				codeinfo = "".join(racehdrxpath[j].select('.//span[5]/text()').extract()).strip()
				if "Race Type:" in codeinfo:
					code = cleanup(codeinfo.replace("Race Type: ","")).strip()
					codereps = {'National Hunt Flat' : 'NH Flat'}
					code = code.encode('utf-8', 'ignore')
					item['code'] = translate(code, codereps)
			elif "Going:" in checkinfo:
				goinginfo = "".join(racehdrxpath[j].select('.//span[1]/text()').re(r'[A-Z]{2,10}.')).replace(";"," ").lower().strip().split(" ")
				distinfo = "".join(racehdrxpath[j].select('.//span[2]/text()').extract()).strip()
				if "Distance:" in distinfo:
					item['distance'] = calc_distance(cleanup(distinfo.replace("Distance: ", "")).strip())	
				agerinfo = "".join(racehdrxpath[j].select('.//span[3]/text()').extract()).strip()
				if "Age:" in agerinfo:
					item['agerange'] = cleanup(agerinfo.replace("Age: ", "")).strip()
				purseinfo = "".join(racehdrxpath[j].select('.//span[4]/text()').extract()).strip()
				purse = "".join(racehdrxpath[j].select('.//span[4]/text()').re(r'\d+')).strip()
				if "Total prize money: " in purseinfo:
					item['purse'] = purse
				else:
					item['purse'] = "n/a"		
				rnrsinfo = "".join(racehdrxpath[j].select('.//span[5]/text()').extract()).strip()
				if "Race Type:" in rnrsinfo:
					code = cleanup(rnrsinfo.replace("Race Type: ","")).strip()
					codereps = {'National Hunt Flat' : 'NH Flat'}
					code = code.encode('utf-8', 'ignore')
					item['code'] = translate(code, codereps)
				codeinfo = "".join(racehdrxpath[j].select('.//span[6]/text()').extract()).strip()
				if "Race Type:" in codeinfo:
					code = cleanup(codeinfo.replace("Race Type: ","")).strip()
					codereps = {'National Hunt Flat' : 'NH Flat'}
					code = code.encode('utf-8', 'ignore')
					item['code'] = translate(code, codereps)
				if 'all-weather' in goinginfo:
					awgoing = goinginfo[:]
					if len(awgoing) == 2:
						item['going'] = awgoing[1]
						item['code'] = "AW"
					elif len(awgoing) == 3:
						item['going'] = awgoing[1] + " to " + awgoing[2]
						item['code'] = "AW"
					else:
						item['going'] = awgoing[1]
						item['code'] = "AW"		
				else:
					if len(goinginfo) == 1:
						item['going'] = goinginfo[0]
					elif len(goinginfo) == 2:
						item['going'] = goinginfo[0] + " to " + goinginfo[1]
					elif len(goinginfo) > 2:
						if goinginfo[0] == goinginfo[1]:
							item['going'] = goinginfo[0]
						elif goinginfo[1] == goinginfo[2]:
							item['going'] = goinginfo[1]  
						else:
							item['going'] = goinginfo[0]
					else:
						item['going'] = goinginfo[0]
			j = j + 1
			k = 0
			while k < len(raceftrxpath):
				item['runners'] = "".join(raceftrxpath[k].extract()).strip().split(" Ran, Winning Time: ")[0]
				item['wintime'] = calc_wintime("".join(raceftrxpath[k].extract()).strip().split(" Ran, Winning Time: ")[1])
				k = k + 1
				totdistbtn = 0	
				n = 0
				z = len(resevenxpath) + len(resoddxpath)
				while n < z:
					if n % 2 == 0:
						# n is even, will have odd number finishers 1st, 3rd, 5th etc
						num = (n/2)
						restable = resevenxpath.select('../tr[@class="even"]')[num]
						position = "".join(restable.select('./td[1]/span[1]/text()').extract())
						inrun_reps = {"/" : "", "-" : ""}
						if position == '1':
 							item['win'] = 1
							hi_ir = "".join(restable.select('./td[8]/span[1]/text()').extract())
							item['hi_ir'] = translate(hi_ir, inrun_reps).strip()
							item['lo_ir'] = "-"
						else:
							item['win'] = 0
							lo_ir = "".join(restable.select('./td[8]/span[1]/text()').extract())
							item['lo_ir'] = translate(lo_ir, inrun_reps).strip()
							item['hi_ir'] = "-"
						item['position'] = position
						item['draw'] = remove_brackets("".join(restable.select('./td[1]/span[2]/text()').extract()))
						distbtn = "".join(restable.select('./td[2]/text()').extract())
						distreps = {'\xc2' : '', '\xbd' : '.5', '\xbc' : '.25', '\xbe' : '.75', 'dh' : '0', 'dht' : '0',  'ns' : '0.05', 'nse' : '0.05', 's.h' : '0.1', 'sh' : '0.1', 'hd' : '0.2', 'snk' : '0.25', 'nk' : '0.3', 'ds' : '30', 'dist' : '30'}
						distbtn = distbtn.encode('utf-8', 'ignore')
						if distbtn == "":
							if position[0].isdigit:
								totdistbtn = totdistbtn
							else:
								totdistbtn = "-"
						else:
							tranny = translate(distbtn, distreps)
							totdistbtn += float(tranny)
						item['distbtn'] = totdistbtn
						item['horse'] = "".join(restable.select('./td[3]/a/text()').extract())
						item['age'] = cleanup("".join(restable.select('./td[4]/text()').extract()).strip())		
						weight = "".join(restable.select('./td[5]/span[1]/text()').extract()).split("-")
						stones = int(weight[0]) * 14
						if len(weight) > 1:
							pounds = int(weight[1])
							item['weight'] = stones + pounds
						else:
							pounds = 0
							item['weight'] = stones + pounds	
						item['offrating'] = remove_brackets("".join(restable.select('./td[5]/span[2]/text()').extract()))
						item['equipment'] = cleanup("".join(restable.select('./td[6]/text()').extract()).strip())
						item['jockey'] = "".join(restable.select('./td[7]/a[1]/text()').extract())
						item['allowance'] = remove_brackets("".join(restable.select('./td[7]/sup/text()').extract()))
						trainer = "".join(restable.select('./td[7]/a[2]/text()').extract())
						trainer_reps = {"," : ""}
						item['trainer'] = translate(trainer, trainer_reps).strip()
						bsp = "".join(restable.select('./td[9]/span[1]/text()').extract())
						isp = "".join(restable.select('./td[9]/span[2]/text()').extract()) 
						perc = "".join(restable.select('./td[9]/span[3]/text()').extract()) 
						place = "".join(restable.select('./td[10]/text()').extract()) 	
						item['bsp'] = translate(bsp, inrun_reps).strip()
						item['isp'] = translate(isp, inrun_reps).strip()
						perc_reps = {"(" : "", ")" : "", "," : ""}
						if bsp == "-":
							item['perc'] = ""
						else:
							item['perc'] = translate(perc, perc_reps).strip()
						item['place'] = translate(place, inrun_reps).strip()
						item['date_horse'] = item['racedate'] + item['horse']
						yield item
						n += 1
					else:
						# n is odd, will have 2nd, 4th, 6th etc
						num = (n-1)/2
						restable = resoddxpath.select('../tr[@class="odd"]')[num]
						position = "".join(restable.select('./td[1]/span[1]/text()').extract())
						inrun_reps = {"/" : "", "-" : ""} 	
						if position == '1':
 							item['win'] = 1
							hi_ir = "".join(restable.select('./td[8]/span[1]/text()').extract())
							item['hi_ir'] = translate(hi_ir, inrun_reps).strip()
							item['lo_ir'] = "-"
						else:
							item['win'] = 0
							lo_ir = "".join(restable.select('./td[8]/span[1]/text()').extract())
							item['lo_ir'] = translate(lo_ir, inrun_reps).strip()
							item['hi_ir'] = "-"
						item['position'] = position
						item['draw'] = remove_brackets("".join(restable.select('./td[1]/span[2]/text()').extract()))
						distbtn = "".join(restable.select('./td[2]/text()').extract())
						distreps = {'\xc2' : '', '\xbd' : '.5', '\xbc' : '.25', '\xbe' : '.75', 'dh' : '0', 'dht' : '0', 'ns' : '0.05', 'nse' : '0.05', 's.h' : '0.1', 'sh' : '0.1', 'hd' : '0.2', 'snk' : '0.25', 'nk' : '0.3', 'ds' : '30', 'dist' : '30'}
						distbtn = distbtn.encode('utf-8', 'ignore')
						if distbtn == "":
							if position[0].isdigit():
								totdistbtn += 0
							else:
								totdistbtn = "-"
						else:
							tranny = translate(distbtn, distreps)
							totdistbtn += float(tranny)
						item['distbtn'] = totdistbtn
						item['horse'] = "".join(restable.select('./td[3]/a/text()').extract())
						item['age'] = cleanup("".join(restable.select('./td[4]/text()').extract()).strip())		
						weight = "".join(restable.select('./td[5]/span[1]/text()').extract()).split("-")
						stones = int(weight[0]) * 14
						if len(weight) > 1:
							pounds = int(weight[1])
							item['weight'] = stones + pounds
						else:
							pounds = 0
							item['weight'] = stones + pounds
						item['offrating'] = remove_brackets("".join(restable.select('./td[5]/span[2]/text()').extract()))
						item['equipment'] = cleanup("".join(restable.select('./td[6]/text()').extract()).strip())
						item['jockey'] = "".join(restable.select('./td[7]/a[1]/text()').extract())
						item['allowance'] = remove_brackets("".join(restable.select('./td[7]/sup/text()').extract()))
						trainer = "".join(restable.select('./td[7]/a[2]/text()').extract())
						trainer_reps = {"," : ""}
						item['trainer'] = translate(trainer, trainer_reps).strip()
						bsp = "".join(restable.select('./td[9]/span[1]/text()').extract())
						isp = "".join(restable.select('./td[9]/span[2]/text()').extract()) 
						perc = "".join(restable.select('./td[9]/span[3]/text()').extract()) 
						place = "".join(restable.select('./td[10]/text()').extract()) 	
						item['bsp'] = translate(bsp, inrun_reps).strip()
						item['isp'] = translate(isp, inrun_reps).strip()
						perc_reps = {"(" : "", ")" : "", "," : ""}
						if bsp == "-":
							item['perc'] = ""
						else:
							item['perc'] = translate(perc, perc_reps).strip()
						item['place'] = translate(place, inrun_reps).strip()
						item['date_horse'] = item['racedate'] + item['horse']
						yield item
						n += 1  			

					
