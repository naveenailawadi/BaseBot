from licensing.methods import Helpers
from datetime import datetime as dt, timedelta
import time
import jwt
import sys
import os


# make an auth filename
AUTH_FILE = '.license'
MACHINE_ID = Helpers.GetMachineCode()

# use the dev id as an encryption tool
DEV_ID = '5a57d2080dbc5b1803249fcfc47c6b336b5408aa5b2eb8b33d0a69df3d94afa0'

# set issue time
TODAY = dt.now()
DAY_ADD_DEFAULT = 36500  # 100 years
ISSUE_END = 7


# check if there is a verification file
files = os.listdir()


# make a function to issue the certificate
def issue_certificate(expiry_days=DAY_ADD_DEFAULT):
    expiry = TODAY + timedelta(expiry_days)
    issue_end = TODAY + timedelta(ISSUE_END)
    data = {
        'id': MACHINE_ID,
        'expiry': expiry.timestamp(),
        'issue_end': issue_end.timestamp()
    }
    # issue a certificate (just the machine code ID)
    token = jwt.encode(data, DEV_ID)
    with open(AUTH_FILE, 'wb') as outfile:
        outfile.write(token)


# make a function to remove the directory
def punish():
    try:
        os.remove('core/bots.py')
    except FileNotFoundError:
        pass
    print('Failed licensing check.')


# autoissue for developer
if MACHINE_ID == DEV_ID:
    issue_certificate()
elif not (AUTH_FILE in files):
    print('Please obtain a license from the developer.')
    sys.exit()


# open the verification dotfile
with open(AUTH_FILE, 'r') as infile:
    data = jwt.decode(infile.read(), DEV_ID)
    this_id = data['id']
    expiry = data['expiry']
    issue_end = data['issue_end']


if MACHINE_ID == DEV_ID:
    # protect yourself
    pass
elif expiry <= time.time():
    punish()
    print('This license is expired')
elif this_id == DEV_ID:
    # check if a certificate can be issued
    if issue_end >= time.time():
        # don't change the expiry days
        expiry_date = dt.fromtimestamp(expiry)
        expiry_days = (expiry_date - TODAY).days
        issue_certificate(expiry_days)
    else:
        punish()
        print('The issue period has ended.')

elif this_id != MACHINE_ID:
    punish()
    print('This device does not have the appropriate license')

# allow setting a custom expiry (only for the developer)
if (__name__ == '__main__') and (MACHINE_ID == DEV_ID):
    expiry_days = int(sys.argv[1].strip())

    issue_certificate(expiry_days)
