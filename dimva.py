import os
import dill
import urllib2
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
    file_name = 'dimva_abstracts'

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
        year_url = urljoin(ROOT, 'search?q=dimva%20year%3A{0}%3A'.format(year))
        print 'Starting year {0}'.format(year)
        pub_req = urllib2.Request(year_url, headers={'User-Agent': "Magic Browser"})
        print(year_url)
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
                    publication_url = urljoin('', paper_url)
                    paper_req = urllib2.Request(publication_url, headers={'User-Agent': "Magic Browser"})
                    paper_page = urllib2.urlopen(paper_req).read()
                    abstract_soup = BeautifulSoup(paper_page, 'html.parser')
                    

                    paragraphs = abstract_soup.find('section', {'class': 'Abstract'}).findAll('p')
                    text = ''
                    for paragraph in paragraphs:
                        text += paragraph.getText() + ' '
                    #print(text)
                    #if 'Abstract Missing' not in text:
                    res[year][publication] = text
                    count_actual += 1
                        
                    count += 1

        print 'COUNT={0}/{1}'.format(count_actual, count)
        total += count
        total_actual += count_actual

    print 'TOTAL={0}/{1}'.format(total_actual, total)
    return res
