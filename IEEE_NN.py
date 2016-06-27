import os
import dill
from IEEE_general import get_abstracts

PUBLICATION_NUMER = 72
YEARS = range(1990, 2012)
FILE_CUT = 'IEEE_NN_abstracts'


def maybe_pickle_abstracts(force=False):
    set_filename = '{0}.dill'.format(FILE_CUT)
    if os.path.exists(set_filename) and not force:
        print '{0} already present - Loading dill.'.format(set_filename)
        abstracts = dill.load(open(set_filename, 'rb'))
    else:
        abstracts = get_abstracts(PUBLICATION_NUMER, YEARS)
        abstracts = [abstracts[v][k] for v in YEARS for k in abstracts[v]]
        try:
            print 'Dilling {0}'.format(set_filename)
            dill.dump(abstracts, open(set_filename, 'wb'))
        except Exception as e:
            print('Unable to save data to', set_filename, ':', e)
    return abstracts
