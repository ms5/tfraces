# Scrapy settings for tfraces project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'tfraces'

SPIDER_MODULES = ['tfraces.spiders']
NEWSPIDER_MODULE = 'tfraces.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'tfraces (+http://www.yourdomain.com)'

ITEM_PIPELINES = ['tfraces.pipelines.tfracesPipeline']
