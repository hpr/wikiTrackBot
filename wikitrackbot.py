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

PROD = 0

Q_METER = 'Q11573'
Q_MPS = 'Q182429'
Q_IAAF = [ 'Q54960205', '' ][PROD]
Q_RACERES = [ 'Q54959061', 'Q166169' ][PROD] # deprecated
Q_SECONDS = [ 'Q11574', 'Q166170' ][PROD]
Q_INDOORS = 'Q10235779'
Q_ATHLETICSMEETING = 'Q11783626'

Q_FEMALE = 'Q6581072'
Q_MALE = 'Q6581097'

P_IAAFID = [ 'P1146', 'P76442' ][PROD]
P_RESULTS = [ 'P1344', 'P76745' ][PROD] # 2501 "results" -> 1344 "participant of"
P_SPORTDISC = [ 'P2416', 'P76746', 'P76749' ][PROD]
P_POINTINTIME = [ 'P585', 'P66' ][PROD]
P_STATEDIN = [ 'P248', '' ][PROD]
P_RETRIEVED = [ 'P813', '' ][PROD]
P_REFURL = [ 'P854', '' ][PROD]
P_WIND = 'P5065'
P_SPORT = 'P641'
P_RANK = 'P1352'
P_COMPETITION = 'P5249'
P_COUNTRY = 'P17'
P_STAGEREACHED = 'P2443'
P_COMPCLASS = 'P2094'
P_STATEDAS = 'P1932'
P_INSTANCEOF = 'P31'
P_HASPART = 'P527'
P_PARTOF = 'P361'
P_OBJECTHASROLE = 'P3831'
P_GENDER = 'P21'
P_COMPCLASS = 'P2094'
P_PARTICIPANT = 'P710'

P_RACETIME = [ 'P2781', 'P27728' ][PROD]
P_POINTS = 'P1358'
P_DISTANCE = 'P2043'

site = pywikibot.Site([ 'wikidata', 'test' ][PROD], 'wikidata')

repo = site.data_repository()

data = {
    'labels': { 'en': 'Usain Bolt' },
    'descriptions': { 'en': 'Jamaican sprinter' },
    'aliases': { 'en': [ 'Lightning Bolt' ] },
    'sitelinks': [ { 'site': 'enwiki', 'title': 'Usain Bolt' } ],
}
#item.editEntity(data, summary = 'edited data')

rnd2wd = {
    'F': 'Q1366722',
    'F1': 'Q54967487',
    'F2': 'Q54967487',
    'F3': 'Q54967487',
    'F4': 'Q54967487',
    'F5': 'Q54967487',
    'F6': 'Q54967487',
    'F7': 'Q54967487',
    'F8': 'Q54967487',
    'F9': 'Q54967487',
    'F10': 'Q54967487',
    'H': 'Q2122052',
    'H1': 'Q2122052',
    'H2': 'Q2122052',
    'H3': 'Q2122052',
    'H4': 'Q2122052',
    'H5': 'Q2122052',
    'H6': 'Q2122052',
    'H7': 'Q2122052',
    'H8': 'Q2122052',
    'H9': 'Q2122052',
    'H10': 'Q2122052',
    'SF': 'Q599999',
    'SF1': 'Q599999',
    'SF2': 'Q599999',
    'SF3': 'Q599999',
    'SF4': 'Q599999',
    'SF5': 'Q599999',
    'SF6': 'Q599999',
    'SF7': 'Q599999',
    'SF8': 'Q599999',
    'SF9': 'Q599999',
    'SF10': 'Q599999',
}

perf2wd = {
    'DNF': 'Q1210380',
    'NM': 'Q54967576',
    'NH': 'Q54967576',
    'ND': 'Q54967576',
}

