import pandas as pd
import json
from os import listdir
from os.path import isfile, join

#############
# UTILITIES #
#############

def load_config(where):
    """Loads the configuration file."""
    config = None
    with open(where, 'r', encoding='utf-8') as fp:
        config = json.loads(fp.read())
    return config

def fix_id(inlet):
    """
    Fix a id in number format to a valid string.
    """
    outlet = str(inlet)
    return ('0'*(11-len(outlet))) + outlet

def fix_payment_year(inlet):
    if len(inlet) != 4:
        raise SyntaxError
    return int(inlet)

def get_all_files(src):
    return [src + f for f in listdir(src) if isfile(join(src, f))]

def invert_map(m):
    return { v: k for k, v in m.items() }
