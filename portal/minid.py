from minid_client import minid_client_api

from globus_portal_framework.search.models import Minid, MINID_BDBAG

MINID_SERVER = 'http://minid.bd2k.org/minid'

def add_minid(user, minid):
    r = minid_client_api.get_entities(MINID_SERVER, minid, False)
    if not r.get(minid):
        raise ValueError('Could not find Minid: {}'.format(minid))

    t = r[minid].get('titles')
    if t:
        t = t[0]['title']
    else:
        t = r.get('creator')
    new_minid = Minid(id=minid, category=MINID_BDBAG, description=t)
    new_minid.save()
    new_minid.users.add(user)
    return new_minid