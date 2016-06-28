import os
import dill
import urllib2
from collections import defaultdict
from bs4 import BeautifulSoup

# Maximum 1000 per year is reasonable
QUERY_PATTERN = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?hc=1000&pn='
QUERY_PATTERN_YEAR = '&py='

SOURCES = dict()
SOURCES['IEEE_TPAMI'] = (34, range(1979, 2017))
SOURCES['IEEE_NN'] = (72, range(1990, 2012))
SOURCES['IEEE_NN_LS'] = (5962385, range(2012, 2017))
SOURCES['IEEE_KDA'] = (69, range(1989, 2017))
SOURCES['IEEE_MI'] = (42, range(1982, 2017))
SOURCES['IEEE_EC'] = (4235, range(1997, 2017))
SOURCES['IEEE_CIM'] = (10207, range(2006, 2017))
SOURCES['IEEE_ASLP'] = (10376, range(2006, 2017))
SOURCES['IEEE_IS'] = (9670, range(2001, 2017))
SOURCES['IEEE_SMCB'] = (3477, range(1996, 2013))
SOURCES['IEEE_FS'] = (91, range(1993, 2017))


def maybe_pickle_abstracts(name, force=False):
    file_name = '{0}_abstracts'.format(name)
    publication_number, years = SOURCES[name]

    set_filename = '{0}.dill'.format(file_name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        abstracts = dill.load(open(set_filename, 'rb'))
    else:
        abstracts = get_abstracts(publication_number, years)
        abstracts = [abstracts[v][k] for v in years for k in abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return abstracts


def get_abstracts(publication_number, years):
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    total_actual = 0
    for year in years:
        query = '{0}{1}{2}{3}'.format(QUERY_PATTERN, publication_number, QUERY_PATTERN_YEAR, year)
        print 'Starting {0}'.format(query)
        page = urllib2.urlopen(query).read()
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
