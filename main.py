import sys
from collections import Counter
import itertools
from operator import add
import jmlr
import jmlr_proc
import springer_ai
import IEEE_general
import elsevier
import acm
import nips
from general import get_keywords_of_single_abstract


# Avoids some strange unicode error...
# <http://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte>
reload(sys)
sys.setdefaultencoding('utf8')


DETAILS = dict()
DETAILS['jmlr'] = ('Journal of Machine Learning Research', 2.473)
DETAILS['jmlr_proc'] = ('Journal of Machine Learning Research Conference Proceedings', (9.1862 + 4.2905 + 2.473) / 3) # ICML + COLT + JMLR
DETAILS['springer_ai'] = ('Springer Machine Learning', 1.889)
DETAILS['IEEE_FS'] = ('IEEE Transactions on Fuzzy Systems', 8.746)
DETAILS['IEEE_SMCB'] = ('IEEE Transactions on Systems, Man, and Cybernetics, Part B (Cybernetics)', 6.220)
DETAILS['IEEE_TPAMI'] = ('IEEE Transactions on Pattern Analysis and Machine Intelligence', 5.781)
DETAILS['IEEE_NN_LS'] = ('IEEE Transactions on Neural Networks and Learning Systems', 4.291)
DETAILS['IEEE_EC'] = ('IEEE Transactions on Evolutionary Computation', 3.654)
DETAILS['IEEE_NN'] = ('IEEE Transactions on Neural Networks', 2.633)
DETAILS['IEEE_CIM'] = ('IEEE Computational Intelligence Magazine', 2.571)
DETAILS['IEEE_ASLP'] = ('IEEE Transactions on Audio, Speech and Language Processing', 2.475)
DETAILS['IEEE_MI'] = ('IEEE Transactions on Medical Imaging', 3.390)
DETAILS['IEEE_IS'] = ('IEEE Intelligent Systems', 2.340)
DETAILS['IEEE_KDA'] = ('IEEE Transactions on Knowledge and Data Engineering', 2.067)
DETAILS['IEEE_CVPR'] = ('Conference on Computer Vision and Pattern Recognition', 6.6133)
DETAILS['IEEE_ICCV'] = ('International Conference on Computer Vision', 11.9754)
DETAILS['Elsevier_AI'] = ('Artificial Intelligence', 3.371)
DETAILS['Elsevier_PR'] = ('Pattern Recognition', 3.096)
DETAILS['Elsevier_KBS'] = ('Knowledge-Based Systems', 2.947)
DETAILS['Elsevier_NN'] = ('Neural Networks', 2.708)
DETAILS['Elsevier_Neuro'] = ('Neurocomputing', 2.083)
DETAILS['Elsevier_CSL'] = ('Computer Speech and Language', 1.753)
DETAILS['Elsevier_PRL'] = ('Pattern Recognition Letters', 1.551)
DETAILS['Elsevier_CSDA'] = ('Computational Statistics & Data Analysis', 1.400)
DETAILS['Elsevier_IPM'] = ('Information Processing & Management', 1.265)
DETAILS['Elsevier_DKE'] = ('Data & Knowledge Engineering', 1.115)
DETAILS['ACM_JACM'] = ('Journal of the ACM', 1.39)
DETAILS['nips'] = ('Advances in Neural Information Processing Systems', 8.5437)


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
    source['IEEE_FS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_FS')
    source['IEEE_SMCB'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_SMCB')
    source['IEEE_TPAMI'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_TPAMI')
    source['IEEE_NN_LS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN_LS')
    source['IEEE_EC'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_EC')
    source['IEEE_NN'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_NN')
    source['IEEE_CIM'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_CIM')
    source['IEEE_ASLP'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_ASLP')
    source['IEEE_MI'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_MI')
    source['IEEE_IS'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_IS')
    source['IEEE_KDA'] = get_content(IEEE_general.maybe_pickle_abstracts, 'IEEE_KDA')
    source['IEEE_CVPR'] = get_content(IEEE_general.maybe_pickle_proceeding_abstracts, 'IEEE_CVPR')
    source['IEEE_ICCV'] = get_content(IEEE_general.maybe_pickle_proceeding_abstracts, 'IEEE_ICCV')
    source['Elsevier_AI'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_AI')
    source['Elsevier_PR'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_PR')
    source['Elsevier_KBS'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_KBS')
    source['Elsevier_NN'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_NN')
    source['Elsevier_Neuro'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_Neuro')
    source['Elsevier_CSL'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_CSL')
    source['Elsevier_PRL'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_PRL')
    source['Elsevier_CSDA'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_CSDA')
    source['Elsevier_IPM'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_IPM')
    source['Elsevier_DKE'] = get_content(elsevier.maybe_pickle_abstracts, 'Elsevier_DKE')
    source['ACM_JACM'] = get_content(acm.maybe_pickle_abstracts)
    source['nips'] = get_content(nips.maybe_pickle_abstracts)

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

    for k in reduce(add, counters.values(), Counter()).most_common(200):
        print k

if __name__ == '__main__':
    main()
