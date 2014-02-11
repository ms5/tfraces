# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class tfracesItem(Item):
	# define the fields for your item here like:
	# name = Field()
	racelink = Field()
	racedate = Field()
	racetime = Field()
	racecourse = Field()
	racetype = Field()
	raceclass = Field()
	going = Field()
	distance = Field()
	agerange = Field()
	purse = Field()
	code = Field()
	runners = Field()
	wintime = Field()
	racelink = Field()
	win = Field()
	position = Field()
	draw = Field()
	distbtn = Field()
	horse = Field()
	age = Field()
	weight = Field()
	offrating = Field()
	equipment = Field()
	jockey = Field()
	allowance = Field()
	trainer = Field()
	hi_ir = Field()
	lo_ir = Field()	
	bsp = Field()	
	isp = Field()
	perc = Field()
	place = Field()
	date_horse = Field()
	form = Field()
	dslr = Field()
	comment = Field()
	pass
