import os
import dill
import urllib2
from collections import defaultdict
from urlparse import urljoin
from bs4 import BeautifulSoup

ROOT = 'https://papers.nips.cc/'
YEARS = ('20-2007',
         '21-2008',
         '22-2000',
         '23-2010',
         '24-2011',
         '25-2012',
         '26-2013',
         '27-2014',
         '28-2015',
         )


def maybe_pickle_abstracts(force=False):
    file_name = 'nips_abstracts'

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
        year_url = urljoin(ROOT, 'book/advances-in-neural-information-processing-systems-{0}'.format(year))
        print 'Starting year {0}'.format(year)
        pub_req = urllib2.Request(year_url, headers={'User-Agent': "Magic Browser"})
        pub_page = urllib2.urlopen(pub_req).read()
        soup = BeautifulSoup(pub_page, 'html.parser')

        count = 0
        count_actual = 0
        for link in soup.find_all('a'):
            paper_url = link.get('href')
            # Only abstracts
            if paper_url and '/paper/' in paper_url:
                publication = paper_url[paper_url.find('/paper/') + 7:]
                print 'Reading {0}'.format(publication)
                publication_url = urljoin(ROOT, paper_url)
                paper_req = urllib2.Request(publication_url, headers={'User-Agent': "Magic Browser"})
                paper_page = urllib2.urlopen(paper_req).read()
                abstract_soup = BeautifulSoup(paper_page, 'html.parser')

                paragraphs = abstract_soup.findAll('p')
                for paragraph in paragraphs:
                    class_tag = paragraph.get('class')
                    if class_tag and 'abstract' in class_tag:
                        text = paragraph.getText()
                        if 'Abstract Missing' not in text:
                            res[year][publication] = paragraph.getText()
                            count_actual += 1
                            break
                count += 1

        print 'COUNT={0}/{1}'.format(count_actual, count)
        total += count
        total_actual += count_actual

    print 'TOTAL={0}/{1}'.format(total_actual, total)
    return res