iaafc2wd = {
    'Kingston Jamaican Ch.': 'Q55029485',
    'Ostrava Golden Spike': 'Q178299',
    'London Müller Anniversary Games': 'Q791183',
    'London Sainsbury\'s Anniversary Games': 'Q791183',
    'London Aviva Grand Prix': 'Q791183',
    'London Norwich Union Super Grand Prix': 'Q791183',
    'Crystal Palace Norwich Union London Grand Prix': 'Q791183',
    'Crystal Palace Norwich Union LONDON Grand Prix': 'Q791183',
    'Melbourne NITRO Athletics': 'Q29025671',
    'Monaco Herculis': 'Q1250640',
    'London IAAF World Championships in Athletics': 'Q175508',
    'Nassau IAAF World Relays': 'Q926006',
    'New York adidas Grand Prix': 'Q240958',
    'New York Reebok Grand Prix': 'Q240958',
    'Beijing IAAF World Championships': 'Q1026555',
    'Glasgow Commonwealth Games': 'Q1116999',
    'Roma Golden Gala': 'Q225463',
    'Roma Compeed Golden Gala': 'Q225463',
    'Oslo ExxonMobil Bislett Games': 'Q866398',
    'Paris Meeting AREVA': 'Q983696',
    'Paris-St-Denis Meeting Areva': 'Q983696',
    'Moskva IAAF World Championships': 'Q842232',
    'Zürich Weltklasse': 'Q661729',
    'Bruxelles Memorial Van Damme': 'Q1426540',
    'Lausanne Athletissima': 'Q665517',
    'Stockholm DN Galan': 'Q1154703',
    'Daegu IAAF World Championships': 'Q208675',
    'Zagreb IAAF World Challenge': 'Q954718',
    'Zagreb 2006': 'Q954718',
    'Philadelphia Penn Relays': 'Q3374756',
    'Philadelphia Penn Relays OD': 'Q3374756',
    'Shanghai IAAF Diamond League Meeting': 'Q942004',
    'Berlin IAAF World Championships': 'Q152772',
    'Paris-St-Denis IAAF World Championships': 'Q263403',
    'Thessaloniki IAAF/VTB Bank World Athletics Final': 'Q1471412',
    'Stuttgart IAAF World Athletics Final': 'Q1471412',
    'Kingston Jamaica International': 'Q2659410',
    'Kingston Jamaica Invitational': 'Q2659410',
    'Athina Grand Prix Tsiklitiria': 'Q1769244',
    'Sheffield Norwich Union British Grand Prix': 'Q746741',
    'Gateshead AVIVA British Grand Prix': 'Q746741',
    'Gateshead Norwich Union British Grand Prix': 'Q746741',
    'Osaka IAAF World Championships': 'Q208423',
    'Athina IAAF World Cup': 'Q264769',
    'Nassau CAC Championships': 'Q2949788',
    'Helsinki IAAF World Championships': { '1983': 'Q509599', '2005': 'Q630307' },
    'Hamilton CARIFTA Games': { '1975': 'Q4576552', '1980': 'Q4579188', '2004': 'Q4602580', '2012': 'Q4624983' },
    'Bridgetown Carifta Games U17': { '1972': 'Q4574956', '1977': 'Q4577589', '1985': 'Q4582223', '1989': 'Q4585097', '1994': 'Q4589274', '1997': 'Q4592277', '2001': 'Q4598538' },
    'Kingston Jamaican HS Ch. Class 1.': 'Q6044695',
    'Kingston Jamaican HS Ch. Class 2': 'Q6044695',
    'Port of Spain Carifta Games Jun.': { '1973': 'Q4575479', '1987': 'Q4583595', '1991': 'Q4586747', '1998': 'Q4593419', '2003': 'Q4601182' },
    'Sherbrooke IAAF World Youth Championships': 'Q2703482',
    'Debrecen IAAF World Youth Championships': 'Q2698736',
    'Bridgetown Pan American Junior Ch.': 'Q2955756',
    'Bridgetown CAC U18 Ch.': { '1982': 'Q4580349', '2002': 'Q4599836' },
    'Kingston IAAF World Junior Championships': 'Q968074',
    'London Marathon': 'Q578794',
    'Monza Nike Breaking2': 'Q30687990',
    'Berlin Marathon': 'Q161222',
    'New Delhi Half Marathon': 'Q1184175',
    'Ras Al Khaimah International Half Marathon': 'Q927906',
    'Rotterdam Marathon': 'Q1341108',
    'Castelbuono Giro Podistico Internazionale': 'Q1526878',
    'Chicago Marathon': 'Q1071822',
    'Hamburg Marathon': 'Q448958',
    'San Diego Rock \'n\' Roll Half Marathon': 'Q2160555',
    'Klagenfurt Half Marathon': 'Q1411556',
    'Carlsbad 5000': 'Q1043345',
    'Karlsruhe Internationales Hallenmeeting': 'Q2877552',
    'Karlsruhe BW-Bank-Meeting': 'Q2877552',
    'Doha IAAF Diamond League Meeting': 'Q1118647',
    'Doha Samsung Diamond League Meeting': 'Q1118647',
    'Doha Qatar Athletic Super Grand Prix': 'Q1118647',
    'Doha Qatar IAAF Super Tour': 'Q1118647',
    'Eugene Prefontaine Classic': 'Q679614',
    'Birmingham Aviva Indoor Grand Prix': 'Q2874427',
    'Nairobi Kenyan Olympic Trials': 'Q28223308',
    'Nairobi Kenyan Ch.': 'Q28223308',
    'Nairobi Kenyan Trials': 'Q28223308',
    'Nairobi Kenyan World Ch. Trials': 'Q28223308',
    'Lille Half Marathon': 'Q1728814',
    'Kavarna IAAF World Half Marathon Championships': 'Q1111254',
    'Stuttgart Sparkassen-Cup': 'Q3492700',
    'Stuttgart Sparkassen Cup': 'Q3492700',
    'Düsseldorf PSD Bank Meeting': 'Q4351908',
    'Hengelo Fanny Blankers-Koen Games': 'Q1386731',
    'Hengelo THALES FBK-Games': 'Q1386731',
    'New Delhi Commonwealth Games': 'Q695233',
    'Milano Notturna di Milano': 'Q3878960',
    'Sheffield BUPA Great Yorkshire Run': 'Q5600317',
    'Utrecht Singelloop': 'Q2289166',
    'Madrid San Silvestre Vallecana': 'Q1549242',
    
    'St-Etienne IAAF World Cross Country Championships': 'Q1141463',
    'Bruxelles IAAF World Cross Country Championships': 'Q1141461',
    'Lausanne IAAF World Cross Country Championships': 'Q675257',
    'Dublin IAAF World Cross Country Championships': 'Q127283',

    'Athens Olympic Games': { '1896': 'Q339297', '2004': 'Q339297' }, #{ '1896': 'Q8080', '2004': 'Q8558' },
    'Beijing Olympic Games': 'Q189941', #'Q8567',
    'London Olympic Games': { '1908': 'Q733330', '1948': 'Q515125', '2012': 'Q185262' }, #{ '1908': 'Q8111', '1948': 'Q8403', '2012': 'Q8577' },
    'Rio de Janeiro Olympic Games': 'Q18193712', #'Q8613',
    
    'Monaco IAAF World Athletics Final': { '2003': 'Q3072437', '2004': 'Q3072439', '2005': 'Q3072441' },
    'Berlin ISTAF': 'Q703948',
    'Rovereto Palio Città della Quercia': 'Q3361438',
    'Boston Marathon': 'Q826038',
}

