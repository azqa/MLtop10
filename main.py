import sys
from collections import Counter
import itertools
import jmlr
import jmlr_proc
import springer_ai
import IEEE_general
from general import get_keywords_of_single_abstract


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


NAME = dict()
NAME['jmlr'] = 'Journal of Machine Learning Research'
NAME['jmlr_proc'] = 'Journal of Machine Learning Research Conference Proceedings'
NAME['springer_ai'] = 'Springer Machine Learning'
NAME['IEEE_TPAMI'] = 'IEEE Transactions on Pattern Analysis and Machine Intelligence'
NAME['IEEE_NN'] = 'IEEE Transactions on Neural Networks'
NAME['IEEE_NN_LS'] = 'IEEE Transactions on Neural Networks and Learning Systems'


def get_content(func, argument=None):
    if argument:
        return [get_keywords_of_single_abstract(abs) for abs in func(argument)]
    else:
        return [get_keywords_of_single_abstract(abs) for abs in func()]


def main():
    # TODO: better cleaning: get rid of \n, math, non-ASCII
    source = dict()
    source['jmlr'] = get_content(jmlr.maybe_pickle_abstracts)
    source['jmlr_proc'] = get_content(jmlr_proc.maybe_pickle_abstracts)
    source['springer_ai'] = get_content(springer_ai.maybe_pickle_springer_ai_raw_abstracts)
    source['IEEE_TPAMI'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_TPAMI')
    source['IEEE_NN'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN')
    source['IEEE_NN_LS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN_LS')

    total = 0
    for s in source.keys():
        count = len(source[s])
        total += count
        print 'Number of {0} abstracts: {1}'.format(NAME[s], count)

    print 'Total = {0}'.format(total)

    keywords = list(itertools.chain(*[list(itertools.chain(*source[s])) for s in source]))
    all_keywords = Counter(keywords)
    for k in Counter(all_keywords).most_common(30):
        print k

if __name__ == '__main__':
    main()
