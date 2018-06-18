
import logging
import django
from django.conf import settings

django.utils.autoreload._cached_filenames.append(settings.SEARCH_SCHEMA)

log = logging.getLogger(__name__)

NAMESPACE = 'http://gtex.globuscs.info/meta/GTEx_v7.xsd#'


# Configured in settings.py to be run by globus_portal_framework
def general_mapper(entry, schema):

    denamespaced = {k.replace(NAMESPACE, ''): v for k, v in entry[0].items()}

    fields = {k: {
                       'field_title': schema[k].get('field_title', k),
                       'data': v
                  } for k, v in denamespaced.items() if schema.get(k)}
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
    log.debug('Mapped Fields for {}: \n{}\n\t'.format('',
                                                      '\n\t'.join(info)))
    ignored = [f.replace(NAMESPACE, '[#]')
               for f in entry[0] if f not in fields.keys()]
    log.debug('Search fields ignored: {}'.format(', '.join(ignored)))
