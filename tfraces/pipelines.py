# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv

from tfraces.items import tfracesItem

class tfracesPipeline(object):

	def __init__(self):
		self.tfracesCsv = csv.writer(open('tf_races_2007.csv', 'wb'))
		self.tfracesCsv.writerow(['racelink', 'racedate', 'racetime', 'racecourse', 'racetype', 'raceclass', 'going', 'distance', 'agerange', 'purse', 'runners', 'code', 'wintime', 'win', 'position', 'draw', 'distbtn', 'horse', 'age', 'weight', 'offrating', 'equipment', 'jockey', 'allowance', 'trainer', 'hi_ir', 'lo_ir', 'bsp', 'isp', 'perc', 'place','datehorse'])
# 'form', 'dslr', 'comment'])
    
	def process_item(self, item, spider):	
	    if isinstance(item, tfracesItem):
        	self.tfracesCsv.writerow([item['racelink'], item['racedate'],item['racetime'],item['racecourse'],item['racetype'],item['raceclass'],item['going'], item['distance'],item['agerange'],item['purse'],item['runners'],item['code'],item['wintime'],item['win'],item['position'],item['draw'],item['distbtn'],item['horse'], item['age'],item['weight'], item['offrating'],item['equipment'],item['jockey'],item['allowance'],item['trainer'],item['hi_ir'],item['lo_ir'],item['bsp'],item['isp'],item['perc'],item['place'],item['date_horse']])
# item['form'],item['dslr'],item['comment']])
		return item
