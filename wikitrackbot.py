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
Q_POINTS = 'Q24038885'

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
P_COMPCLASS = 'P2094'
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

# NOTE: ordered ( main event, male gendered, female gendered )
iaafe2wd = {
    '50 Metres': ( 'Q240356', 'Q55242741', 'Q55242785' ),
    '50 Metres Hurdles': ( 'Q4639907', 'Q55242835', 'Q55242883' ),
    '55 Metres': ( 'Q4640627', 'Q55242931', 'Q55242979' ),
    '55 Metres Hurdles': ( 'Q4640620', 'Q55243099', 'Q55243145' ),
    '60 Metres': ( 'Q246681', 'Q55243193', 'Q55243244' ),
    '60 Metres Hurdles': ( 'Q1026754', 'Q55243293', 'Q55243345' ),
    '100 Metres': ( 'Q164761', 'Q55243390', 'Q55243435' ),
    '100 Metres Hurdles': ( 'Q164731', 'Q55243477', 'Q55243520' ),
    '110 Metres Hurdles': ( 'Q170004', 'Q55243565', 'Q55243608' ),
    '150 Metres': ( 'Q2807981', 'Q55243658', 'Q55243705' ),
    '200 Metres': ( 'Q211155', 'Q55243755', 'Q55243804' ),
    '300 Metres': ( 'Q2402434', 'Q55243851', 'Q55243894' ),
    '400 Metres': ( 'Q334734', 'Q55243939', 'Q55243980' ),
    '400 Metres Hurdles': ( 'Q231419', 'Q55244026', 'Q55244071' ),
    '500 Metres': ( 'Q2817139', 'Q55244117', 'Q55244158' ),
    '600 Metres': ( 'Q2817913', 'Q55244207', 'Q55244249' ),
    '800 Metres': ( 'Q271008', 'Q55244298', 'Q55244345' ),
    '1000 Metres': ( 'Q1629556', 'Q55244390', 'Q55244439' ),
    '1500 Metres': ( 'Q191691', 'Q55244489', 'Q55244535' ),
    'One Mile': ( 'Q943635', 'Q55244585', 'Q55244631' ),
    '2000 Metres': ( 'Q211164', 'Q55244678', 'Q55244718' ),
    '2000 Metres Steeplechase': ( 'Q30588012', 'Q55244765', 'Q55244808' ),
    '3000 Metres': ( 'Q223779', 'Q55244852', 'Q55244891' ),
    '3000 Metres Steeplechase': ( 'Q10437559', 'Q55244942', 'Q55244986' ),
    '3000 Metres Race Walk': ( 'Q30588450', 'Q55245034', 'Q55245081' ),
    'Two Miles': ( 'Q2815830', 'Q55245128', 'Q55245177' ),
    '5000 Metres': ( 'Q240500', 'Q55245220', 'Q55245268' ),
    '5000 Metres Race Walk': ( 'Q11187928', 'Q55245310', 'Q55245354' ),
    '10,000 Metres': ( 'Q163892', 'Q55245399', 'Q55245440' ),
    '10,000 Metres Race Walk': ( 'Q28444668', 'Q55245493', 'Q55245535' ),
    '10 Kilometres': ( 'Q2774730', 'Q55245579', 'Q55245623' ),
    '10 Kilometres Race Walk': ( 'Q26844349', 'Q55245670', 'Q55245711' ),
    '15 Kilometres': ( 'Q19767716', 'Q55245745', 'Q55245778' ),
    '10 Miles': ( 'Q2767252', 'Q55245809', 'Q55245841' ),
    '20 Kilometres': ( 'Q19827858', 'Q55246102', 'Q55246136' ),
    '20 Kilometres Race Walk': ( 'Q210673', 'Q55246165', 'Q55246190' ),
    'Half Marathon': ( 'Q215677', 'Q55246222', 'Q55246259' ),
    '30 Kilometres': ( 'Q54964282', 'Q55246292', 'Q55246317' ),
    '35 Kilometres Race Walk': ( 'Q55234451', 'Q55246352', 'Q55246393' ),
    'Marathon': ( 'Q40244', 'Q55246435', 'Q55246472' ),
    '50 Kilometres': ( 'Q2817174', 'Q55246501', 'Q55246530' ),
    '50 Kilometres Race Walk': ( 'Q240387', 'Q55246561', 'Q55246594' ),
    '100 Kilometres': ( 'Q1847570', 'Q55246623', 'Q55246655' ),
    'Cross Country': ( 'Q500050', 'Q55246682', 'Q55246713' ), # not used?
    'Short Race': ( 'Q55247078', 'Q55247308', 'Q55247336' ),
    'Long Race': ( 'Q55247140', 'Q55247363', 'Q55247390' ),
    'U20 Race': ( 'Q55247191', 'Q55247419', 'Q55247449' ),
    'Senior Race': ( 'Q55246937', 'Q55247480', 'Q55247513' ),
    '4x100 Metres Relay': ( 'Q230061', 'Q55247536', 'Q55247559' ),
    '4x200 Metres Relay': ( 'Q3114131', 'Q55247588', 'Q55247613' ),
    'Medley Relay': ( 'Q2532187', 'Q55247637', 'Q55247662' ), # swedish
    'Sprint Medley Relay': ( 'Q7581309', 'Q55247684', 'Q55247709' ),
    '4x400 Metres Relay': ( 'Q230057', 'Q55247732', 'Q55247759' ),
    '4x800 Metres Relay': ( 'Q744307', 'Q55247784', 'Q55247810' ),
    'Distance Medley Relay': ( 'Q5282867', 'Q55247832', 'Q55247856' ),
    '4x1500 Metres Relay': ( 'Q2076688', 'Q55247882', 'Q55247916' ),
}

