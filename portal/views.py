from datetime import datetime
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import json
from urllib.parse import urlparse

from minid_client import minid_client_api


from globus_portal_framework.search import views as gpf_search_views
from globus_portal_framework.search.models import Minid, MINID_BDBAG
from globus_portal_framework.search.views import get_search_query_params
from globus_portal_framework import post_search, load_globus_access_token

from globus_sdk import AuthClient, AccessTokenAuthorizer

from concierge.api import create_bag

from portal.models import Task, Workflow, Profile
from portal.workflow import (TASK_TASK_NAMES, TASK_GLOBUS_GENOMICS,
                             TASK_JUPYTERHUB, TASK_READY,
                             TASK_WAITING, TASK_RUNNING)
from portal.minid import add_minid


log = logging.getLogger(__name__)


def landing_page(request):
    context = {}
    return render(request, 'landing_page.html', context)


# def _set_minid_email(request, minid_email):
#     p = Profile.objects.filter(user=request.user).first()
#     key = request.POST.get('apikey')
#
#
#             messages.info(request, 'Your API key has been set.')
#         else:
#             messages.warning(request, 'Please enter your key.')
#
#     context = {'profile': p}
#     return render(request, 'profile.html', context)

@login_required
def bag_create(request):

    profile = Profile.objects.filter(user=request.user).first()
    if not profile:
        profile = Profile(user=request.user, minid_email=request.user.email)
        profile.save()

    ata = AccessTokenAuthorizer(
        load_globus_access_token(request.user, 'auth.globus.org'))
    ac = AuthClient(authorizer=ata)
    user_info = ac.oauth2_userinfo()
    request.user.email = user_info.get('email')
    request.user.save()

    identity_not_set = bool(ac.get_identities(
        request.user.email).data.get('identities'))

    context = {'profile': profile, 'identity_not_set': identity_not_set}

    if request.method == 'GET':

        query, filters, page = get_search_query_params(request)
        context['search'] = post_search(settings.SEARCH_INDEX, query, filters,
                                        request.user, limit=settings.BAG_LIMIT)
        # log.debug(context['search']['search_results'][0]['service'].keys())

        rfm_lists = [sr['service']['remote_file_manifest']
            for sr in context['search']['search_results']]
        flat_rfm_list = [item for sublist in rfm_lists for item in sublist]

        log.debug('{} result candidates for bag creation'.format(
            len(context['search']['search_results'])))
        request.session['search_query'] = urlparse(request.get_full_path()).query
        request.session['candidate_bags'] = flat_rfm_list
        request.session.modified = True
        # log.debug(context['search']['search_results'][0]['service'])
        return render(request, 'bag-create.html', context)
    if request.method == 'POST':
        bag_title = request.POST.get('bag-name')
        rfm_urls = request.POST.getlist('rfm-urls')
        can_bags = request.session.get('candidate_bags')
        minid_email = request.POST.get('minid-email')
        if minid_email:
            profile.minid_email = minid_email
            profile.save()
        log.debug(minid_email)
        if not can_bags or not rfm_urls or not bag_title:
            log.error('Error creating a bag. Bag name "{}", Session stored '
                      'manifests ({}), or user chosen bag urls ({}) were empty'
                      ''.format(bag_title, len(can_bags), len(rfm_urls)))
            messages.error(request, 'There was an error creating your bag, '
                                    'please contact your system administrator.'
                           )
            return redirect('bag-list')
        del request.session['candidate_bags']


        manifests = [b for b in can_bags if b['url'] in rfm_urls]
        # c_scope = '524361f2-e4a9-4bd0-a3a6-03e365cac8a9'
        # tok = load_globus_access_token(request.user, c_scope)
        tok = load_globus_access_token(request.user, 'auth.globus.org')
        try:
            log.debug('Creating minid with: {}'.format(profile.minid_email))
            # resp = create_bag('http://localhost:8080', manifests,
            #                    request.user.get_full_name(), request.user.email,
            #                    bag_title, tok)
            resp = create_bag('https://concierge.fair-research.org', manifests,
                               request.user.get_full_name(), request.user.email,
                               bag_title, tok)
            minid = Minid(id=resp['minid_id'], description=bag_title)
            minid.save()
            minid.users.add(request.user)
            messages.info(request, 'Your bag {} has been created with {} files.'
                                   ''.format(minid.id, len(manifests)))
            return redirect('bag-list')
        except Exception as e:
            log.error(e)
        messages.error(request, 'There was an error creating your bag, ensure your'
                                ' minid email has been set correctly.')
        log.debug(request.session.get('search_query'))
        return redirect(reverse('bag-create') + '?' + request.session.get('search_query'))


