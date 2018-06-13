#!/usr/bin/env python3

import bs4
import pprint
import iaafcc
import datetime
import requests
import pywikibot
from pywikibot import pagegenerators

session = requests.Session()
session.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0' }

PROD = 0

Q_BOLT = 'Q165437'
Q_IAAF = [ 'Q1158', '' ][PROD]
Q_RACERES = [ 'Q54959061', 'Q166169' ][PROD]
Q_SECONDS = [ 'Q11574', 'Q166170' ][PROD]
P_IAAFID = [ 'P1146', 'P76442' ][PROD]
P_RESULTS = [ 'P2501', 'P76745' ][PROD]
P_SPORTDISC = [ 'P2416', 'P76746', 'P76749' ][PROD]
P_RACETIME = [ 'P2781', 'P27728' ][PROD]
P_POINTINTIME = [ 'P585', 'P66' ][PROD]
P_STATEDIN = [ 'P248', '' ][PROD]
P_RETRIEVED = [ 'P813', '' ][PROD]
P_REFURL = [ 'P854', '' ][PROD]

site = pywikibot.Site([ 'wikidata', 'test' ][PROD], 'wikidata')

repo = site.data_repository()
item = pywikibot.ItemPage(repo, Q_BOLT)

data = {
    'labels': { 'en': 'Usain Bolt' },
    'descriptions': { 'en': 'Jamaican sprinter' },
    'aliases': { 'en': [ 'Lightning Bolt' ] },
    'sitelinks': [ { 'site': 'enwiki', 'title': 'Usain Bolt' } ],
}
#item.editEntity(data, summary = 'edited data')

iaafe2wd = {
    '60 Metres': 'Q246681',
    '100 Metres': 'Q164761',
    '150 Metres': 'Q2807981',
    '200 Metres': 'Q211155',
    '300 Metres': 'Q2402434',
    '400 Metres': 'Q334734',
    '500 Metres': 'Q2817139',
    '600 Metres': 'Q2817913',
    '800 Metres': 'Q271008',
    '1500 Metres': 'Q191691',
    '4x100 Metres Relay': 'Q230061',
    '4x400 Metres Relay': 'Q230057',
}

wdq = '''SELECT ?item WHERE {{
  ?item wdt:{} ?value .
}}'''.format(P_IAAFID)

if PROD != -1:
    generator = site.preloadpages(
        pagegenerators.WikidataSPARQLPageGenerator(wdq, site),
        pageprops = True
    )
else:
    generator = [ item ]

for page in generator:
    itemd = page.get()
    pprint.pprint(itemd)

    claim = pywikibot.Claim(repo, P_RESULTS)
    
    iaafid = itemd['claims'][P_IAAFID][0].getTarget()
    iaafurl = 'https://www.iaaf.org/athletes/athlete=' + iaafid
    print(iaafurl)
    iaafs = bs4.BeautifulSoup(session.get(iaafurl).text, 'html.parser')
    aaid = iaafs.find('div', { 'data-aaid': True })['data-aaid']
    years = [ op['value'] for op in iaafs.find('select', { 'name': 'resultsByYear' }).find_all('option') ]
    for y in years:
        apiurl = 'https://www.iaaf.org/data/GetCompetitorResultsByYearHtml?resultsByYear={}&resultsByYearOrderBy=date&aaId={}'.format(y, aaid)
        ysoup = bs4.BeautifulSoup(session.get(apiurl).text, 'html.parser')
        perfs = ysoup.find('tbody').find_all('tr')
        for p in perfs:
            print(p.text)
            claim.setTarget(pywikibot.ItemPage(repo, Q_RACERES))
            page.addClaim(claim, summary = 'Adding {} race result'.format(y))
            # parsing
            pdate = p.find('td', { 'data-th': 'Date' }).text.strip()
            pdate = datetime.datetime.strptime(pdate.title(), '%d %b %Y')
            pcomp = p.find('td', { 'data-th': 'Competition' }).text.strip()
            pevnt = p.find('td', { 'data-th': 'Event' }).text.strip()
            pcnt = iaafcc.iaafcc[p.find('td', { 'data-th': 'Cnt.' }).text.strip()]
            pcat = p.find('td', { 'data-th': 'Cat' }).text.strip()
            prace = p.find('td', { 'data-th': 'Race' }).text.strip()
            pplace = p.find('td', { 'data-th': 'Pl.' }).text.strip()
            pres = p.find('td', { 'data-th': 'Result' }).text.strip()
            try:
                pres = float(pres)
            except:
                pres = None
            pwind = p.find('td', { 'data-th': 'Wind' }).text.strip()
            # add qualifiers
            quals = []
            if pres:
                presqualifier = pywikibot.Claim(repo, P_RACETIME)
                presqualifier.setTarget(pywikibot.WbQuantity(pres, unit = pywikibot.ItemPage(repo, Q_SECONDS), error = 0.01, site = site))
                quals.append(presqualifier)
            if pdate:
                datequalifier = pywikibot.Claim(repo, P_POINTINTIME)
                datequalifier.setTarget(pywikibot.WbTime(year = pdate.year, month = pdate.month, day = pdate.day))
                quals.append(datequalifier)
            if pevnt:
                evntqualifier = pywikibot.Claim(repo, P_SPORTDISC)
                if PROD == -1:
                    evntqualifier.setTarget(pevnt)
                else:
                    qevnt = iaafe2wd[pevnt.replace(' Indoor', '')]
                    evntqualifier.setTarget(pywikibot.ItemPage(repo, qevnt))
                quals.append(evntqualifier)
            claim.addQualifiers(quals, summary = 'Adding race qualifiers for {} on {}'.format(pevnt, pdate.strptime('%Y-%m-%d')))
            # add sources
            now = datetime.datetime.now()
            retrieved = pywikibot.Claim(repo, P_RETRIEVED)
            retrieved.setTarget(pywikibot.WbTime(year = now.year, month = now.month, day = now.day))
            statedin = pywikibot.Claim(repo, P_STATEDIN)
            statedin.setTarget(pywikibot.ItemPage(repo, Q_IAAF))
            refurl = pywikibot.Claim(repo, P_REFURL)
            refurl.setTarget(apiurl)
            claim.addSources([ statedin, refurl, retrieved ], summary = 'Adding sources for race from {}'.format(refurl))
