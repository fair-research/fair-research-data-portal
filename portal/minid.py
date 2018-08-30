import requests
import logging
from minid_client import minid_client_api
from globus_sdk import AccessTokenAuthorizer
from identifier_client.identifier_api import IdentifierClient

from globus_portal_framework.search.models import Minid, MINID_BDBAG
from globus_portal_framework import load_globus_access_token

log = logging.getLogger(__name__)

MINID_SERVER = 'http://minid.bd2k.org/minid'
IDENTIFIER_SCOPE = ('https://auth.globus.org/scopes/'
                    'identifiers.globus.org/create_update')
IDENTIFIERS_URL = 'https://identifiers.globus.org/'

def add_minid(user, minid):
    old_minid = Minid.objects.filter(id=minid).first()
    if old_minid:
        old_minid.users.add(user)
        log.debug('Adding existing user to minid: {}'.format(old_minid))
        return old_minid

    r = requests.get('{}{}'.format(IDENTIFIERS_URL, minid))
    if r.status_code == 404:
        return None
    minid_data = r.json()
    log.debug(r.text)
    print(minid_data)
    t = minid_data['metadata'].get('title', minid_data['identifier'])
    new_minid = Minid(id=minid, category=MINID_BDBAG, description=t)
    new_minid.save()
    new_minid.users.add(user)
    return new_minid