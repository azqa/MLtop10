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
JOURNALS['Elsevier_KBS'] = ('09507051', range(26, 107) +\
                                        ['25/1'] +\
                                        ['24/{0}'.format(issue) for issue in range(1, 9)] +\
                                        ['23/{0}'.format(issue) for issue in range(1, 9)] +\
                                        ['22/{0}'.format(issue) for issue in range(1, 9)] +\
                                        ['21/{0}'.format(issue) for issue in range(1, 9)] +\
                                        ['20/{0}'.format(issue) for issue in range(1, 9)]
                            )
JOURNALS['Elsevier_NN'] = ('08936080', range(31, 82) +\
                                       ['29-30', 28, 27, 26, 25] +\
                                       ['24/{0}'.format(issue) for issue in range(1, 11)] +\
                                       ['23/{0}'.format(issue) for issue in range(1, 8)] + ['23/8-9'] + ['23/10'] +\
                                       ['22/{0}'.format(issue) for issue in range(1, 5)] + ['22/5-6'] + ['22/{0}'.format(issue) for issue in range(7, 11)] +\
                                       ['21/1'] + ['21/2-3'] + ['21/{0}'.format(issue) for issue in range(4, 11)] +\
                                       ['20/{0}'.format(issue) for issue in range(1, 11)]
                           )
JOURNALS['Elsevier_Neuro'] = ('09252312', range(176, 206) +\
                                          ['175/part/PB', '175/part/PA', '174/part/PB', '174/part/PA'] +\
                                          ['173/part/P1', '173/part/P2', '173/part/P3'] +\
                                          range(152, 172) +\
                                          ['151/part/P1', '151/part/P2', '151/part/P3'] +\
                                          ['150/part/PB', '150/part/PA'] +\
                                          ['149/part/PC', '149/part/PB', '149/part/PA'] +\
                                          range(79, 149) +\
                                          ['78/1', '77/1', '76/1', '75/1'] +\
                                          ['74/{0}'.format(issue) for issue in range(16, 19)] + ['74/12-13', '74/14-15'] + ['74/{0}'.format(issue) for issue in range(4, 12)] + ['74/1-3'] +\
                                          ['73/16-18', '73/13-15', '73/10-12', '73/7-9', '73/4-6', '73/1-3'] +\
                                          ['72/16-18', '72/13-15', '72/10-12', '72/7-9', '72/4-6', '72/1-3'] +\
                                          ['71/16-18', '71/13-15', '71/10-12', '71/7-9', '71/4-6', '71/1-3'] +\
                                          ['70/16-18', '70/13-15', '70/10-12', '70/7-9', '70/4-6']
                            )
JOURNALS['Elsevier_AI'] = ('00043702', range(201, 239) + ['199-200'] + range(193, 199) + ['191-192', '190', '189', '187-188', '186', '184-185', '182-183', '188-181', '177-179'] +\
                                       ['176/1', '175/18', '175/16-17', '175/14-15', '175/12-13', '175/11', '175/9-10', '175/7-8', '175/5-6', '175/3-4', '175/2', '175/1'] +\
                                       ['174/18', '174/16-17', '174/15', '174/14', '174/12-13', '174/11', '174/9-10', '174/7-8', '174/5-6', '174/3-4', '174/2', '174/1'] +\
                                       ['173/18', '173/16-17', '173/15', '173/14', '173/12-13', '173/11', '173/9-10', '173/7-8', '173/5-6', '173/3-4', '173/2', '173/1'] +\
                                       ['172/18', '172/16-17', '172/15', '172/14', '172/12-13', '173/11', '172/10', '172/8-9', '172/7-8', '172/6-7', '172/4-5', '172/2-3', '172/1'] +\
                                       ['171/18', '171/16-17', '171/10-15', '171/8-9', '171/7', '171/5-6', '171/4', '171/2-3', '171/1']
                           )
JOURNALS['Elsevier_CSL'] = ('08852308', range(35, 42) + ['34/1', '33/1', '32/1', '31/1', '30/1', '29/1'] +\
                                        ['28/{0}'.format(issue) for issue in range(1, 7)] +\
                                        ['27/{0}'.format(issue) for issue in range(1, 7)] +\
                                        ['26/{0}'.format(issue) for issue in range(1, 6)] +\
                                        ['25/{0}'.format(issue) for issue in range(1, 5)] +\
                                        ['24/{0}'.format(issue) for issue in range(1, 5)] +\
                                        ['23/{0}'.format(issue) for issue in range(1, 5)] +\
                                        ['22/{0}'.format(issue) for issue in range(1, 5)] +\
                                        ['21/{0}'.format(issue) for issue in range(1, 5)]
                           )
JOURNALS['Elsevier_PRL'] = ('01678655', range(69, 81) + ['68/part/P2' + '68/part/P1' + '67/part/P2' + '67/part/P1'] +\
                                        range(62, 67) + ['60-61'] + range(35, 60) +\
                                        ['34/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['33/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['32/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['31/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['30/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['29/{0}'.format(issue) for issue in range(1, 17)] +\
                                        ['28/{0}'.format(issue) for issue in range(1, 17)]
                            )
JOURNALS['Elsevier_CSDA'] = ('01679473', range(58, 104) + ['57/1'] +\
                                         ['56/{0}'.format(issue) for issue in range(1, 13)] +\
                                         ['55/{0}'.format(issue) for issue in range(1, 13)] +\
                                         ['54/{0}'.format(issue) for issue in range(1, 13)] +\
                                         ['53/{0}'.format(issue) for issue in range(1, 13)] +\
                                         ['52/{0}'.format(issue) for issue in range(1, 13)] +\
                                         ['51/{0}'.format(issue) for issue in range(1, 13)]
                             )

JOURNALS['Elsevier_IPM'] = ('03064573', ['52/{0}'.format(issue) for issue in range(1, 5)] +\
                                      ['51/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['50/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['49/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['48/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['47/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['46/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['45/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['44/{0}'.format(issue) for issue in range(1, 7)] +\
                                      ['43/{0}'.format(issue) for issue in range(1, 7)]
                            )

JOURNALS['Elsevier_DKE'] = ('0169023X', range(101, 104) + ['100/part/PB', '100/part/PA', 99, 98, '96-97', 95, '94/part/PB', '94/part/PA'] +\
                                        range(83, 94) + ['81-82', '79-80', '76-78'] + range(72, 76) + ['71/1'] +\
                                        ['70/{0}'.format(issue) for issue in range(1, 13)] +\
                                        ['69/{0}'.format(issue) for issue in range(1, 13)] +\
                                        ['68/{0}'.format(issue) for issue in range(1, 13)] +\
                                        ['67/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['66/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['65/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['64/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['64/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['63/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['62/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['61/{0}'.format(issue) for issue in range(1, 4)] +\
                                        ['60/{0}'.format(issue) for issue in range(1, 4)]
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
