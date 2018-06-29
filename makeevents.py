#!/usr/bin/env python3

import bs4
import csv
import time
import pprint
import iaafcc
import datetime
import requests
import pywikibot
from pywikibot import pagegenerators

session = requests.Session()
session.headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36' }

Q_METER = 'Q11573'
Q_MPS = 'Q182429'
Q_IAAF = 'Q54960205'
Q_RACERES = 'Q54959061' # deprecated
Q_SECONDS = 'Q11574'
Q_INDOORS = 'Q10235779'
Q_ATHLETICSMEETING = 'Q11783626'
Q_ATHLETICS = 'Q542'
Q_SPORTCLASS = 'Q1744559'

Q_FEMALE = 'Q6581072'
Q_MALE = 'Q6581097'

P_IAAFID = 'P1146'
P_RESULTS = 'P1344' # 2501 "results" -> 1344 "participant of"
P_SPORTDISC = 'P2416'
P_POINTINTIME = 'P585'
P_STATEDIN = 'P248'
P_RETRIEVED = 'P813'
P_REFURL = 'P854'
P_WIND = 'P5065'
P_SPORT = 'P641'
P_RANK = 'P1352'
P_COMPETITION = 'P5249'
P_COUNTRY = 'P17'
P_STAGEREACHED = 'P2443'
P_STATEDAS = 'P1932'
P_INSTANCEOF = 'P31'
P_HASPART = 'P527'
P_PARTOF = 'P361'
P_OBJECTHASROLE = 'P3831'
P_GENDER = 'P21'
P_COMPCLASS = 'P2094'
P_PARTICIPANT = 'P710'

P_RACETIME = 'P2781'
P_POINTS = 'P1358'
P_DISTANCE = 'P2043'

site = pywikibot.Site('wikidata', 'wikidata')

repo = site.data_repository()

evnts = {
    '50 Metres': 'Q240356',
    '50 Metres Hurdles': 'Q4639907',
    '55 Metres': 'Q4640627',
    '55 Metres Hurdles': 'Q4640620',
    '60 Metres': 'Q246681',
    '60 Metres Hurdles': 'Q1026754',
    '100 Metres': 'Q164761',
    '100 Metres Hurdles': 'Q164731',
    '110 Metres Hurdles': 'Q170004',
    '150 Metres': 'Q2807981',
    '200 Metres': 'Q211155',
    '300 Metres': 'Q2402434',
    '400 Metres': 'Q334734',
    '400 Metres Hurdles': 'Q231419',
    '500 Metres': 'Q2817139',
    '600 Metres': 'Q2817913',
    '800 Metres': 'Q271008',
    '1000 Metres': 'Q1629556',
    '1500 Metres': 'Q191691',
    'One Mile': 'Q943635',
    '2000 Metres': 'Q211164',
    '2000 Metres Steeplechase': 'Q30588012',
    '3000 Metres': 'Q223779',
    '3000 Metres Steeplechase': 'Q10437559',
    '3000 Metres Race Walk': 'Q30588450',
    'Two Miles': 'Q2815830',
    '5000 Metres': 'Q240500',
    '5000 Metres Race Walk': 'Q11187928',
    '10,000 Metres': 'Q163892',
    '10,000 Metres Race Walk': 'Q28444668',
    '10 Kilometres': 'Q2774730',
    '10 Kilometres Race Walk': 'Q26844349',
    '15 Kilometres': 'Q19767716',
    '10 Miles': 'Q2767252',
    '20 Kilometres': 'Q19827858',
    '20 Kilometres Race Walk': 'Q210673',
    'Half Marathon': 'Q215677',
    '30 Kilometres': 'Q54964282',
    '35 Kilometres Race Walk': 'Q55234451',
    'Marathon': 'Q40244',
    '50 Kilometres': 'Q2817174',
    '50 Kilometres Race Walk': 'Q240387',
    '100 Kilometres': 'Q1847570',
    'Cross Country': 'Q500050', # not real
    'Short Race': 'Q55247078',
    'Long Race': 'Q55247140',
    'U20 Race': 'Q55247191',
    'Senior Race': 'Q55246937',
    '4x100 Metres Relay': 'Q230061',
    '4x200 Metres Relay': 'Q3114131',
    'Medley Relay': 'Q2532187', # swedish
    'Sprint Medley Relay': 'Q7581309',
    '4x400 Metres Relay': 'Q230057',
    '4x800 Metres Relay': 'Q744307',
    'Distance Medley Relay': 'Q5282867',
    '4x1500 Metres Relay': 'Q2076688',
    'Pole Vault': 'Q185027',
    'Javelin Throw': 'Q178108',
    'Hammer Throw': 'Q184865',
    'High Jump': 'Q165704',
    'Long Jump': 'Q170737',
    'Triple Jump': 'Q187204',
    'Shot Put': 'Q180935',
    'Discus Throw': 'Q182570',
    '35libs Weight': 'Q259509',
    'Decathlon': 'Q184654',
    'Heptathlon': 'Q243264',
    'Pentathlon': 'Q24688986',
}

for i, k in enumerate(evnts.keys()):
    evp = pywikibot.ItemPage(repo, evnts[k])
    evpi = evp.get()
    label = evpi['labels']['en']
    gens = []
    for g in [ 'men\'s', 'women\'s' ]:
        newlabel = '{} {}'.format(g, label)
        nevp = pywikibot.ItemPage(site)
        nevp.editEntity({
            'labels': { 'en': newlabel },
            'descriptions': { 'en': 'gendered athletics discipline competition class' },
        }, summary = 'Creating athletics competition class as per dicussion at [[Property talk:P2416#sport competition (Q13406554) type constraint?]]')
        instanceclaim = pywikibot.Claim(repo, P_INSTANCEOF)
        instanceclaim.setTarget(pywikibot.ItemPage(repo, Q_SPORTCLASS))
        sportclaim = pywikibot.Claim(repo, P_SPORT)
        sportclaim.setTarget(pywikibot.ItemPage(repo, Q_ATHLETICS))
        compclass = pywikibot.Claim(repo, P_COMPCLASS)
        compclass.setTarget(pywikibot.ItemPage(repo, Q_FEMALE if 'women' in g else Q_MALE))
        compclass2 = pywikibot.Claim(repo, P_COMPCLASS)
        compclass2.setTarget(pywikibot.ItemPage(repo, evnts[k]))
        nevp.addClaim(instanceclaim, summary = 'adding instance of sport classification')
        nevp.addClaim(sportclaim, summary = 'adding sport of athletics')
        nevp.addClaim(compclass, summary = 'adding competition class gender')
        nevp.addClaim(compclass2, summary = 'adding competition class event')
        gens.append(nevp.getID())
    print('    \'{}\': ( \'{}\', \'{}\', \'{}\' ),'.format(k, evnts[k], gens[0], gens[1]))
