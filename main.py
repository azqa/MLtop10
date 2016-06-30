import sys
from collections import Counter
import itertools
import jmlr
import jmlr_proc
import springer_ai
import IEEE_general
#import elsevier
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
NAME['IEEE_KDA'] = 'IEEE Transactions on Knowledge and Data Engineering'
NAME['IEEE_MI'] = 'IEEE Transactions on Medical Imaging'
NAME['IEEE_EC'] = 'IEEE Transactions on Evolutionary Computation'
NAME['IEEE_CIM'] = 'IEEE Computational Intelligence Magazine'
NAME['IEEE_ASLP'] = 'IEEE Transactions on Audio, Speech, and Language Processing'
NAME['IEEE_IS'] = 'IEEE Intelligent Systems'
NAME['IEEE_SMCB'] = 'IEEE Transactions on Systems, Man, and Cybernetics, Part B (Cybernetics)'
NAME['IEEE_FS'] = 'IEEE Transactions on Fuzzy Systems'
NAME['IEEE_CVPR'] = 'Conference on Computer Vision and Pattern Recognition'
NAME['IEEE_ICCV'] = 'International Conference on Computer Vision'
NAME['Elsevier_KBS'] = 'Knowledge-Based Systems'
NAME['Elsevier_NN'] = 'Neural Networks'
NAME['Elsevier_Neuro'] = 'Neurocomputing'
NAME['Elsevier_PR'] = 'Pattern Recognition'
NAME['Elsevier_AI'] = 'Artificial Intelligence'
NAME['Elsevier_CSL'] = 'Computer Speech and Language'
NAME['Elsevier_PRL'] = 'Pattern Recognition Letters'
NAME['Elsevier_CSDA'] = 'Computational Statistics & Data Analysis'
NAME['Elsevier_IPM'] = 'Information Processing & Management'
NAME['Elsevier_IPM'] = 'Data & Knowledge Engineering'
NAME['Elsevier_CSR'] = 'Cognitive Systems Research'


def get_content(func, argument=None):
    if argument:
        return [get_keywords_of_single_abstract(abs) for abs in func(argument)]
    else:
        return [get_keywords_of_single_abstract(abs) for abs in func()]


def main():
    # TODO: better cleaning: get rid of \n, math, non-ASCII, some HTML, etc.
    source = dict()
    source['jmlr'] = get_content(jmlr.maybe_pickle_abstracts)
    source['jmlr_proc'] = get_content(jmlr_proc.maybe_pickle_abstracts)
    source['springer_ai'] = get_content(springer_ai.maybe_pickle_springer_ai_raw_abstracts)
    source['IEEE_TPAMI'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_TPAMI')
    source['IEEE_NN'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN')
    source['IEEE_NN_LS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN_LS')
    source['IEEE_KDA'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_KDA')
    source['IEEE_MI'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_MI')
    source['IEEE_EC'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_EC')
    source['IEEE_CIM'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_CIM')
    source['IEEE_ASLP'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_ASLP')
    source['IEEE_IS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_IS')
    source['IEEE_SMCB'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_SMCB')
    source['IEEE_FS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_FS')
    source['IEEE_CVPR'] = get_content(IEEE_general.maybe_pickle_proceeding_abstracts, 'IEEE_CVPR')
    source['IEEE_ICCV'] = get_content(IEEE_general.maybe_pickle_proceeding_abstracts, 'IEEE_ICCV')
    #source['Elsevier_PR'] = get_content(elsevier.maybe_pickle_proceeding_abstracts, 'Elsevier_PR')

    total = 0
    for s in source.keys():
        count = len(source[s])
        total += count
        print 'Number of {0} abstracts: {1}'.format(NAME[s], count)

    print 'Total = {0}'.format(total)

    keywords = list(itertools.chain(*[list(itertools.chain(*source[s])) for s in source]))
    all_keywords = Counter(keywords)
    for k in Counter(all_keywords).most_common(200):
        print k

if __name__ == '__main__':
    main()
