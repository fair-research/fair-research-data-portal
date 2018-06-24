import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages

from globus_portal_framework.search import views as gpf_search_views
from globus_portal_framework.search.models import Minid

from concierge.api import create_bag

from portal.models import Workflow

from portal.workflow import WORKFLOW_TASK_NAMES


log = logging.getLogger(__name__)


def landing_page(request):
    context = {}
    return render(request, 'landing_page.html', context)


def bag_create(request):
    if request.method == 'GET':
        messages.warning(request, 'The index has not yet been rebuilt with '
                                  'manifests containing proper Globus URLs. '
                                  'Your bags will not be registered with '
                                  'Minid. Thanks for testing!')
        return gpf_search_views.bag_create(request)
    if request.method == 'POST':
        bag_title = request.POST.get('bag-name')
        rfm_urls = request.POST.getlist('rfm-urls')
        can_bags = request.session.get('candidate_bags')
        if not can_bags or not rfm_urls or not bag_title:
            log.error('Error creating a bag. Bag name "{}", Session stored '
                      'manifests ({}), or user chosen bag urls ({}) were empty'
                      ''.format(bag_title, len(can_bags), len(rfm_urls)))
            messages.error(request, 'There was an error creating your bag, '
                                    'please contact your system administrator.'
                           )
            return redirect('bag-list')
        del request.session['candidate_bags']

        can_bags_list = []
        for rfm in can_bags:
            if isinstance(rfm, list):
                can_bags_list.extend(rfm)
            elif isinstance(rfm, dict):
                can_bags_list.append(rfm)

        manifests = [b for b in can_bags_list if b['url'] in rfm_urls]

        # ENABLE THIS WHEN REMOTE FILE MANIFESTS CAN BE TRUSTED!
        # (Remember to also remove the messages.warning above)
        # tok = load_globus_access_token(request.user, 'auth.globus.org')
        # resp = create_bag('https://concierge.fair-research.org', manifests,
        #                    request.user.get_full_name(), request.user.email,
        #                    'testbag', tok)
        # minid = Minid(id=resp['minid_id'], user=request.user)

        minid = Minid(id=bag_title, user=request.user)
        minid.save()
        messages.info(request, 'Your bag {} has been created with {} files.'
                      ''.format(minid.id, len(manifests)))
        return redirect('bag-list.html')


def tasks(request):
    if request.method == 'POST':
        log.debug(request.POST)
        tid = request.POST.get('id')
        task = Workflow.objects.get(id=tid)
        if task.user != request.user:
            messages.warning(request, 'Naughtiness detected, please don\'t '
                                      'try that again.')
            log.warning('User edited task not theirs {} --> {}'
                        .format(request.user, task))
        task.task.start()
        messages.info('Started task')
        return redirect('workflows')


def workflows(request):
    context = {'bags': Minid.objects.filter(user=request.user),
               'workflows': Workflow.objects.filter(user=request.user),
               'workflow_categories':
                   [
                    {'value': val, 'name': name}
                    for val, name in WORKFLOW_TASK_NAMES.items()
                    ]
               }
    return render(request, 'workflows.html', context)
