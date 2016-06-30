import os
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

ROOT = 'http://www.sciencedirect.com/science/journal/'
JOURNALS = dict()
# Starting 2007
JOURNALS['Elsevier_PR'] = ('00313203', ['60', '58', '57', '56', '55', '54', '53', '52', '51', '50', '49'] +\
                                       ['48/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['47/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['46/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['45/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['44/{0}'.format(issue) for issue in range(1, 9)] + ['44/10-11', '44/12'] +\
                                       ['43/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['42/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['41/{0}'.format(issue) for issue in range(1, 13)] +\
                                       ['40/{0}'.format(issue) for issue in range(1, 13)]
                           )


def maybe_pickle_abstracts(name, force=False):
    file_name = '{0}_abstracts'.format(name)

    set_filename = '{0}.dill'.format(file_name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        abstracts = dill.load(open(set_filename, 'rb'))
    else:
        _, volumes = JOURNALS[name]
        abstracts = get_abstracts(name)
        abstracts = [abstracts[v][k] for v in volumes for k in abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return abstracts


def get_abstracts(name):
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    id, volumes = JOURNALS[name]
    for volume in volumes:
        volume_url = urljoin(ROOT, '{0}/{1}'.format(id, volume))
        print 'Starting volume {0}'.format(volume)
        pub_req = urllib2.Request(volume_url, headers={'User-Agent': "Magic Browser"})
        pub_page = urllib2.urlopen(pub_req).read()
        soup = BeautifulSoup(pub_page, 'html.parser')

        count = 0
        for link in soup.find_all('a'):
            abstract_url = link.get('data-url')
            # Only abstracts
            if abstract_url and 'abstract' in abstract_url:
                publication = abstract_url[abstract_url.find('pii') + 4:abstract_url.find('&_issn')]
                print 'Reading {0}'.format(publication)
                abstract_req = urllib2.Request(abstract_url, headers={'User-Agent': "Magic Browser"})
                abstract_page = urllib2.urlopen(abstract_req).read()
                abstract_soup = BeautifulSoup(abstract_page, 'html.parser')
                raw_abstract = abstract_soup.getText()

                start_idx = raw_abstract.find('Abstract')
                end_idx = raw_abstract.rfind('Citing articles')
                abstract = raw_abstract[start_idx + len('Abstract'):end_idx-1]

                res[volume][abstract_url] = abstract

                count += 1
        print 'COUNT={0}'.format(count)
        total += count

    print 'TOTAL={0}'.format(total)
    return res