iaafe2wd = {
    '60 Metres': 'Q246681',
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
    '1500 Metres': 'Q191691',
    'One Mile': 'Q943635',
    '2000 Metres': 'Q211164',
    '2000 Metres Steeplechase': 'Q30588012',
    '3000 Metres': 'Q223779',
    '3000 Metres Steeplechase': 'Q10437559',
    'Two Miles': 'Q2815830',
    '5000 Metres': 'Q240500',
    '10,000 Metres': 'Q163892',
    '10 Kilometres': 'Q2774730',
    '10 Kilometres Race Walk': 'Q26844349',
    '20 Kilometres': 'Q19767716',
    '20 Kilometres Race Walk': 'Q210673',
    'Half Marathon': 'Q215677',
    '30 Kilometres': 'Q54964282',
    'Marathon': 'Q40244',
    '50 Kilometres Race Walk': 'Q240387',
    'Short Race': 'Q500050',
    'Long Race': 'Q500050',
    'U20 Race': 'Q500050',
    '4x100 Metres Relay': 'Q230061',
    'Medley Relay': 'Q2532187', # swedish
    'Sprint Medley Relay': 'Q7581309',
    '4x400 Metres Relay': 'Q230057',
    'Distance Medley Relay': 'Q5282867',
    
}

iaafe2wd_m = {
    'Pole Vault': 'Q185027',
    'Javelin Throw': 'Q178108',
    'Hammer Throw': 'Q184865',
    'High Jump': 'Q165704',
    'Long Jump': 'Q170737',
    'Triple Jump': 'Q187204',
    'Shot Put': 'Q180935',
    'Discus Throw': 'Q182570',
    '35libs Weight': 'Q259509',
}

