import os
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

JOURNALS = dict()
JOURNALS['ACM_CSUR'] = ['csur', range(2007, 2017)]
JOURNALS['ACM_JACM'] = ['jacm', range(2007, 2017)]
JOURNALS['ACM_TIST'] = ['tist', range(2010, 2017)]
JOURNALS['ACM_TOIS'] = ['tois', range(2007, 2017)]
JOURNALS['ACM_TKDD'] = ['tkdd', range(2007, 2017)]
JOURNALS['ACM_TAAS'] = ['taas', range(2007, 2017)]
JOURNALS['ACM_TiiS'] = ['tiis', range(2011, 2017)]
JOURNALS['ACM_TAP'] = ['tap', range(2007, 2017)]
JOURNALS['ACM_TEAC'] = ['teac', range(2013, 2017)]

ROOT_PRE = 'http://'
ROOT_POST = '.acm.org/'
ROOT_ARCHIVE = 'archive.cfm'
VERSIONS = []


def maybe_pickle_abstracts(name, force=False):
    set_filename = '{0}_abstracts.dill'.format(name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        all_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        _, years = JOURNALS[name]
        abstracts = get_raw_abstracts(name)
        all_abstracts = [abstracts[y][k] for y in years for k in abstracts[y]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(all_abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return all_abstracts


def get_raw_abstracts(name):
    res = defaultdict(lambda: defaultdict(set))
    total = 0
    short_name, years = JOURNALS[name]
    home_url = '{0}{1}{2}{3}'.format(ROOT_PRE, short_name, ROOT_POST, ROOT_ARCHIVE)
    print 'Starting {0}'.format(home_url)
    homepage = urllib2.urlopen(home_url).read()
    home_soup = BeautifulSoup(homepage, 'html.parser')

    for link in home_soup.find_all('a'):
        if 'Volume' in link.text:
            year = int(link.text.split(' ')[-1])
            if not year in years:
                break
            volume_link = link['href']
            l_index = volume_link.rfind('=')
            v = volume_link[l_index + 1:]
            VERSIONS.append(v)
            volume_url = urljoin('{0}{1}{2}'.format(ROOT_PRE, short_name, ROOT_POST),'{0}'.format(volume_link))
            print 'Starting {0}, {1}'.format(volume_url, link)
            vol_page = urllib2.urlopen(volume_url).read()
            vol_soup = BeautifulSoup(vol_page, 'html.parser')

            count = 0
            publication_dict = {}
            for pub_link in vol_soup.find_all('a'):
                if 'citation.cfm' in pub_link['href']:
                    publication_url = pub_link['href']
                    if publication_url not in publication_dict:
                        publication_dict[publication_url] = []
                        publication = pub_link.text
                        publication_url_flat = publication_url + '&preflayout=flat'
                        # Add header otherwise the request will be blocked by acm
                        pub_req = urllib2.Request(publication_url_flat, headers={'User-Agent': "Magic Browser"})
                        pub_page = urllib2.urlopen(pub_req).read()
                        abstract_soup = BeautifulSoup(pub_page, 'html.parser')

                        ## slice the page
                        h1tags = abstract_soup.find_all('h1')

                        def next_element(elem):
                            while elem is not None:
                                # Find next element, skip NavigableString objects
                                elem = elem.next_sibling
                                if elem.name == 'div':
                                    return elem

                        for h1tag in h1tags:
                            if h1tag.text == 'ABSTRACT':
                                #page = [str(h1tag)]
                                elem = next_element(h1tag)
                                page = [str(elem)]
                                #page.append(str(elem))
                                break
                        abstract_soup = BeautifulSoup(page[0], 'html.parser')
                        res[year][pub_link] = abstract_soup.text
                        print pub_link
                        print abstract_soup.text
                        count += 1
                        print count

            print 'COUNT={0}'.format(count)
            total += count

    print 'TOTAL={0}'.format(total)
    return res


if __name__ == '__main__':
    from general import get_keywords_of_single_abstract
    maybe_pickle_abstracts('ACM_JACM')

    index = 0
    for abstract in maybe_pickle_abstracts('ACM_JACM'):
        index+=1
        keyw = get_keywords_of_single_abstract(abstract)
        #print(keyw)
        #if (len(keyw)==0):
            #print("ABSTRACT #"+str(index))
