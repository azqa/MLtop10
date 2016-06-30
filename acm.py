import os
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

ROOT = 'http://jacm.acm.org/'
ROOTPUB = 'http://dl.acm.org/'
FILE_RAW = 'acm_raw_abstracts'
FILE_CUT = 'acm_abstracts'
VERSIONS = []

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
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        all_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        raw_abstracts = get_raw_abstracts()
        #cut_abstracts = get_cut_abstracts(raw_abstracts)
        all_abstracts = [raw_abstracts[v][k] for v in VERSIONS for k in raw_abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(all_abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return all_abstracts


def get_raw_abstracts():
    res = defaultdict(lambda: defaultdict(set))
    total = 0
    home_url = ROOT + 'archive.cfm'
    print 'Starting {0}'.format(home_url)
    homepage = urllib2.urlopen(home_url).read()
    home_soup = BeautifulSoup(homepage, 'html.parser')

    for link in home_soup.find_all('a'):
        if 'Volume' in link.text:
            if '2007' in link.text:
                break
            volume_link = link['href']
            l_index = volume_link.rfind('=')
            v = volume_link[l_index + 1:]
            VERSIONS.append(v)
            volume_url = urljoin(ROOT,'{0}'.format(volume_link))
            print 'Starting {0}'.format(volume_url)
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
                        res[v][publication] = abstract_soup.text
                        #print abstract_soup.text
                        count += 1
                        print count

            print 'COUNT={0}'.format(count)
            total += count

    print 'TOTAL={0}'.format(total)
    return res



def maybe_pickle_acm_raw_abstracts(force=False):
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





if __name__ == '__main__':
    import main

    index = 0
    for abstract in maybe_pickle_abstracts():
        index+=1
        keyw = main.get_keywords_of_single_abstract(abstract)
        #print(keyw)
        #if (len(keyw)==0):
            #print("ABSTRACT #"+str(index))