@login_required
def bag_add(request):
    if request.method == 'POST':
        minid = request.POST.get('minid')

        m = Minid.objects.filter(id=minid, users=request.user).first()
        if m:
            messages.info(request, 'Your minid has already been added.')
        else:
            new_min = add_minid(request.user, minid)
            messages.info(request, '"{}" has been added.'.format(
                new_min.description))
            log.debug('User {} added a new bag {}'.format(request.user,
                                                          new_min))
    return redirect('workflows')


@login_required
def bag_delete(request, minid):
    log.debug('User {} request to delete: {}'.format(request.user, minid))
    m = Minid.objects.filter(users=request.user, id=minid).first()
    if m:
        m.users.remove(request.user)
    else:
        messages.warning(request, '{} does not appear to be a valid minid.')
        log.warning('{} tried to delete {}'.format(request.user, minid))
    return redirect('workflows')


@login_required
def profile(request):
    p = Profile.objects.filter(user=request.user).first()
    if request.method == 'POST':
        key = request.POST.get('apikey')

        if key:
            if not p:
                p = Profile(user=request.user, globus_genomics_apikey=key)
            else:
                p.globus_genomics_apikey = key
            p.save()
            messages.info(request, 'Your API key has been set.')
        else:
            messages.warning(request, 'Please enter your key.')

    context = {'profile': p}
    return render(request, 'profile.html', context)


@login_required
def workflow_delete(request):
    if request.method == 'POST':
        r = Workflow.objects.filter(id=request.POST.get('id'),
                                    user=request.user).first()
        if r:
            r.delete()
            messages.info(request, 'Your workspace has been deleted')
    return redirect('workflows')


@login_required
def tasks(request):
    if request.method == 'POST':
        tid = request.POST.get('id')
        task = Task.objects.filter(id=tid, user=request.user).first()
        if not task:
            messages.warning(request, 'There was an error starting your task')
            log.error('Could not find task {} for user {}'.format(
                tid, request.user))
        else:
            log.debug('User {} started task {}'.format(request.user, task))
            task.task.start()
            messages.info(request, 'Started task: {}'.format(task.name))
    else:
        log.error(request.method)
    return redirect('workflows')


@login_required
def task_detail(request, task):
    task = Task.objects.filter(id=task, user=request.user).first()
    task_data = json.dumps(task.data, indent=4)
    return render(request, 'task-info.html', {'task': task,
                                              'task_data': task_data})

@login_required
def workflows(request):
    if request.method == 'POST':
        input = request.POST.get('input-bag')
        minid = None
        if input:
            minid = Minid.objects.filter(id=input, users=request.user).first()
        if not minid:
            messages.error(request, 'Could not find minid: {}'.format(minid))
        else:
            p = Profile.objects.filter(user=request.user).first()
            if not p:
                return redirect('profile')
            workflow = Workflow(user=request.user, name='Workflow with {}'
                                ''.format(minid.description))
            workflow.save()
            gg = Task(name='Globus Genomics',
                      workflow=workflow,
                      user=request.user,
                      category=TASK_GLOBUS_GENOMICS,
                      status=TASK_READY)
            gg.data = {'apikey': p.globus_genomics_apikey}
            gg.save()
            gg.input.add(minid)
            j = Task(name='Jupyterhub',
                     workflow=workflow,
                     user=request.user,
                     category=TASK_JUPYTERHUB,
                     status=TASK_WAITING)
            j.save()


    active_tasks = [{'id':t.id} for t in Task.objects.filter(user=request.user)]
    context = {'bags': Minid.objects.filter(users=request.user),
               'workflows': Workflow.objects.filter(user=request.user),
               'profile': Profile.objects.filter(user=request.user).first(),
               'active_tasks': json.dumps(active_tasks)
               }
    return render(request, 'workflows.html', context)
