import os.path, sys

APP_NAME = 'Log Monitor'
APP_VERSION = '1.00'    # remember to update wtclient.iss also
VENDOR_NAME = 'Invenco Group Ltd'

#CFG_FILENAME = APP_NAME + '.ini'

APP_DIR = sys.path[0]

if os.path.isfile(APP_DIR):  #py2exe/py2app
    APP_DIR = os.path.dirname(APP_DIR)

