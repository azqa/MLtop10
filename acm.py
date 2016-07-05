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

ROOT = 'http://jacm.acm.org/'
ROOTPUB = 'http://dl.acm.org/'

PROCEEDINGS = {
    "KDD '15": "Research Paper Presentations",
    "KDD '14": "Research session",
    "KDD '12": "Research session",
    "KDD '10": "Research track",
    "KDD '09": "Research track",
    "KDD '08": "papers",
    "KDD '07": "papers"
}


PROCEEDINGS_EXCEPTIONS = {
    "KDD '13": ["Keynote session","Research poster session"],
    "KDD '11": ["Keynote address","Panel Session","Demonstration track"]
}



def maybe_pickle_abstracts(name, force=False):
    set_filename = '{0}_abstracts.dill'.format(name)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        all_abstracts = dill.load(open(set_filename, 'rb'))
    else:
        if name == 'ACM_KDD':
            raw_abstracts = get_raw_proceeding_abstracts()
            all_abstracts = [raw_abstracts[v][k] for v in VERSIONS for k in raw_abstracts[v]]
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



def get_raw_proceeding_abstracts():
    res = defaultdict(lambda: defaultdict(set))
    total = 0
    home_url = 'http://dl.acm.org/proceedings.cfm?CFID=806986308&CFTOKEN=51891117'
    print 'Starting {0}'.format(home_url)
    home_req = urllib2.Request(home_url, headers={'User-Agent': "My Browser"})
    homepage = urllib2.urlopen(home_req).read()
    #homepage = urllib2.urlopen(home_url).read()
    home_soup = BeautifulSoup(homepage, 'html.parser')
    proceeding_dict = {}
    for link in home_soup.find_all('a'):
        if( ("KDD '" in link.get_text()) & ("Knowledge Discovery and Data Mining" in link.get_text()) ) or (("KDD '" in link.get_text()) & ("Knowledge discovery and data mining" in link.get_text()) ):
            proceeding_url = link['href']

            if (link['title'] in PROCEEDINGS.keys()) or link['title'] in PROCEEDINGS_EXCEPTIONS.keys():
                VERSIONS.append(link['title'])
                count = 0
                if proceeding_url not in proceeding_dict:
                    proceeding_dict[proceeding_url] = []


                    publication_url_flat = ROOTPUB + proceeding_url + '&preflayout=flat'
                    # Add header otherwise the request will be blocked by acm
                    pub_req = urllib2.Request(publication_url_flat, headers={'User-Agent': "My Browser"})
                    pub_page = urllib2.urlopen(pub_req).read()
                    print 'Starting {0}'.format(publication_url_flat)
                    abstract_soup = BeautifulSoup(pub_page, 'html.parser')


                    ##Every year format is different
                    table_soup = abstract_soup.findAll('td')
                    flag = 0
                    publication = None
                    for td in table_soup:
                        if "SESSION:" in td.renderContents():
                            #print td.renderContents()
                            if link['title'] in PROCEEDINGS.keys():
                                if PROCEEDINGS[link['title']] in td.renderContents():
                                    flag = 1
                                else:
                                    flag = 0
                            elif link['title'] in PROCEEDINGS_EXCEPTIONS.keys():
                                for item in PROCEEDINGS_EXCEPTIONS.keys()[:-1]:
                                    if item in td.renderContents():
                                        continue
                                if PROCEEDINGS_EXCEPTIONS[link['title']][-1] in td.renderContents():
                                    break
                                else:
                                    flag = 1


                        if flag == 1:
                            check_title = 0
                            if publication == None:
                                publications = td.find_all('a')
                                for item in publications:
                                    if (item != None) & ('citation.cfm' in item['href']):
                                        publication = item.get_text()
                                        break
                                continue


                            abstracts = td.find('div')
                            if abstracts != None:
                               for abstract in abstracts.find_all('span'):
                                    if "toHide" in abstract.attrs['id']:
                                        abstract_text = abstract.find("p").get_text()
                                        if publication not in res[link['title']]:
                                            res[link['title']][publication] = abstract_text
                                            count += 1
                                        else:
                                            print publication
                                        #print abstract_text

                                        publication = None
                                        #print count
                                        break
                print 'COUNT={0}'.format(count)
                total += count
            else:
                continue



    print 'TOTAL={0}'.format(total)
    return res


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
                        #print pub_link
                        #print abstract_soup.text
                        count += 1
                        #print count

            print 'COUNT={0}'.format(count)
            total += count

    print 'TOTAL={0}'.format(total)
    return res


if __name__ == '__main__':
    #maybe_pickle_abstracts('ACM_JACM')
    maybe_pickle_abstracts('ACM_KDD')

