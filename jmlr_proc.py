import os
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

ROOT = 'http://www.jmlr.org/proceedings/papers/'
VERSIONS = range(1, 52)
FILE_RAW = 'jmlr_proc_raw_abstracts'
FILE_CUT = 'jmlr_proc_abstracts'


def maybe_pickle_raw_abstracts(force=False):
    set_filename = '{0}.dill'.format(FILE_RAW)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        raw_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        raw_abstracts = get_raw_abstracts()
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(raw_abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return raw_abstracts


def maybe_pickle_abstracts(force=False):
    set_filename = '{0}.dill'.format(FILE_CUT)
    print set_filename
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        all_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        raw_abstracts = maybe_pickle_raw_abstracts()
        cut_abstracts = get_cut_abstracts(raw_abstracts)
        all_abstracts = [cut_abstracts[v][k] for v in VERSIONS for k in cut_abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(all_abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return all_abstracts


def get_raw_abstracts():
    res = defaultdict(lambda: defaultdict(set))

    total = 0
    for v in VERSIONS:
        volume_url = urljoin(ROOT, 'v{0}'.format(v))
        print 'Starting {0}'.format(volume_url)
        page = urllib2.urlopen(volume_url).read()
        soup = BeautifulSoup(page, 'html.parser')

        count = 0
        for link in soup.find_all('a'):
            # Only abstracts
            if 'abs' in link.text:
                publication = link['href']
                l_index = publication.rfind('/')
                r_index = publication.rfind('.htm')
                html_htm_page = 'htm'
                if 'html' in publication:
                    html_htm_page = 'html'
                publication = publication[l_index+1:r_index]

                # Do not take revisions
                if publication[-2] != 'r':
                    print 'Reading {0}'.format(publication)

                    abstract_url = urljoin(volume_url, 'v{0}/{1}.{2}'.format(v, publication, html_htm_page))
                    # print abstract_url
                    abstract_page = urllib2.urlopen(abstract_url).read()
                    abstract_soup = BeautifulSoup(abstract_page, 'html.parser')

                    res[v][publication] = abstract_soup.get_text()
                    count += 1
        print 'COUNT={0}'.format(count)
        total += count

    print 'TOTAL={0}'.format(total)
    return res


def get_cut_abstracts(raw_abstracts):
    res = defaultdict(lambda: defaultdict(set))

    for v in VERSIONS:
        for k in raw_abstracts[v]:
            abstract = raw_abstracts[v][k]
            start_idx = abstract.find('Abstract')
            end_idx = abstract.rfind('Home Page')
            res[v][k] = abstract[start_idx + len('Abstract'):end_idx-1]

    return res
