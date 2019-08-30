import sys
from collections import Counter
import itertools
from operator import add
import IEEE_general
import elsevier
import dimva, ccs, snp,ndss, esorics
from general import get_keywords_of_single_abstract_RAKE, get_keywords_of_single_abstract_grams


METHOD = get_keywords_of_single_abstract_RAKE


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


DETAILS = dict()
# Journals

# Conferences - h5-index 
# 1 is not found
DETAILS['dimva'] = ('Conference of Intrusions and Malware & Vulnerability Assessment', 1)
DETAILS['snp'] = ('IEEE Symposium on Security and privacy', 32)
DETAILS['ccs'] = ('ACM Conference on Computer and Communications Security', 82)
DETAILS['ndss'] = ('Usenix Network and Distributed System Security Symposium', 65)
DETAILS['esorics'] = ('European Symposium On Research In Computer Security', 1)



def get_content(func, argument=None):
    if argument:
        return [METHOD(abs) for abs in func(argument)]
    else:
        return [METHOD(abs) for abs in func()]


def main():
    # TODO: better cleaning: get rid of \n, math, non-ASCII, some HTML, etc.
    source = dict()

    source['dimva'] = get_content(dimva.maybe_pickle_abstracts)
    source['ccs'] = get_content(ccs.maybe_pickle_abstracts)
    source['ndss'] = get_content(ndss.maybe_pickle_abstracts)
    source['snp'] = get_content(snp.maybe_pickle_abstracts)
    source['esorics'] = get_content(esorics.maybe_pickle_abstracts)


    total = 0
    for s in source.keys():
        count = len(source[s])
        total += count
        print 'Number of {0} abstracts: {1}'.format(DETAILS[s][0], count)

    print 'Total = {0}'.format(total)

    # Weight sources by impact factor
    all_impacts = [d[1] for d in DETAILS.values() if d[1] != None]
    mean_impact = 1. * sum(all_impacts) / len(all_impacts)
    counters = dict()
    for s in source.keys():
        counters[s] = Counter(list(itertools.chain(*source[s])))
        impact = DETAILS[s][1]
        if not impact:
            impact = mean_impact
        for w in counters[s]:
            counters[s][w] *= impact

    for k in reduce(add, counters.values(), Counter()).most_common(100):
        print k

if __name__ == '__main__':
    main()
