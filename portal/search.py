
import logging
import django
from django.conf import settings

# @HACK: Use this only for debugging. Remove when we move to models.
if settings.DEBUG:
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

    #fields['title'] = {'field_title': 'Sample ID', 'value': fields['SAMPID']['data']}
    fields['minid'] = entry[0].get('Argon_GUID')

    # if settings.DEBUG:
    #     debug_fields(entry, fields)
    #
    # log.debug(fields.keys())
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
