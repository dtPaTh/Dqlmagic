__version__='1.1.0'

from .dqlmagic import DQLmagic

def load_ipython_extension(ipython):
    ipython.register_magics(DQLmagic)