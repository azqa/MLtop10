import os
import dill
import urllib2
from collections import defaultdict
from bs4 import BeautifulSoup

# Maximum 1000 per year is reasonable
#QUERY = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?doi=*TPAMI*&hc=1000&py='
QUERY = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?pn=34&hc=1000&py='
YEARS = range(1979, 2000) + range(2000, 2017)
FILE_CUT = 'IEEE_TPAMI_abstracts'


def maybe_pickle_abstracts(force=False):
    set_filename = '{0}.dill'.format(FILE_CUT)
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
        year_url = '{0}{1}'.format(QUERY, year)
        print 'Starting {0}'.format(year_url)
        page = urllib2.urlopen(year_url).read()
        soup = BeautifulSoup(page, 'lxml-xml')
        documents = soup.findAll('document')

        count = len(documents)
        count_actual = 0
        for document in documents:
            doi = document.find('doi').getText()
            abstract = document.findAll('abstract')
            # Some may not have an abstract
            if len(abstract):
                count_actual += 1
                res[year][doi] = abstract[0].getText()

        print 'COUNT={0}/{1}'.format(count_actual, count)
        total += count
        total_actual += count_actual

    print 'TOTAL={0}/{1}'.format(total_actual, total)
    return res
