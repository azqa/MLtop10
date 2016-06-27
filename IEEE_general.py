import os
import dill
import urllib2
from collections import defaultdict
from bs4 import BeautifulSoup

# Maximum 1000 per year is reasonable
QUERY_PATTERN = 'http://ieeexplore.ieee.org/gateway/ipsSearch.jsp?hc=1000&pn='
QUERY_PATTERN_YEAR = '&py='


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
