#!/usr/bin/env python3

import pywikibot
import pprint

site = pywikibot.Site('en', 'wikipedia')  # any site will work, this is just an example

for cnt in open('/home/habs/wiki/countries/countries.txt').read().split('\n'):
    print(cnt, end = ',')
    page = pywikibot.Page(site, cnt)
    item = pywikibot.ItemPage.fromPage(page)
    print(item.id)