iaafe2wd_pts = {
    'Decathlon': 'Q184654',
    'Heptathlon': 'Q243264',
    'Pentathlon': 'Q24688986',
}

cnt2wd = { ine.split(',')[0].replace('_', ' '): ine.split(',')[-1] for ine in open('countries.csv').read().split('\n') }

wdq = '''SELECT ?item WHERE {{
  ?item wdt:{} ?value .
}}'''.format(P_IAAFID)

generator = site.preloadpages(
    pagegenerators.WikidataSPARQLPageGenerator(wdq, site),
    pageprops = True
)

generator = [ pywikibot.ItemPage(repo, 'Q1189') ]

edits = 0

def incedits():
    global edits
    edits += 1
    print('{} edits'.format(edits))

cachedmeets = { row[0]: row[1] for row in csv.reader(open('cachedmeets.csv', newline = '')) }
iaaf2gen = { row[0]: row[1] for row in csv.reader(open('iaaf2gen.csv', newline = '')) }

for page in generator:
    gender = None
    iaafid = None
    aaid = None
    itemd = page.get()
    #pprint.pprint(itemd)
    print(itemd['labels']['en'] if 'en' in itemd['labels'] else itemd['labels'])
    print(itemd['descriptions']['en'] if 'en' in itemd['descriptions'] else itemd['descriptions'])

    claim = pywikibot.Claim(repo, P_RESULTS)
    
    iaafid = itemd['claims'][P_IAAFID][0].getTarget()
    iaafurl = 'https://www.iaaf.org/athletes/athlete=' + iaafid
    print(iaafurl)
    iaafs = bs4.BeautifulSoup(session.get(iaafurl).text, 'html.parser')
    aaid = iaafs.find('div', { 'data-aaid': True })
    if aaid:
        aaid = aaid['data-aaid']
    else:
        print('skipped for no aaid')
        continue
    if iaafid in iaaf2gen:
        gender = iaaf2gen[iaafid] # 'Men' or 'Women'
        if gender not in [ 'Men', 'Women' ]:
            print('skipped for error in gender')
            continue
        gender = Q_FEMALE if gender == 'Women' else Q_MALE
    else:
        print('skipped for no gender')
        continue
    years = [ op['value'] for op in iaafs.find('select', { 'name': 'resultsByYear' }).find_all('option') ]
    for y in years:
        apiurl = 'https://www.iaaf.org/data/GetCompetitorResultsByYearHtml?resultsByYear={}&resultsByYearOrderBy=date&aaId={}'.format(y, aaid)
        ysoup = bs4.BeautifulSoup(session.get(apiurl).text, 'html.parser')
        perfs = ysoup.find('tbody').find_all('tr')
        for p in perfs:
            quals = []
            # parsing
            statedqual = pywikibot.Claim(repo, P_STATEDAS)
            statedqual_s = (' ; '.join([ td.text.strip() for td in p.find_all('td') ])[:254]).strip()
            print(statedqual_s)
            statedqual.setTarget(statedqual_s)
            quals.append(statedqual)

            pdate = p.find('td', { 'data-th': 'Date' }).text.strip()
            pdate = datetime.datetime.strptime(pdate.title(), '%d %b %Y')
            pcomp = p.find('td', { 'data-th': 'Competition' }).text.strip()
            pevnt = p.find('td', { 'data-th': 'Event' }).text.strip()
            pcnt = iaafcc.iaafcc[p.find('td', { 'data-th': 'Cnt.' }).text.strip()]
            pcat = p.find('td', { 'data-th': 'Cat' }).text.strip()
            prace = p.find('td', { 'data-th': 'Race' }).text.strip()
            pplace = p.find('td', { 'data-th': 'Pl.' }).text.strip()
            try:
                pplace = int(pplace.replace('.', '').strip())
            except:
                pplace = None
            pres = p.find('td', { 'data-th': 'Result' }).text.strip()
            if pres in perf2wd:
                resqual = pywikibot.Claim(repo, P_RESULTS) # TODO fix P here
                resqual.setTarget(pywikibot.ItemPage(repo, perf2wd[pres]))
                quals.append(resqual)
            reserr = 0.5
            if '.' in pres:
                reserr = 0.005
            if 'h' in pres:
                reserr = 0.05
            try:
                pres = sum(float(x) * 60 ** i for i, x in enumerate(reversed(pres.split(':'))))
            except:
                pres = None
            try:
                pwind = float(p.find('td', { 'data-th': 'Wind' }).text.strip())
            except:
                pwind = None
            # add qualifiers
            unit = None
            if pdate:
                # important: start skipping logic based on date matches here
                skip = False
                if P_RESULTS in itemd['claims']:
                    for resclaim in itemd['claims'][P_RESULTS]:
                        if P_POINTINTIME in resclaim.qualifiers:
                            timeq = resclaim.qualifiers[P_POINTINTIME][0].getTarget()
                            timeq = datetime.datetime(timeq.year, timeq.month, timeq.day)
                            if timeq == pdate:
                                skip = True
                if skip:
                    continue
                datequalifier = pywikibot.Claim(repo, P_POINTINTIME)
                datequalifier.setTarget(pywikibot.WbTime(year = pdate.year, month = pdate.month, day = pdate.day))
                quals.append(datequalifier)
            indoor = False
            field = False
            qcnt = None
            if pcnt:
                if pcnt not in cnt2wd:
                    print('Not in cnt2wd: {}'.format(pcnt))
                else:
                    qcnt = cnt2wd[pcnt]
                    cntqual = pywikibot.Claim(repo, P_COUNTRY)
                    cntqual.setTarget(pywikibot.ItemPage(repo, qcnt))
                    quals.append(cntqual)
            if prace:
                if prace in rnd2wd:
                    rndqual = pywikibot.Claim(repo, P_STAGEREACHED)
                    rndqual.setTarget(pywikibot.ItemPage(repo, rnd2wd[prace]))
                    quals.append(rndqual)
                else:
                    print('not in rnd2wd: {}'.format(prace))
            qevnt = None
            if pevnt:
                if 'Indoor' in pevnt:
                    pevnt = pevnt.replace('Indoor', '').strip()
                    indoor = True
                evntqualifier = pywikibot.Claim(repo, P_SPORTDISC)
                if pevnt in iaafe2wd:
                    unit = pywikibot.ItemPage(repo, Q_SECONDS)
                    qevnt = iaafe2wd[pevnt]
                elif pevnt in iaafe2wd_m:
                    field = True
                    reserr = 0.005
                    unit = pywikibot.ItemPage(repo, Q_METER)
                    qevnt = iaafe2wd_m[pevnt]
                elif pevnt in iaafe2wd_pts:
                    field = False
                    reserr = 0.5
                    unit = pywikibot.ItemPage(repo, Q_POINTS)
                    qevnt = iaafe2wd_pts[pevnt]
                else:
                    print('could not find event: {}'.format(pevnt))
                    print(apiurl)
                evntqualifier.setTarget(pywikibot.ItemPage(repo, qevnt))
                quals.append(evntqualifier)
            if indoor:
                indqualifier = pywikibot.Claim(repo, P_SPORT)
                indqualifier.setTarget(pywikibot.ItemPage(repo, Q_INDOORS))
                quals.append(indqualifier)
            #
            # IMPORTANT competition and event item creation
            #
            if pcomp and qevnt:
                ypcomp = '{} {}'.format(y, pcomp)
                if pcomp in iaafc2wd:
                    qcomp = iaafc2wd[pcomp]
                    if type(qcomp) is dict:
                        qcomp = qcomp[y]
                elif ypcomp in cachedmeets:
                    qcomp = cachedmeets[ypcomp]
                else:
                    print('competition not found, creating: {}'.format(pcomp))
                    ypcomp_item = pywikibot.ItemPage(site)
                    ypcomp_item.editEntity({
                        'labels': { 'en': ypcomp },
                        'descriptions': { 'en': 'Athletics competition in {}'.format(y) },
                    }, summary = 'Creating athletics competition')
                    incedits()
                    instanceclaim = pywikibot.Claim(repo, P_INSTANCEOF)
                    instanceclaim.setTarget(pywikibot.ItemPage(repo, Q_ATHLETICSMEETING))
                    ypcomp_item.addClaim(instanceclaim, summary = 'adding: instance of "athletics meeting"')
                    incedits()
                    if qcnt:
                        cntclaim = pywikibot.Claim(repo, P_COUNTRY)
                        cntclaim.setTarget(pywikibot.ItemPage(repo, qcnt))
                        ypcomp_item.addClaim(cntclaim, summary = 'adding country to athletics meeting')
                        incedits()
                    qcomp = ypcomp_item.getID()
                    csv.writer(open('cachedmeets.csv', 'a', newline = '')).writerow([ ypcomp, qcomp ])
                    cachedmeets[ypcomp] = qcomp
                # now we have qcomp, time to find or create qevntcomp
                qcomp_item = pywikibot.ItemPage(repo, qcomp)
                qevntcomp = None
                qcomp_itemd = qcomp_item.get()
                if P_HASPART in qcomp_itemd['claims']:
                    for partclaim in qcomp_itemd['claims'][P_HASPART]:
                        if P_OBJECTHASROLE in partclaim.qualifiers:
                            hasgender = False
                            hasqevnt = False
                            for role in partclaim.qualifiers[P_OBJECTHASROLE]:
                                if role.getTarget().getID() == gender:
                                    hasgender = True
                                if role.getTarget().getID() == qevnt:
                                    hasqevnt = True
                            if hasgender and hasqevnt:
                                qevntcomp = partclaim.getTarget().getID()
                                break
                if not qevntcomp:
                    qevntcomp_item = pywikibot.ItemPage(site)
                    qevntcomp_label = '{} - {} {}'.format(ypcomp, 'Women\'s' if gender == Q_FEMALE else 'Men\'s', pywikibot.ItemPage(repo, qevnt).get()['labels']['en'])
                    print('CREATING: ' + qevntcomp_label)
                    qevntcomp_item.editEntity({
                        'labels': { 'en': qevntcomp_label },
                        'descriptions': { 'en': 'Athletics discipline event at an athletics meeting' },
                    }, summary = 'Creating athletics event item')
                    incedits()
                    qevntcomp = qevntcomp_item.getID()
                    partclaim2 = pywikibot.Claim(repo, P_HASPART)
                    partclaim2.setTarget(pywikibot.ItemPage(repo, qevntcomp))
                    qcomp_item.addClaim(partclaim2, summary = 'Adding part of claim to athletics meeting')
                    incedits()
                    rolequal_gender = pywikibot.Claim(repo, P_OBJECTHASROLE)
                    rolequal_gender.setTarget(pywikibot.ItemPage(repo, gender))
                    partclaim2.addQualifier(rolequal_gender, summary = 'Adding gender role to athletics event')
                    incedits()
                    rolequal_event = pywikibot.Claim(repo, P_OBJECTHASROLE)
                    rolequal_event.setTarget(pywikibot.ItemPage(repo, qevnt))
                    partclaim2.addQualifier(rolequal_event, summary = 'Adding sports discipline role to athletics event')
                    incedits()
                    partofclaim = pywikibot.Claim(repo, P_PARTOF)
                    partofclaim.setTarget(pywikibot.ItemPage(repo, qcomp))
                    qevntcomp_item.addClaim(partofclaim, summary = 'Adding part of claim to athletics event')
                    incedits()
                    discclaim = pywikibot.Claim(repo, P_COMPCLASS)
                    discclaim.setTarget(pywikibot.ItemPage(repo, qevnt))
                    qevntcomp_item.addClaim(discclaim, summary = 'Adding sports discipline to athletics event')
                    incedits()
                    genclaim = pywikibot.Claim(repo, P_COMPCLASS)
                    genclaim.setTarget(pywikibot.ItemPage(repo, gender))
                    qevntcomp_item.addClaim(genclaim, summary = 'Adding gender to athletics event')
                    incedits()
                    instanceclass = pywikibot.Claim(repo, P_INSTANCEOF)
                    instanceclass.setTarget(pywikibot.ItemPage(repo, Q_ATHLETICSMEETING))
                    qevntcomp_item.addClaim(instanceclass, summary = 'Adding instance of athletics meeting to athletics event')
                    incedits()
                    particlaim = pywikibot.Claim(repo, P_PARTICIPANT)
                    particlaim.setTarget(pywikibot.ItemPage(repo, page.getID()))
                    qevntcomp_item.addClaim(particlaim, summary = 'Add participant to athletics event at athletics meeting')
                    incedits()
                claim.setTarget(pywikibot.ItemPage(repo, qevntcomp))
            else:
                print('something is terribly wrong')
                exit()
            #
            # end competition and event item creation
            #
            if pwind is not None:
                windqual = pywikibot.Claim(repo, P_WIND)
                windqual.setTarget(pywikibot.WbQuantity(pwind, unit = pywikibot.ItemPage(repo, Q_MPS), site = site))
                quals.append(windqual)
            if pplace is not None:
                placequal = pywikibot.Claim(repo, P_RANK)
                placequal.setTarget(pywikibot.WbQuantity(pplace, site = site))
                quals.append(placequal)
            if pres:
                if field:
                    presqualifier = pywikibot.Claim(repo, P_DISTANCE)
                else:
                    presqualifier = pywikibot.Claim(repo, P_RACETIME)
                presqualifier.setTarget(pywikibot.WbQuantity(pres, unit = unit, error = reserr, site = site))
                quals.append(presqualifier)
            page.addClaim(claim, summary = 'Adding {} race result'.format(y))
            incedits()
            for qua in quals:
                claim.addQualifier(qua, summary = 'Adding athletics performance qualifier for {} on {}'.format(pevnt, pdate.strftime('%Y-%m-%d')))
                incedits()
                time.sleep(0.5)
                if particlaim:
                    particlaim.addQualifier(qua, summary = 'Adding athletics performance qualifier to event for {} on {}'.format(pevnt, pdate.strftime('%Y-%m-%d')))
                    incedits()
                time.sleep(0.5)
            # add sources
            now = datetime.datetime.now()
            retrieved = pywikibot.Claim(repo, P_RETRIEVED)
            retrieved.setTarget(pywikibot.WbTime(year = now.year, month = now.month, day = now.day))
            statedin = pywikibot.Claim(repo, P_STATEDIN)
            statedin.setTarget(pywikibot.ItemPage(repo, Q_IAAF))
            refurl = pywikibot.Claim(repo, P_REFURL)
            refurl.setTarget(apiurl)
            claim.addSources([ statedin, refurl, retrieved ], summary = 'Adding sources for athletics performance from {}'.format(refurl))
            incedits()
            if particlaim:
                particlaim.addSources([ statedin, refurl, retrieved ], summary = 'Adding sources for athletics performance from {}'.format(refurl))
                incedits()