iaafe2wd_m = {
    'Pole Vault': ( 'Q185027', 'Q55247946', 'Q55247977' ),
    'Javelin Throw': ( 'Q178108', 'Q55248012', 'Q55248046' ),
    'Hammer Throw': ( 'Q184865', 'Q55248070', 'Q55248094' ),
    'High Jump': ( 'Q165704', 'Q55248117', 'Q55248144' ),
    'Long Jump': ( 'Q170737', 'Q55248168', 'Q55248192' ),
    'Triple Jump': ( 'Q187204', 'Q55248213', 'Q55248239' ),
    'Shot Put': ( 'Q180935', 'Q55248267', 'Q55248302' ),
    'Discus Throw': ( 'Q182570', 'Q55248331', 'Q55248363' ),
    '35libs Weight': ( 'Q259509', 'Q55248398', 'Q55248425' ),
}

iaafe2wd_pts = {
    'Decathlon': ( 'Q184654', 'Q55248448', 'Q55248471' ),
    'Heptathlon': ( 'Q243264', 'Q55248494', 'Q55248516' ),
    'Pentathlon': ( 'Q24688986', 'Q55248540', 'Q55248562' ),
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
    gendernum = None
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
        gendernum = 2 if gender == 'Women' else 1
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
            multi = False
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
            qevntg = None
            if pevnt:
                if 'Indoor' in pevnt:
                    pevnt = pevnt.replace('Indoor', '').strip()
                    indoor = True
                evntqualifier = pywikibot.Claim(repo, P_SPORTDISC)
                if pevnt in iaafe2wd:
                    unit = pywikibot.ItemPage(repo, Q_SECONDS)
                    qevnt = iaafe2wd[pevnt][0]
                    qevntg = iaafe2wd[pevnt][gendernum]
                elif pevnt in iaafe2wd_m:
                    field = True
                    reserr = 0.005
                    unit = pywikibot.ItemPage(repo, Q_METER)
                    qevnt = iaafe2wd_m[pevnt][0]
                    qevntg = iaafe2wd_m[pevnt][gendernum]
                elif pevnt in iaafe2wd_pts:
                    multi = True
                    field = False
                    reserr = 0.5
                    unit = pywikibot.ItemPage(repo, Q_POINTS)
                    qevnt = iaafe2wd_pts[pevnt][0]
                    qevntg = iaafe2wd_pts[pevnt][gendernum]
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
            qcomp = None
            particlaim = None
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
                        if P_OBJECTHASROLE in partclaim.qualifiers and P_POINTINTIME in partclaim.qualifiers:
                            if partclaim.qualifiers[P_OBJECTHASROLE][0].getID() == qevntg:
                                timeq = partclaim.qualifiers[P_POINTINTIME][0].getTarget()
                                if timeq.year == pdate.year: # can't be more specific for prelim / finals on different days
                                    qevntcomp = partclaim.getTarget().getID()
                                    break
                if not qevntcomp:
                    qevntcomp_item = pywikibot.ItemPage(site)
                    qevntcomp_label = '{} – {} {}'.format(ypcomp, 'Women\'s' if gender == Q_FEMALE else 'Men\'s', pywikibot.ItemPage(repo, qevnt).get()['labels']['en'])
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
                    rolequal_event = pywikibot.Claim(repo, P_OBJECTHASROLE)
                    rolequal_event.setTarget(pywikibot.ItemPage(repo, qevntg))
                    partclaim2.addQualifier(rolequal_event, summary = 'Adding gendered sport discipline role to athletics event')
                    incedits()
                    pointintimequal = pywikibot.Claim(repo, P_POINTINTIME)
                    pointintimequal.setTarget(pywikibot.WbTime(year = pdate.year, month = pdate.month, day = pdate.day))
                    partclaim2.addQualifier(pointintimequal, summary = 'Adding point in time qualifier to athletics event')
                    incedits()
                    partofclaim = pywikibot.Claim(repo, P_PARTOF)
                    partofclaim.setTarget(pywikibot.ItemPage(repo, qcomp))
                    qevntcomp_item.addClaim(partofclaim, summary = 'Adding part of claim to athletics event')
                    incedits()
                    discclaim = pywikibot.Claim(repo, P_COMPCLASS)
                    discclaim.setTarget(pywikibot.ItemPage(repo, qevntg))
                    qevntcomp_item.addClaim(discclaim, summary = 'Adding gendered sports discipline to athletics event')
                    incedits()
                    edateclaim = pywikibot.Claim(repo, P_POINTINTIME)
                    edateclaim.setTarget(pywikibot.WbTime(year = pdate.year, month = pdate.month, day = pdate.day))
                    qevntcomp_item.addClaim(edateclaim, summary = 'Adding date to athletics event')
                    incedits()
                    instanceclass = pywikibot.Claim(repo, P_INSTANCEOF)
                    instanceclass.setTarget(pywikibot.ItemPage(repo, Q_ATHLETICSMEETING))
                    qevntcomp_item.addClaim(instanceclass, summary = 'Adding instance of athletics meeting to athletics event')
                    incedits()
                qevntcomp_item = pywikibot.ItemPage(repo, qevntcomp)
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
            if qcomp:
                compartqual = pywikibot.Claim(repo, P_PARTOF)
                compartqual.setTarget(pywikibot.ItemPage(repo, qcomp))
                quals.append(compartqual)
            if pwind is not None:
                windqual = pywikibot.Claim(repo, P_WIND)
                windqual.setTarget(pywikibot.WbQuantity(pwind, unit = pywikibot.ItemPage(repo, Q_MPS), site = site))
                quals.append(windqual)
            if pplace is not None:
                placequal = pywikibot.Claim(repo, P_RANK)
                placequal.setTarget(pywikibot.WbQuantity(pplace, site = site))
                quals.append(placequal)
            if pres:
                if multi:
                    presqualifier = pywikibot.Claim(repo, P_POINTS)
                elif field:
                    presqualifier = pywikibot.Claim(repo, P_DISTANCE)
                else:
                    presqualifier = pywikibot.Claim(repo, P_RACETIME)
                if pres in perf2wd: # check for DNS / NM / ND
                    presqualifier.setSnakType('novalue')
                else:
                    presqualifier.setSnakType('value')
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
            claim.addSources([ statedin, refurl, retrieved ], summary = 'Adding sources for athletics performance from {}'.format(apiurl))
            incedits()
            if particlaim:
                particlaim.addSources([ statedin, refurl, retrieved ], summary = 'Adding sources for athletics performance from {}'.format(apiurl))
                incedits()
