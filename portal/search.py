
import logging
from django.conf import settings
from globus_portal_framework import default_search_mapper


log = logging.getLogger(__name__)


# Configured in settings.py to be run by globus_portal_framework
def general_mapper(entry, schema):
    fields = default_search_mapper(entry, schema)
    fields['metadata'] = entry[0].get('field_metadata')
    fields['remote_file_manifest'] = entry[0].get('remote_file_manifest')
    fields['globus_group'] = entry[0].get('globus_group')

    if settings.DEBUG:
        debug_fields(entry, fields)

    return fields


def debug_fields(entry, fields):
    info = []
    for f, d in fields.items():
        field_info = f
        if isinstance(d, dict):
            if isinstance(d.get('data'), list):
                field_info += '.data.[]'
                if len(d.get('data')) > 0:
                    field_info += '.(%s)' % ','.join(d['data'][0].keys())
            if isinstance(d.get('data'), dict):
                field_info += '.data.(%s)' % ','.join(d['data'].keys())
        info.append(field_info)
    log.debug('Mapped Fields for {}: \n{}'.format(fields['title']['value'],
                                                  '\n\t'.join(info)))
    ignored = [f for f in entry[0]['perfdata'] if f not in fields.keys()]
    log.debug('Search fields ignored: {}'.format(', '.join(ignored)))
