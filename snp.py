import os, time
import dill
import urllib2
from urllib2 import HTTPError
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

ROOT = 'https://dblp.uni-trier.de/'
YEARS = ('2010', '2011', '2012', '2013', '2014',
         '2018',
         '2015',
         '2016',
         '2017',
         '2019'
         )


def maybe_pickle_abstracts(force=False):
    file_name = 'snp_abstracts'

    set_filename = '{0}.dill'.format(file_name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        abstracts = dill.load(open(set_filename, 'rb'))
    else:
        abstracts = get_abstracts()
        abstracts = [abstracts[v][k] for v in YEARS for k in abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return abstracts


def get_abstracts():
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    total_actual = 0
    for year in YEARS:
        year_url = urljoin(ROOT, 'search?q=ieee%20symposium%20on%20security%20and%20privacy%20year%3A{0}%3A'.format(year))
        print 'Starting year {0}'.format(year)
        pub_req = urllib2.Request(year_url, headers={'User-Agent': "Magic Browser"})
        pub_page = urllib2.urlopen(pub_req).read()
        soup = BeautifulSoup(pub_page, 'html.parser')

        count = 0
        count_actual = 0
        heads = soup.findAll('div', {'class': 'head'})
        for head in heads:
            for link in head.find_all('a'):
                paper_url = link.get('href')
                #print(link)
                # Only abstracts
                if paper_url and 'https://doi.org/' in paper_url: # find the doi url
                    publication = paper_url
                    print 'Reading {0}'.format(paper_url)
                    paper_req = urllib2.Request(paper_url, headers={'User-Agent': "Magic Browser"})
                    paper_page = None
                    try:
                        paper_page = urllib2.urlopen(paper_req).read()
                    except HTTPError as e:
                        if e.code == 503:
                            print("Service unaviallble. Returing after 20 seconds")
                            t=30
                            to = int(e.hdrs.get('retry-after', t))
                            time.sleep(t)
                            paper_page = urllib2.urlopen(paper_req).read()
                        else:
                            raise

                    abstract_soup = BeautifulSoup(paper_page, 'html.parser')
                    
                    import re
                    text = ''
                    pattern = re.compile(r',"abstract":"(.*?)",', re.MULTILINE | re.DOTALL)
                    paragraphs = abstract_soup.find('script', text=pattern)
                    if paragraphs:
                        match = pattern.search(paragraphs.text)
                        if match:
                            text= match.group(1)  
                            #print(text)  
                        res[year][publication] = text
                        count_actual += 1

                    count += 1

        print 'COUNT={0}/{1}'.format(count_actual, count)
        total += count
        total_actual += count_actual

    print 'TOTAL={0}/{1}'.format(total_actual, total)
    return res
